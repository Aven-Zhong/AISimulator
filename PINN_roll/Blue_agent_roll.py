import math
import numpy as np
from const.Obs import Observation, ObjState
import sys
from PINN_roll.PID import PID
from PINN_roll.const import *


# 蓝方，训练滚转角控制
class Agent_1v1_Blue_Roll:
    def __init__(self, id):
        self.id = id
        self.flightData = FlightData()
        # 滚转角
        self.rollCtrl_roll_u = PID()
        self.rollCtrl_roll_u.setParam(3, 0., 0., 1)
        self.rollCtrl_roll_u.setLimits(-9, 9)

        self.rollCtrl_u_ctrl = PID()
        self.rollCtrl_u_ctrl.setParam(-1, 0., 0., 1)
        self.rollCtrl_u_ctrl.setLimits(-1, 1)

        self.start_roll = 0
        self.target_roll = 60


    def reset(self, pidParams: list = None):
        if pidParams is None or len(pidParams) != 6:
            print("Error: No PID parameters provided.")
            return

        self.rollCtrl_roll_u.setParam(pidParams[0], pidParams[1], pidParams[2], 1)
        self.rollCtrl_u_ctrl.setParam(pidParams[3], pidParams[4], pidParams[5], 1)
        print("blue reset")

    def step(self, obs: Observation):
        if not obs.enemy_aircraft:  # 检查敌机列表是否为空
            print("Warning: No enemy aircraft data available.")
            obs.enemy_aircraft = np.zeros(24)
        self.updateFlightData(obs.self_aircraft[0])

        roll_exp = self.target_roll
        # print("roll_exp:", roll_exp)
        ctrl = CtrlInfo()

        self.rollCtrl_roll_u.setPid(roll_exp / 180 * math.pi, self.flightData.phi)
        uc = self.rollCtrl_roll_u.update()

        self.rollCtrl_u_ctrl.setPid(uc, self.flightData.omega[0])
        ctrl.dwYpos = self.rollCtrl_u_ctrl.update()


        action = Action(0, ctrl.dwYpos, 0.5, 0)

        return action

    def updateFlightData(self, self_aircraft: ObjState):
        flightData = self.toFlightData(self_aircraft)
        self.flightData = flightData

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

