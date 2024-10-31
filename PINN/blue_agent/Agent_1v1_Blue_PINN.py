import numpy as np

from const.Obs import *


class Agent_1v1_Blue_PINN:
    def __init__(self, id):
        self.id = id
        self.blue_agent = None

    def reset(self):
        # 重置agent相关参数
        print("blue agent reset ...")

    # 调用step函数，返回控制指令
    def step(self, obs: Observation):
        if not obs.enemy_aircraft:  # 检查敌机列表是否为空
            print("Warning: No enemy aircraft data available.")
            obs.enemy_aircraft = np.zeros(24)

        action = Action()