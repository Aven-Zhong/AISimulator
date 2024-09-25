import logging
import math
import json
import random

import gymnasium as gym
import numpy as np
import ctypes

from ctypes import *
from gymnasium.spaces import Box

from const.Agent import Agent_1V1_Red, Agent_1V1_Blue
from const.Judge import Judge1V1
from const.helper import input_str_2_observation, action_2_order, input_str_2_judge_obs, obs_2_space
from const.Record_acmi import Record_acmi
from const.Obs import *

CAMP_RED = 'red'
CAMP_BLUE = 'blue'
RED_AGENT_ID = '1001'
BLUE_AGENT_ID = '2001'
DEFAULT_SC_PATH = './scenario/sc.json'


# 	编写能够创建训练环境的函数，设置训练中需要的参数，例如实例号等。
def make_train_env(sc=None,
                   grp_no: int = 0,
                   need_record: bool = False,
                   record_interval: int = 1,
                   train_camp: str = 'red',
                   observation_dim: int = 24,
                   action_dim: int = 3,
                   pidPram: list = None):
    def _call():
        env = TrainEnv(sc=sc,
                       grp_no=grp_no,
                       need_record=need_record,
                       record_interval=record_interval,
                       train_camp=train_camp,
                       observation_dim=observation_dim,
                       action_dim=action_dim,
                       pidPram=pidPram)
        return env

    return _call


