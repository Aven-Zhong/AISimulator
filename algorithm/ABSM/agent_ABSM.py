import numpy as np
from const.Obs import *
from algorithm.ABSM.highAgent_ABSM import HighAgent_ABSM


# 蓝方 使用自适应后退滑模控制策略
class Agent_1V1_Blue_asm_altitude:
    def __init__(self, id):
        self.id = id
        self.blue_agent = HighAgent_ABSM()
        # AltitudeController(climb_altitude=100, k=0.05, lambda_control=0.01, eta=0.001)

    def reset(self):
        # 重置agent相关参数[to do]
        print("blue agent reset ...")

    # 调用step函数,返回控制指令
    def step(self, obs: Observation):
        if not obs.enemy_aircraft:  # 检查敌机列表是否为空
            print("Warning: No enemy aircraft data available.")
            obs.enemy_aircraft = np.zeros(24)
        # current_altitude = obs.self_aircraft.alt
        m_ctrl = self.blue_agent.action_climb(obs.self_aircraft[0], obs.enemy_aircraft[0])
        action = Action(m_ctrl.dwXpos, m_ctrl.dwYpos, m_ctrl.dwZpos, m_ctrl.dwRpos)

        # m_pidtrl = self.blue_agent.action_feizhixian(obs.self_aircraft[0], obs.enemy_aircraft[0])
        # action = Action(m_pidtrl.dwXpos, m_pidtrl.dwYpos, m_pidtrl.dwZpos, m_pidtrl.dwRpos)

        return action
