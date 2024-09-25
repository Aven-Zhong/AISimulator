"""
定义姿态控制、速度控制、高度控制、
"""
import math
import numpy as np
from train.blue_agent.PID_ctrl.PID_baseControl import FlightData, CtrlInfo
from train.blue_agent.PID_ctrl.PID_baseControl import CtrlInfo
from train.blue_agent.PID_ctrl.PID_definition import PID

class AttitudeController:
    def __init__(self, target_attitude, k, lambda_control, eta, current_attitude=0):
        self.target_attitude = target_attitude
        self.k = k  # 控制增益
        self.lambda_control = lambda_control  # 滑块控制参数
        self.eta = eta  # 自适应控制增益
        self.current_attitude = current_attitude  # 初始姿态
        self.error_integral = 0  # 积分项，用于自适应控制

    def control_step(self, delta_t=0.01):
        error = self.target_attitude - self.current_attitude
        self.error_integral += error * delta_t
        adaptive_term = self.eta * self.error_integral
        control_signal = self.k * error - self.lambda_control * np.sign(error) + adaptive_term
        self.current_attitude +=control_signal *delta_t
        return self.current_attitude


class SpeedController:
    def __init__(self, target_speed, k, lambda_control, eta, current_speed=0):
        self.target_speed = target_speed
        self.k = k
        self.lambda_control = lambda_control
        self.eta = eta
        self.current_speed = current_speed
        self.error_integral = 0

    def control_step(self, delta_t=0.01):
        error = self.target_speed - self.current_speed
        self.error_integral += error * delta_t
        adaptive_term = self.eta * self.error_integral
        control_signal = self.k * error - self.lambda_control * np.sign(error) + adaptive_term
        self.current_speed += control_signal * delta_t
        return self.current_speed