class TrainEnv(gym.Env):
    """
    训练环境
    """

    def __init__(self,
                 sc=None,
                 grp_no: int = 1,
                 need_record: bool = True,
                 record_interval: int = 2,
                 train_camp: str = 'red',
                 observation_dim: int = 24,
                 action_dim: int = 3,
                 pidPram: list = None):

        if sc is None:  # 若没有指定则采用默认想定
            file = open(DEFAULT_SC_PATH, 'r')
            self.sc = file.read()
            file.close()
        else:
            self.sc = sc  # 想定json内容
        self.grp_no = grp_no  # 实例组号
        self.need_record = need_record  # 是否记录
        self.record_interval = record_interval  # 记录间隔
        self.train_camp = train_camp  # 待训智能体阵营

        self.simulator = ctypes.CDLL("./AISimulator.dll")  # 仿真器实例
        self.simulator.getAIInstance(1)  # 创建实例
        input_ptr = c_char_p(self.sc.encode('utf-8'))
        init = self.simulator.Init(self.grp_no, input_ptr)  # 仿真环境初始化

        self.red = Agent_1V1_Red(RED_AGENT_ID)  # 根据想定里面红方的id填写
        self.blue = Agent_1V1_Blue(BLUE_AGENT_ID)  # 根据想定里面蓝方的id填写
        self.judge = Judge1V1()  # 裁决方实例
        self.record = Record_acmi(path=f"./train/record/", grp_no=self.grp_no)  # 数据记录

        self.episode = 0  # 本轮episode计数（用于判断本局是否记录轨迹数据）
        self.done = 0  # 裁决方单步判定结果

        self.steps = 0  # 步数计数
        self.red_obs = None  # 红方态势信息
        self.blue_obs = None  # 蓝方态势信息
        self.obs = None  # 待训智能体的态势数据，由self.train_camp决定
        self.judge_obs = None  # 裁决方态势信息（上帝视角）
        self.info = None  # 额外信息

        self.preObservation = None  # 在step过程中上一次记录的obs信息

        self.observation_space = Box(low=-1.0,
                                     high=1.0,
                                     shape=(observation_dim,),
                                     dtype=np.float32)
        # self.action_space = Box(low=np.array([-1.0, -1.0, -1.0, 0.]),
        #                         high=np.array([1.0, 1.0, 1.0, 1.0]),
        #                         shape=(action_dim,),
        #                         dtype=np.float64)
        self.action_space = Box(low=np.array([-1.0, -1.0, -1.0]),
                                high=np.array([1.0, 1.0, 1.0]),
                                shape=(action_dim,),
                                dtype=np.float64)

        logging.info(f"init = {init}")

    def reset(self, seed=None, sc=None):
        self.episode += 1
        # self.red.reset()
        self.blue.reset()
        self.judge.reset()
        if self.need_record and self.episode % self.record_interval == 0:
            self.record.reset(self.episode)
        print(f'第{self.grp_no}组{self.episode}局开始')

        # 采用随机想定
        random_int = random.randint(1, 10)
        new_path = DEFAULT_SC_PATH.replace('sc.json', f'sc{random_int}.json')
        print(new_path)
        file = open(new_path, 'r')
        self.sc = file.read()
        # print(self.sc)
        file.close()

        # if sc is None:  # 若没有指定则采用默认想定
        #     file = open(DEFAULT_SC_PATH, 'r')
        #     self.sc = file.read()
        #     file.close()
        # else:
        #     self.sc = sc  # 想定json内容

        input_ptr = c_char_p(self.sc.encode('utf-8'))
        init = self.simulator.Init(self.grp_no, input_ptr)  # 仿真环境初始化
        observation, info = self.get_data()  # 获取态势数据（包括红、蓝、裁决）

        # while self.red_obs.enemy_aircraft.alt == 0:
        #     # print("没有敌机信息再次拿信息")
        #     self.simulator.Step(self.grp_no)
        #     observation, info = self.get_data()
        # print("有敌机信息了")
        # print(self.red_obs.to_json())
        self.red.reset(self.red_obs)

        logging.info(f"init = {init}")

        return observation, info

    def step(self, action: list = (0, 0, 0)):
        self.steps += 1
        # 0.执行指令(根据待训智能体阵营判别控制指令)
        # 待训智能体执行指令
        pid_action = Action_pid(alt=action[0],
                                spd=action[1],
                                turn=action[2])
        train_agent_id = RED_AGENT_ID if self.train_camp.strip() == 'red' else BLUE_AGENT_ID

        if True:
            control_action = self.red.step(self.red_obs, pid_action)
        self.simulator.Control(self.grp_no,
                               c_char_p(action_2_order(train_agent_id, control_action).encode('utf-8')))
        # 陪练智能体执行指令
        if self.train_camp.strip() == 'red':
            blue_action = self.blue.step(self.blue_obs)
            self.simulator.Control(self.grp_no,
                                   c_char_p(action_2_order(BLUE_AGENT_ID, blue_action).encode('utf-8')))
        elif self.train_camp.strip() == 'blue':
            red_action = self.red.step(self.red_obs)
            self.simulator.Control(self.grp_no,
                                   c_char_p(action_2_order(RED_AGENT_ID, red_action).encode('utf-8')))
        # 仿真推演一步*10 10ms 0.01s
        for _ in range(10):
            self.simulator.Step(self.grp_no)

        # 1.获取态势信息(obs)
        observation, info = self.get_data()  # 符合gym规范的态势返回值

        terminated, truncated = False, False
        # 裁决方 判定是否双方都还有飞机在 ：0继续 -1蓝方胜 1红方胜
        self.done = self.judge.step(self.judge_obs)  # 暂时先不用，直接在get_state_reward里面判定self.done
        if self.done != 0:
            terminated = True
            self.save_reward()
            if self.done == -1:
                reward = -50
            else:
                reward = 50

        # 2.计算奖励 -待写
        # TODO: 计算奖励值
        if self.done == 0:
            reward = self.get_state_reward(self.red_obs, info['sim_time'])
            # 3.判断单步结束情况(继续、结束、超时) -待写
            # TODO: 判断动作执行后的对局情况，继续or正常结束or超时or…
            if self.done == 1 or self.done == 2:  # 1迎角失控 2 达到优势位置
                terminated = True  # terminated 是否达到终局条件--瞄准敌机
            if self.done == 3:  # 超时 距离过大 高度越界
                truncated = True  # truncated 是否达到截断条件：时间超出限制，智能体超出边界

        # 4.记录轨迹
        if self.need_record and self.episode % self.record_interval == 0:
            self.record.step(self.judge_obs)
            if terminated or truncated:
                self.record.terminal()

        return observation, reward, terminated, truncated, info

    def render(self):
        pass

    def get_data(self):
        """
        获取红、蓝、裁决状态数据，返回符合gym规范的状态和额外信息
        :return: (observation, info)
        """
        self.simulator.GetSimOutput.argtypes = []
        self.simulator.GetSimOutput.restype = ctypes.c_char_p
        info = {'sim_time': 0.}
        # 获取红方态势

        red_agent_input = self.simulator.GetSimOutput(self.grp_no, 1)
        obs_json = json.loads(red_agent_input)
        # print("obs_json",obs_json)

        if obs_json["msg_info"] == []:
            # print(obs_json)
            # print("没有信息，推演一步，再拿一次")
            self.simulator.Step(self.grp_no)
            red_agent_input = self.simulator.GetSimOutput(self.grp_no, 1)
            # obs_json = json.loads(red_agent_input)
        # print("输出红方态势：")
        self.red_obs = input_str_2_observation(red_agent_input, RED_AGENT_ID)

        # 获取蓝方态势
        blue_agent_input = self.simulator.GetSimOutput(self.grp_no, 2)
        # print("输出蓝方态势：")
        self.blue_obs = input_str_2_observation(blue_agent_input, BLUE_AGENT_ID)

        # 获取裁决方态势
        jude_input = self.simulator.GetSimOutput(self.grp_no, 0)
        # print("输出裁决方态势：")
        self.judge_obs = input_str_2_judge_obs(jude_input)

        if self.train_camp.strip() == 'red':
            info['sim_time'] = self.red_obs.sim_time
            self.obs = self.red_obs
            self.info = info
        elif self.train_camp.strip() == 'blue':
            info['sim_time'] = self.blue_obs.sim_time
            self.obs = self.blue_obs
            self.info = info
        else:
            logging.warning(f'train_camp错误:{self.train_camp}')

        observation = np.array(obs_2_space(self.obs), dtype=np.float32)

        return observation, info

    # 奖励判断
    def get_state_reward(self, obs: Observation, cur_time):

        self_aircraft: ObjState = obs.self_aircraft[0]
        enemy_aircraft: EnemyState = obs.enemy_aircraft[0]
        ############prepare-begin
        #####本机
        cur_self_v_n = self_aircraft.v_n  # 北向速度(m/s)
        cur_self_v_e = self_aircraft.v_e  # 东向速度(m/s)
        cur_self_v_d = self_aircraft.v_d  # 地向速度(m/s)
        cur_self_v_real = (
                                  cur_self_v_n * cur_self_v_n + cur_self_v_e * cur_self_v_e + cur_self_v_d * cur_self_v_d) ** 0.5

        cur_self_lon = self_aircraft.lon  # 经度(°)
        cur_self_lat = self_aircraft.lat  # 纬度(°)
        cur_self_alt = self_aircraft.alt  # 高度(m)

        # 飞机的失控主要的评估手段是迎角α的值，在低角度下，随着迎角增大，升力增大，即头部升高，则飞行器的飞行高度也相应增加。
        # 在迎角超过阈值后，如果再增加俯仰角度，则升力就会降低，此时，飞机的飞行高度就会急剧降低，这种现象称之为失速。
        # 仿真终止条件（小于-15° 或者大于 40°）
        cur_self_alpha = self_aircraft.alpha  # 迎角(弧度)
        cur_self_beta = self_aircraft.beta  # 攻度(弧度)

        cur_self_heading = self_aircraft.heading  # 朝向
        cur_self_pitch = self_aircraft.pitch  # 俯仰
        cur_self_roll = self_aircraft.roll  # 滚转

        cur_self_p = self_aircraft.p  # (弧度每秒)
        cur_self_q = self_aircraft.q  # (弧度每秒)
        cur_self_r = self_aircraft.r  # (弧度每秒)

        ##### 敌机
        cur_enemy_v_n = enemy_aircraft.v_n  # 北向速度(m/s)
        cur_enemy_v_e = enemy_aircraft.v_e  # 东向速度(m/s)
        cur_enemy_v_d = enemy_aircraft.v_d  # 地向速度(m/s)
        cur_enemy_v_real = (
                                   cur_enemy_v_n * cur_enemy_v_n + cur_enemy_v_e * cur_enemy_v_e + cur_enemy_v_d * cur_enemy_v_d) ** 0.5

        cur_enemy_lon = enemy_aircraft.lon  # 经度(°)
        cur_enemy_lat = enemy_aircraft.lat  # 纬度(°)
        cur_enemy_alt = enemy_aircraft.alt  # 高度(m)

        ##### 本机和敌机的相对量
        cur_deta_lon = (cur_enemy_lon - cur_self_lon)  # 两机经度差(°)
        cur_deta_lat = (cur_enemy_lat - cur_self_lat)  # 两机纬度差(°)
        cur_deta_alt = (cur_enemy_alt - cur_self_alt)  # 两机高度差(m)[当前飞行高度与敌机之间的高度差]

        # cur_deta_range = Distance_P2P(cur_self_lon,cur_self_lat,cur_enemy_lon,cur_enemy_lat,cur_self_alt,cur_enemy_alt)  #两机距离

        relative_X = enemy_aircraft.r_x  # 考虑通过经纬度换算
        relative_Y = enemy_aircraft.r_y  # 考虑通过经纬度换算
        relative_Z = enemy_aircraft.r_z  # 考虑通过经纬度换算

        cur_deta_range = (
                                 relative_X * relative_X + relative_Y * relative_Y + relative_Z * relative_Z) ** 0.5  # **乘方 #两机距离
        # 攻击角，天线偏转角，我机速度矢量和我机指向敌机的距离矢量的夹角
        # cur_self_v_e 东向速度(m/s) ；math.acos(x) 返回 x 的反余弦，结果范围在 0 到 pi 之间。

        if cur_deta_range == 0 or cur_self_v_real == 0:
            print(enemy_aircraft)

        cur_attack_angle = math.acos(
            (cur_self_v_e * relative_X + cur_self_v_n * relative_Y - cur_self_v_d * relative_Z) / (
                    cur_deta_range * cur_self_v_real))  # 攻击角
        # 防御角，视界角，敌机速度矢量和我机指向敌机的距离矢量的夹角，0-180°
        cur_escape_angle = math.acos(
            (cur_enemy_v_e * relative_X + cur_enemy_v_n * relative_Y - cur_enemy_v_d * relative_Z) / (
                    cur_deta_range * cur_enemy_v_real))  # [逃逸角]

        # 增加一写相对量的计算
        cur_deta_v_n = cur_self_v_n - cur_enemy_v_n  # 北向速度差(m/s)
        cur_deta_v_e = cur_self_v_e - cur_enemy_v_e  # 东向速度差(m/s)
        cur_deta_v_d = cur_self_v_d - cur_enemy_v_d  # 地向速度差(m/s)
        cur_deta_v_real = cur_self_v_real - cur_enemy_v_real  # 速度大小差

        ############prepare-end

        ###仿真终止条件判定--begin
        ##1迎角失控 2 达到优势位置 3超时 距离过大 高度越界
        Distance_To_Win = 2000
        Time_Limit = 100

        cur_step_reward_total = 0

        # 1.迎角失控
        if cur_self_alpha < -15 * math.pi / 180 or cur_self_alpha > 40 * math.pi / 180:
            cur_step_reward_total = -90
            self.done = 1
            print("迎角失控，当前迎角", cur_self_alpha, ",存活时间:", cur_time, "   与敌机距离： ", cur_deta_range)
            self.red.total_reward += cur_step_reward_total
            self.save_reward()
            return cur_step_reward_total

        # 2.优势位置锁定判定
        if cur_attack_angle < math.pi / 6 and cur_escape_angle < math.pi / 6 and cur_deta_range < Distance_To_Win:  # 攻击角和距离满足条件
            cur_step_reward_total = 50 + (Time_Limit - cur_time) / Time_Limit
            self.done = 2
            print("达成目标,结束时间：", cur_time, 'cur_attack_angle: ', cur_attack_angle, 'cur_escape_angle: ',
                  cur_escape_angle, "   与敌机距离： ", cur_deta_range)
            self.red.total_reward += cur_step_reward_total
            self.save_reward()
            return cur_step_reward_total

        # 3.高度/距离越界
        if cur_self_alt < 500 or cur_self_alt > 10000 or cur_deta_range > 5000:
            cur_step_reward_total = -50
            self.done = 3
            print("高度越界或距离过大,当前高度", cur_self_alt, ",存活时间:", cur_time, "   与敌机距离： ",
                  cur_deta_range)
            self.red.total_reward += cur_step_reward_total
            self.save_reward()
            return cur_step_reward_total

        # 4.仿真时间到
        if cur_time >= Time_Limit:  # 到300s双方都存活,则认为平局
            cur_step_reward_total = -10
            self.done = 3
            print("仿真时间达到", Time_Limit, "s,当前高度:", cur_self_alt, "当前迎角：   ", cur_self_alpha,
                  "   与敌机距离： ", cur_deta_range, "   天线偏转角： ", cur_attack_angle)
            self.red.total_reward += cur_step_reward_total
            self.save_reward()
            return cur_step_reward_total

        ###仿真终止条件判定--end

        ##################单步奖励--begin
        # 角度优势
        cur_step_reward_attack_angle = 0
        if self.red.pre_attack_angle > cur_attack_angle:
            cur_step_reward_attack_angle += 1
        elif self.red.pre_attack_angle == cur_attack_angle:
            cur_step_reward_attack_angle += 0
        else:
            cur_step_reward_attack_angle -= 1

        # 距离优势
        cur_step_reward_distance = 0
        if math.fabs(cur_deta_lon) > math.fabs(self.red.pre_deta_lon):  # 两机经度差(°)
            cur_step_reward_distance -= 0.5
        else:
            cur_step_reward_distance += 0.5
        if math.fabs(cur_deta_lat) > math.fabs(self.red.pre_deta_lat):  # 两机纬度差(°)
            cur_step_reward_distance -= 0.5
        else:
            cur_step_reward_distance += 0.5

        # 高度优势
        cur_step_reward_alt = 0
        if math.fabs(cur_deta_alt) > math.fabs(self.red.pre_deta_alt):
            cur_step_reward_alt -= 1
        else:
            cur_step_reward_alt += 1

        # 单步总奖励
        W_total = 0.0001
        W_single = [3, 6, 2]
        cur_step_reward_attack_angle = W_total * W_single[0] * cur_step_reward_attack_angle
        cur_step_reward_distance = W_total * W_single[1] * cur_step_reward_distance
        cur_step_reward_alt = W_total * W_single[2] * cur_step_reward_alt
        cur_step_reward_total = cur_step_reward_attack_angle + cur_step_reward_distance + cur_step_reward_alt

        # 输出奖励辅助变量
        self.red.total_reward_attack_angle += cur_step_reward_attack_angle  # 累积角度奖励
        self.red.total_reward_distance += cur_step_reward_distance  # 累积距离奖励
        self.red.total_reward_alt += cur_step_reward_alt  # 累积高度奖励
        self.red.total_reward += cur_step_reward_total
        ###########单步奖励--end

        self.red.total_reward += cur_step_reward_total

        return cur_step_reward_total

    # #记录当局所有奖励-------------------------------------------------------------------------------
    # 在这儿记录 ---朝向（攻击角奖励）、高度（高度差奖励）、速度--- 奖励

    def save_reward(self):
        print("记录当局所有奖励")
        # 累积角度奖励
        filename_total_reward = './train/log_reward/TXT/total_reward_attack_angle.txt'
        with open(filename_total_reward, 'a') as file:
            file.write("{} \n".format(self.red.total_reward_attack_angle))

        # 累积距离奖励
        filename_total_reward = './train/log_reward/TXT/total_reward_distance.txt'
        with open(filename_total_reward, 'a') as file:
            file.write("{} \n".format(self.red.total_reward_distance))

        # 累积高度奖励
        filename_total_reward = './train/log_reward/TXT/total_reward_alt.txt'
        with open(filename_total_reward, 'a') as file:
            file.write("{} \n".format(self.red.total_reward_alt))

        # 全局奖励
        filename_total_reward = './train/log_reward/TXT/total_reward.txt'
        with open(filename_total_reward, 'a') as file:
            file.write("{} \n".format(self.red.total_reward))

    # #记录当局所有奖励-------------------------------------------------------------------------------
