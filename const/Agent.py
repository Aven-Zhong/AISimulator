import json
import math
import os
import numpy as np
from const.Obs import *
from train.blue_agent.highAgent import highAgent


# 红方智能体[红方开发人员基于]
class Agent_1V1_Red:
    def __init__(self, id):
        self.id = id
        self.red_agent = highAgent()

        ## 红方记录辅助变量
        self.pre_deta_lon = 0  # 上一步的经度差
        self.pre_deta_lat = 0  # 上一步的纬度差
        self.pre_deta_alt = 0  # 上一步的高度差

        self.pre_attack_angle = 0  # 上一步的攻击角
        self.pre_escape_angle = 0  # 上一步的逃逸角

        self.total_reward = 0
        self.total_reward_attack_angle = 0
        self.total_reward_distance = 0
        self.total_reward_alt = 0

    def reset(self, obs: Observation):
        # 重置agent相关参数[to do]
        ###prepared-begin
        self_aircraft: ObjState = obs.self_aircraft[0]
        enemy_aircraft: EnemyState = obs.enemy_aircraft[0]
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

        self.pre_deta_lon = cur_deta_lon  # 上一步的经度差
        self.pre_deta_lat = cur_deta_lat  # 上一步的纬度差
        self.pre_deta_alt = cur_deta_alt  # 上一步的高度差

        self.pre_attack_angle = cur_attack_angle  # 上一步的攻击角
        self.pre_escape_angle = cur_escape_angle  # 上一步的逃逸角

        self.total_reward = 0
        self.total_reward_attack_angle = 0
        self.total_reward_distance = 0
        self.total_reward_alt = 0

        print("red agent reset ...")

    # 调用step函数,返回控制指令[obs:红方观测信息]
    def step(self, obs: Observation, pid_action: Action_pid):
        # print("red决策")
        # action = Action()
        # print(pid_action.alt,pid_action.spd,pid_action.turn)
        m_pidtrl = self.red_agent.action_pid(obs.self_aircraft[0], pid_action)
        action = Action(m_pidtrl.dwXpos, m_pidtrl.dwYpos, m_pidtrl.dwZpos, m_pidtrl.dwRpos)
        return action


# 蓝方智能体---待写，用PID写一个飞直线的
class Agent_1V1_Blue:
    def __init__(self, id):
        self.id = id
        self.blue_agent = highAgent()

    def reset(self):
        # 重置agent相关参数[to do]
        print("blue agent reset ...")

    # 调用step函数,返回控制指令
    def step(self, obs: Observation):
        if not obs.enemy_aircraft:  # 检查敌机列表是否为空
            print("Warning: No enemy aircraft data available.")
            obs.enemy_aircraft = np.zeros(24)
        m_pidtrl = self.blue_agent.action_feizhixian(obs.self_aircraft[0], obs.enemy_aircraft[0])
        action = Action(m_pidtrl.dwXpos, m_pidtrl.dwYpos, m_pidtrl.dwZpos, m_pidtrl.dwRpos)

        return action
