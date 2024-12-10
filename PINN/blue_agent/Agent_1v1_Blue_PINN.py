import numpy as np

from const.Obs import *
from PINN.blue_agent.HighAgent_PINN import HighAgent_PINN

# 输出控制->操作杆控制
class Agent_1v1_Blue_PINN:
    def __init__(self, id):
        self.id = id
        self.blue_agent = HighAgent_PINN()

    def reset(self):
        # 重置agent相关参数
        print("blue agent reset ...")

    def resetPIDParams(self, pid_params: list):
        Kp = pid_params[0]
        Ki = pid_params[1]
        Kd = pid_params[2]
        self.blue_agent.lowAgent.autoDriver.altiCtrl_alt_u.setParam(Kp, Ki, Kd, 1)

    # 调用step函数，返回控制指令
    def step(self, obs: Observation):
        if not obs.enemy_aircraft:  # 检查敌机列表是否为空
            print("Warning: No enemy aircraft data available.")
            obs.enemy_aircraft = np.zeros(24)

        m_pidtrl = self.blue_agent.flyStraight(obs.self_aircraft[0], obs.enemy_aircraft[0])
        action = Action(m_pidtrl.dwXpos, m_pidtrl.dwYpos, m_pidtrl.dwZpos, m_pidtrl.dwRpos)

        return action