# 高度控制
class AltitudeController:
    def __init__(self, k=0.5, lambda_control=0.3, eta=0.1):
        self.flightData = FlightData()

        self.k = k  # 增益控制
        self.lambda_control = lambda_control  # 滑模控制参数
        self.eta = eta  # 自适应控制增益
        self.error_integral = 0  # 积分项，用于自适应控制

        self.error = 0
        self.derivative_error = 0
        self.previous_error = 0
        self.integral_error = 0
        self.control_signal = 0
        self.adaptive_law = 0.1  # 自适应律的初始值

    def climb(self, alti_exp, spd_exp):

        alti_cur, spd_cur = self.flightData.altitude, self.flightData.Vc

        alti_limit = 50
        tmp_alti = alti_exp - alti_cur
        if tmp_alti > alti_limit:
            alti_exp = alti_cur + alti_limit
        if tmp_alti < -alti_limit:
            alti_exp = alti_cur - alti_limit

        spd_limit = 5
        tmp_spd = spd_exp - spd_cur
        if tmp_spd > spd_limit:
            spd_exp = spd_cur + spd_limit
        if tmp_spd < -spd_limit:
            spd_exp = spd_cur - spd_limit

        # 高度控制 只对俯仰角和速度控制 其他视为外部扰动

        ctrl = self.altiCtrl_(alti_exp, spd_exp)

        # print("PID里的当前高度：", self.flightData.altitude)
        # print("期望高度：", alti_exp)

        return ctrl


    def altiCtrl_(self, alti_exp, spd_exp):
        ctrl = CtrlInfo()

        # 误差计算
        alti_cur = self.flightData.altitude
        self.error = alti_exp - alti_cur
        self.derivative_error = self.error - self.previous_error
        self.integral_error += self.error * self.lambda_control  # 积分项现在也考虑lambda_control

        # 滑模面设计，使用论文中的参数
        sliding_surface = self.k * self.error + 0.1 * self.integral_error + 0.05 * self.derivative_error

        # 自适应律更新，基于论文中的eta参数
        self.adaptive_law = max(0.01, self.eta + 0.02 * abs(sliding_surface))

        # 控制律，包含非线性项和自适应项，使用论文中的lambda_control调整非线性项
        self.control_signal = self.k * sliding_surface + self.adaptive_law * np.sign(sliding_surface)

        # 更新前一个误差值
        self.previous_error = self.error

        # delta_t = 1
        # alti_cur = self.flightData.altitude
        # error = alti_exp - alti_cur
        # self.error_integral += error * delta_t
        #
        # adaptive_term = self.eta * self.error_integral
        # control_signal = self.k * error - self.lambda_control * np.sign(error) + adaptive_term

        u_m_fPitch = alti_cur + self.control_signal

        ctrl.dwXpos = self.thetaCtrl(u_m_fPitch).dwXpos
        ctrl.dwZpos = self.acceSpdCtrl(spd_exp, u_m_fPitch).dwZpos
        return ctrl

    def thetaCtrl(self, theta_exp):
        ctrl = CtrlInfo()

        m_fPitchCtrl_m_fPitch_u = PID(1, 0, 1, 1)
        m_fPitchCtrl_m_fPitch_u.setLimits(-20, 20)
        m_fPitchCtrl_m_fPitch_u.setPid(theta_exp, self.flightData.theta)
        uc = m_fPitchCtrl_m_fPitch_u.update()

        m_fPitchCtrl_u_ctrl = PID(-5, 0, 0, 1)
        m_fPitchCtrl_u_ctrl.setLimits(-1, 1)
        m_fPitchCtrl_u_ctrl.setPid(uc, self.flightData.omega[1])
        ctrl.dwXpos = m_fPitchCtrl_u_ctrl.update()

        return ctrl

    def acceSpdCtrl(self, spd_exp, theta_exp):
        # 油门控制速度
        ctrl = CtrlInfo()
        acceSpdCtrl_u_ctrl = PID(0.5, 0.00001, 0, 1)
        acceSpdCtrl_u_ctrl.setLimits(0, 1)
        acceSpdCtrl_u_ctrl.setPid(spd_exp, self.flightData.Vc)
        ctrl.dwZpos = acceSpdCtrl_u_ctrl.update()
        ctrl.dwXpos = self.thetaCtrl(theta_exp).dwXpos
        return ctrl


    def updateFlightData(self, self_aircraft):
        flightdata = self.toFlightData(self_aircraft)
        self.flightData = flightdata

    def toFlightData(self, self_aircraft):  # 需要修改
        flightdata = FlightData()

        flightdata.VE[0] = self_aircraft.v_n
        flightdata.VE[1] = self_aircraft.v_e
        flightdata.VE[2] = self_aircraft.v_d

        flightdata.longitude = self_aircraft.lon  # 经度(°)
        flightdata.latitude = self_aircraft.lat  # 纬度(°)
        flightdata.altitude = self_aircraft.alt  # 高度(m)

        flightdata.psi = self_aircraft.heading
        flightdata.theta = self_aircraft.pitch
        flightdata.phi = self_aircraft.roll

        flightdata.alpha = self_aircraft.alpha
        flightdata.beta = self_aircraft.beta

        p = self_aircraft.p
        q = self_aircraft.q
        r = self_aircraft.r
        flightdata.omega[0] = p + q * math.sin(flightdata.phi) * math.tan(
            flightdata.theta) + r * math.cos(flightdata.phi) * math.tan(flightdata.theta)
        flightdata.omega[1] = q * math.cos(flightdata.phi) - r * math.sin(flightdata.phi)
        flightdata.omega[2] = q * math.sin(flightdata.phi) / math.cos(flightdata.theta) + r * math.cos(
            flightdata.phi) / math.cos(flightdata.theta)
        flightdata.Vc = math.sqrt(
            flightdata.VE[0] * flightdata.VE[0] + flightdata.VE[1] * flightdata.VE[1] + flightdata.VE[
                2] * flightdata.VE[2])
        return flightdata
