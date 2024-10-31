import ctypes
import json
import random

from ctypes import *
from const.Agent import Agent_1V1_Red
from PINN.blue_agent.Agent_1v1_Blue_PINN import Agent_1v1_Blue_PINN
from const.Judge import Judge1V1
from const.helper import input_str_2_observation, action_2_order, input_str_2_judge_obs
from const.Record_acmi import Record_acmi
from const.Obs import *
from const.Vis import *

red_aircraft_id = "1001"
blue_aircraft_id = "2001"
DEFAULT_SC_PATH = './scenario/sc.json'


# 1v1近距空战仿真环境(支持多实例)
class AISimEnv1v1:
    # 初始化仿真环境
    def __init__(self,
                 sc,  # 想定内容
                 grp_no,  # 实例组号
                 need_show,  # 是否需要可视化
                 need_record,  # 是否记录回放文件
                 record_interval):  # 回放记录间隔
        self.sc = sc  # 想定json内容
        self.grp_no = grp_no  # 实例组号
        self.done = False  # 想定是否结束
        self.aisimulator = ctypes.CDLL("./AISimulator.dll")  # 仿真器实例
        sim = self.aisimulator.getAIInstance(1)  # 创建实例
        input_ptr = c_char_p(sc.encode('utf-8'))
        init = self.aisimulator.Init(self.grp_no, input_ptr)  # 仿真环境初始化

        print("init= ", init)

        self.red = Agent_1V1_Red("1001")  # 根据想定里面红方的id填写
        self.blue = Agent_1v1_Blue_PINN("2001")
        self.judge = Judge1V1()  # 裁决方

        # self.vis = VisServer()  # 可视化数据推送服务
        self.record = Record_acmi(path=f"./PINN/record/", grp_no=self.grp_no)  # 数据记录
        self.need_show = need_show
        self.need_record = need_record

        self.index = 0
        self.record_interval = record_interval

        self.red_obs = None  # 红方态势信息
        self.blue_obs = None  # 蓝方态势信息
        self.judge_obs = None  # 裁决方态势信息（上帝视角）

        self.preObservation = None  # 在step过程中上一次记录的obs信息

    # 重新开始一局
    def reset(self, sc, index):
        # self.red.reset()
        self.blue.reset()
        self.judge.reset()
        # self.vis.close()
        # self.vis.VisServer()
        self.record.reset(index)

        # 采用随机想定
        random_int = random.randint(1, 10)
        new_path = DEFAULT_SC_PATH.replace('sc.json', f'sc{random_int}.json')
        print(new_path)
        file = open(new_path, 'r')
        self.sc = file.read()
        file.close()

        input_ptr = c_char_p(sc.encode('utf-8'))
        init = self.aisimulator.Init(self.grp_no, input_ptr)  # 仿真环境初始化
        self.index = index

    # 仿真环境推演一步[其返回值参考Judge程序]
    def step(self, action: list = (0, 0, 0)):
        self.aisimulator.Step(self.grp_no)

        # 1.获取态势信息 红、蓝、裁决
        self.get_data()

        # 2.进行胜负裁决判断处理
        res = self.judge.step((self.judge_obs))

        # 3.可视化
        # if self.need_show:
            # self.vis.step(self.red_obs)
            # self.vis.step(self.blue_obs)

        # 4.记录(需要记录且满足记录间隔时执行)
        if self.need_record and self.index % self.record_interval == 0:
            self.record.step(self.judge_obs)

        # 5.未结束，调用红蓝决策
        if res == 0:
            # 执行红方一步
            pid_action = Action_pid(alt=action[0],
                                    spd=action[1],
                                    turn=action[2])
            control_action = self.red.step(self.red_obs, pid_action)
            self.aisimulator.Control(self.grp_no,
                                     c_char_p(action_2_order(red_aircraft_id, control_action).encode('utf-8')))

            # 执行蓝方一步
            blue_action = self.blue.step(self.blue_obs)
            self.aisimulator.Control(self.grp_no,
                                     c_char_p(action_2_order(blue_aircraft_id, blue_action).encode('utf-8')))
        else:
            self.record.terminal()
            print("单局结束，结果为：", res)

        return res

    def get_data(self):
        """
        获取红、蓝、裁决状态数据，返回符合gym规范的状态和额外信息
        @return: (observation, info)
        """
        self.aisimulator.GetSimOutput.argtypes = []
        self.aisimulator.GetSimOutput.restype = ctypes.c_char_p
        info = {'sim_time': 0.}

        # 获取红方态势
        red_agent_input = self.aisimulator.GetSimOutput(self.grp_no, 1)
        obs_json = json.loads(red_agent_input)
        if obs_json["msg_info"] == []:
            # print(obs_json)
            # print("没有信息，推演一步，再拿一次")
            self.aisimulator.Step(self.grp_no)
            red_agent_input = self.aisimulator.GetSimOutput(self.grp_no, 1)
            # obs_json = json.loads(red_agent_input)
        self.red_obs = input_str_2_observation(red_agent_input, red_aircraft_id)

        # 获取蓝方态势
        blue_agent_inpt = self.aisimulator.GetSimOutput(self.grp_no, 2)
        self.blue_obs = input_str_2_observation(blue_agent_inpt, blue_aircraft_id)

        # 获取裁决方态势
        judge_input = self.aisimulator.GetSimOutput(self.grp_no, 0)
        self.judge_obs = input_str_2_judge_obs(judge_input)
        # print(judge_input)
