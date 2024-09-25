from const.Obs import *


class Judge1V1:
    def __init__(self):
        self.judge = 0

    def reset(self):
        # 重置相关处理[to do]
        print("judge reset ...")

    # 自行定义对局结束条件[0表示未结束,其余结束返回值自行定义]
    def step(self, judge_obs):
        # print("simtime = ",judge_obs.simtime)

        red_aircraft = []
        blue_aircraft = []

        # 判断处理
        for item in judge_obs.obj_list:
            if item.fac == 1:  # 红方
                if item.tp == "F16":
                    red_aircraft.append(item)
            elif item.fac == 2:  # 蓝方
                if item.tp == "F16":
                    blue_aircraft.append(item)

        # 对局时间结束,飞机都还在[to do]
        red_aircraft_num = len(red_aircraft)
        blue_aircraft_num = len(blue_aircraft)
        # if judge_obs.simtime >= 1000:
        #     return 100
        if red_aircraft_num == 0 and blue_aircraft_num != 0:
            return -1  # 蓝方胜
        elif red_aircraft_num != 0 and blue_aircraft_num == 0:
            return 1  # 红方胜

        return 0
