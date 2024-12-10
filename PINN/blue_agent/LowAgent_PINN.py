"""
左转;右转;掉头;升高,降低,加速,减速;分段爬高加速
"""
from PINN.blue_agent.PID_ctrl.PID_baseControl import AutoDriver, FlightData
from const.Obs import ObjState
import math


class st_HotasinfoOrder:
    def __init__(self):
        self.strObjID = ""
        self.dwXpos = ""
        self.dwYpos = ""
        self.dwZpos = ""
        self.dwRpos = ""


class LowAgent_PINN:
    def __init__(self):
        self.autoDriver = AutoDriver()  # # 掌握多种基础控制PID的类autoDriver
        # self.autoDriver.flightData中存着当前飞机信息
        self.cur_time = 0
        self.aircraft_roll_max = 1.5

    def toFlightData(self, self_aircraft: ObjState):
        flightData = FlightData()

        flightData.VE[0] = self_aircraft.v_n  # 北向速度(m/s)
        flightData.VE[1] = self_aircraft.v_e  # 东向速度(m/s)
        flightData.VE[2] = self_aircraft.v_d  # 地向速度(m/s)

        flightData.longitude = self_aircraft.lon  # 经度(°)
        flightData.latitude = self_aircraft.lat  # 纬度(°)
        flightData.altitude = self_aircraft.alt  # 高度(m)

        flightData.psi = self_aircraft.heading  # 航向角(°)
        flightData.theta = self_aircraft.pitch  # 俯仰角(°)
        flightData.phi = self_aircraft.roll  # 滚转角(°)

        flightData.alpha = self_aircraft.alpha  # 迎角(rad)
        flightData.beta = self_aircraft.beta  # 侧滑角(rad)

        p = self_aircraft.p  # 滚转角速度(rad/s)
        q = self_aircraft.q  # 俯仰角速度(rad/s)
        r = self_aircraft.r  # 侧滑角速度(rad/s)

        flightData.omega[0] = p + q * math.sin(flightData.phi) * math.tan(
            flightData.theta) + r * math.cos(flightData.phi) * math.tan(flightData.theta)
        flightData.omega[1] = q * math.cos(flightData.phi) - r * math.sin(flightData.phi)
        flightData.omega[2] = q * math.sin(flightData.phi) / math.cos(flightData.theta) + r * math.cos(
            flightData.phi) / math.cos(flightData.theta)
        flightData.Vc = math.sqrt(
            flightData.VE[0] * flightData.VE[0] + flightData.VE[1] * flightData.VE[1] + flightData.VE[
                2] * flightData.VE[2])
        return flightData

    def updateFlightData(self, self_aircraft: ObjState):
        flightData = self.toFlightData(self_aircraft)
        self.autoDriver.update_output(flightData)

    # 左转
    def turnLeft(self, roll_exp):
        roll_exp = roll_exp * 1.5
        roll_exp = min(float(self.aircraft_roll_max), roll_exp)
        roll_exp = -max(0.5, roll_exp)

        m_rollCtrl = self.autoDriver.rollCtrl(roll_exp)
        return  m_rollCtrl

    # 右转
    def turnRight(self, roll_exp):
        roll_exp = roll_exp * 1.5
        roll_exp = min(float(self.aircraft_roll_max), roll_exp)
        roll_exp = max(0.5, roll_exp)
        m_rollCtrl = self.autoDriver.rollCtrl(roll_exp)
        return m_rollCtrl

    # #掉头
    def turnHeading(self):
        roll_exp = 1
        m_rollCtrl = self.autoDriver.rollCtrl(roll_exp)
        return m_rollCtrl

    # altiCtrl(self, alti_exp, spd_exp):
    # 升高,降低,加速,减速
    def alti_spd(self, alti_exp, spd_exp):
        m_altiCtrl = self.autoDriver.altiCtrl(alti_exp, spd_exp)
        return m_altiCtrl

    # 分段爬高加速
    def stage_climb(self, alti_exp, spd_exp, alti_cur, spd_cur):
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

        m_altiCtrl = self.autoDriver.altiCtrl(alti_exp, spd_exp)
        return m_altiCtrl

    def transfer_angel(self, x, y):  # 注意.输入是角度制
        angle_rad = math.atan2(y, x)
        angle_deg = math.degrees(angle_rad)

        # 这里的变换是为了和平台的本机朝向的变化范围相适应
        if x >= 0 and y >= 0:  # 第一象限
            angle_deg = 90 - angle_deg
        elif x < 0 and y > 0:  # 第二象限
            angle_deg = 360 + 90 - angle_deg
        elif x < 0 and y == 0:
            angle_deg = 270
        elif x < 0 and y < 0:  # 第三象限
            angle_deg = 90 - angle_deg
        elif x >= 0 and y < 0:  # 第四象限
            angle_deg = 90 - angle_deg

        return angle_deg