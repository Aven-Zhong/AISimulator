import math

from train.blue_agent.PID_ctrl.PID_baseControl import FlightData
from train.blue_agent.lowAgent import lowAgent


class highAgent:
    def __init__(self):
        self.lowAgent = lowAgent()  # 创建 lowAgent 对象

    def action_feizhixian(self, self_aircraft, enemy_aircraft):

        ###############################局势解析-begin####################################################################
        self_aircraft, enemy_aircraft = self_aircraft, enemy_aircraft
        # # 根据敌我高度，升降
        # # 根据敌我速度距离，加减
        # # 根据敌机在左右加减，攻击角
        #
        # #####本机
        # cur_self_heading = self_aircraft.heading  # 朝向
        # cur_self_pitch = self_aircraft.pitch  # 俯仰
        # cur_self_roll = self_aircraft.roll  # 滚转
        #
        # cur_self_v_n = self_aircraft.v_n  # 北向速度(m/s)
        # cur_self_v_e = self_aircraft.v_e  # 东向速度(m/s)
        # cur_self_v_d = self_aircraft.v_d  # 地向速度(m/s)
        # cur_self_v_real = (
        #                           cur_self_v_n * cur_self_v_n + cur_self_v_e * cur_self_v_e + cur_self_v_d * cur_self_v_d) ** 0.5
        # cur_self_alt = self_aircraft.alt  # 高度(m)
        #
        # ##### 敌机
        # cur_enemy_v_n = enemy_aircraft.v_n  # 北向速度(m/s)
        # cur_enemy_v_e = enemy_aircraft.v_e  # 东向速度(m/s)
        # cur_enemy_v_d = enemy_aircraft.v_d  # 地向速度(m/s) 上下升高的作用
        # cur_enemy_v_real = (
        #                            cur_enemy_v_n * cur_enemy_v_n + cur_enemy_v_e * cur_enemy_v_e + cur_enemy_v_d * cur_enemy_v_d) ** 0.5
        # cur_enemy_alt = enemy_aircraft.alt  # 高度(m)
        #
        # ###两机相对量
        # relative_X = enemy_aircraft.r_x  # 考虑通过经纬度换算
        # relative_Y = enemy_aircraft.r_y  # 考虑通过经纬度换算
        # relative_Z = enemy_aircraft.r_z  # 考虑通过经纬度换算
        #
        # # 两机距离
        # cur_deta_range = (relative_X * relative_X + relative_Y * relative_Y + relative_Z * relative_Z) ** 0.5
        #
        # cur_attack_angle = math.acos(
        #     (cur_self_v_e * relative_X + cur_self_v_n * relative_Y - cur_self_v_d * relative_Z) / (
        #             cur_deta_range * cur_self_v_real))  # 攻击角(弧度值)
        #
        # cur_escape_angle = math.acos(
        #     (cur_enemy_v_e * relative_X + cur_enemy_v_n * relative_Y - cur_enemy_v_d * relative_Z) / (
        #             cur_deta_range * cur_enemy_v_real))  # [逃逸角]

        ###############################局势解析-end#######################################################################

        # 每次做决策前，记得更新PID中的本机数据
        self.lowAgent.updateFlightData(self_aircraft)  # 更新PID的数据

        ###############################做决策-begin######################################################################

        m_pidtrl = self.lowAgent.autoDriver.altiCtrl(5000, 200)
        m_rollCtrl = self.lowAgent.autoDriver.rollCtrl(0)
        m_pidtrl.dwYpos = m_rollCtrl.dwYpos

        return m_pidtrl

        ###############################做决策-end######################################################################

    def action_zhuiji(self, self_aircraft, enemy_aircraft):

        ###############################局势解析-begin####################################################################
        self_aircraft, enemy_aircraft = self_aircraft, enemy_aircraft
        # 根据敌我高度，升降
        # 根据敌我速度距离，加减
        # 根据敌机在左右加减，攻击角

        #####本机
        cur_self_heading = self_aircraft.heading  # 朝向
        cur_self_pitch = self_aircraft.pitch  # 俯仰
        cur_self_roll = self_aircraft.roll  # 滚转

        cur_self_v_n = self_aircraft.v_n  # 北向速度(m/s)
        cur_self_v_e = self_aircraft.v_e  # 东向速度(m/s)
        cur_self_v_d = self_aircraft.v_d  # 地向速度(m/s)
        cur_self_v_real = (
                                  cur_self_v_n * cur_self_v_n + cur_self_v_e * cur_self_v_e + cur_self_v_d * cur_self_v_d) ** 0.5
        cur_self_alt = self_aircraft.alt  # 高度(m)

        ##### 敌机
        cur_enemy_v_n = enemy_aircraft.v_n  # 北向速度(m/s)
        cur_enemy_v_e = enemy_aircraft.v_e  # 东向速度(m/s)
        cur_enemy_v_d = enemy_aircraft.v_d  # 地向速度(m/s) 上下升高的作用
        cur_enemy_v_real = (
                                   cur_enemy_v_n * cur_enemy_v_n + cur_enemy_v_e * cur_enemy_v_e + cur_enemy_v_d * cur_enemy_v_d) ** 0.5
        cur_enemy_alt = enemy_aircraft.alt  # 高度(m)

        ###两机相对量
        relative_X = enemy_aircraft.r_x  # 考虑通过经纬度换算
        relative_Y = enemy_aircraft.r_y  # 考虑通过经纬度换算
        relative_Z = enemy_aircraft.r_z  # 考虑通过经纬度换算

        # 两机距离
        cur_deta_range = (relative_X * relative_X + relative_Y * relative_Y + relative_Z * relative_Z) ** 0.5

        cur_attack_angle = math.acos(
            (cur_self_v_e * relative_X + cur_self_v_n * relative_Y - cur_self_v_d * relative_Z) / (
                    cur_deta_range * cur_self_v_real))  # 攻击角(弧度值)

        cur_escape_angle = math.acos(
            (cur_enemy_v_e * relative_X + cur_enemy_v_n * relative_Y - cur_enemy_v_d * relative_Z) / (
                    cur_deta_range * cur_enemy_v_real))  # [逃逸角]

        ###############################局势解析-end#######################################################################

        # 每次做决策前，记得更新PID中的本机数据
        self.lowAgent.updateFlightData(self_aircraft)  # 更新PID的数据

        ###############################做决策-begin######################################################################

        # 高度
        alti_exp = cur_enemy_alt

        # 速度
        if cur_deta_range > 20000:
            spd_exp = cur_enemy_v_real + 100
        elif cur_deta_range >= 10000 and cur_deta_range < 20000:
            # spd_exp=300
            spd_exp = cur_enemy_v_real + 50 + 50 * (cur_deta_range - 10000) / 10000
        elif cur_deta_range >= 5000 and cur_deta_range < 10000:
            spd_exp = cur_enemy_v_real + 20 + 50 * (cur_deta_range - 5000) / 5000
        elif cur_deta_range >= 1000 and cur_deta_range < 5000:
            spd_exp = cur_enemy_v_real + 20 * (cur_deta_range - 1000) / 4000
        else:
            spd_exp = cur_enemy_v_real

        # 转向
        x = relative_X  # 向量的 x 分量
        y = relative_Y  # 向量的 y 分量
        angle_deg = self.lowAgent.transfer_angel(x, y)
        angle_rad = math.radians(angle_deg)
        if cur_self_heading == 2 * math.pi:
            cur_self_heading = 0

        if angle_rad > cur_self_heading:
            tmp = angle_rad - cur_self_heading
            if tmp >= math.pi:
                tmp = 2 * math.pi - tmp
                m_rollCtrl = self.lowAgent.turnLeft(tmp)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在左侧
            else:
                m_rollCtrl = self.lowAgent.turnRight(tmp)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在右侧
        elif angle_rad < cur_self_heading:
            tmp = cur_self_heading - angle_rad
            if tmp >= math.pi:
                tmp = 2 * math.pi - tmp
                m_rollCtrl = self.lowAgent.turnRight(tmp)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在右侧
            else:
                m_rollCtrl = self.lowAgent.turnLeft(tmp)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在左侧
        else:
            m_rollCtrl = self.lowAgent.autoDriver.rollCtrl(0)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在正前方

        # def stage_climb(self, alti_exp, spd_exp, alti_cur, spd_cur):
        m_pidtrl = self.lowAgent.stage_climb(alti_exp, spd_exp, cur_self_alt, cur_self_v_real)
        m_pidtrl.dwYpos = m_rollCtrl.dwYpos

        return m_pidtrl

        ###############################做决策-end######################################################################


    # 接受网络输出的三个维度值,经过PID后输出飞控的四个值
    def action_pid(self, self_aircraft, pid_action):
        ###############################局势解析-begin####################################################################
        self_aircraft = self_aircraft
        #####本机
        cur_self_heading = self_aircraft.heading  # 朝向
        cur_self_pitch = self_aircraft.pitch  # 俯仰
        cur_self_roll = self_aircraft.roll  # 滚转

        cur_self_v_n = self_aircraft.v_n  # 北向速度(m/s)
        cur_self_v_e = self_aircraft.v_e  # 东向速度(m/s)
        cur_self_v_d = self_aircraft.v_d  # 地向速度(m/s)
        cur_self_v_real = (
                                  cur_self_v_n * cur_self_v_n + cur_self_v_e * cur_self_v_e + cur_self_v_d * cur_self_v_d) ** 0.5
        cur_self_alt = self_aircraft.alt  # 高度(m)
        ###############################局势解析-end#######################################################################

        # 每次做决策前，记得更新PID中的本机数据
        self.lowAgent.updateFlightData(self_aircraft)  # 更新PID的数据

        ###############################做决策-begin######################################################################

        # 高度
        alti_exp = pid_action.alt * 50

        # 速度
        spd_exp = pid_action.spd * 5

        # 转向
        turn_exp = pid_action.turn * math.pi

        m_rollCtrl = self.lowAgent.autoDriver.rollCtrl(turn_exp)  # 我机朝向矢量+我机和敌机距离矢量=====判定其在正前方
        m_pidtrl = self.lowAgent.autoDriver.altiCtrl(alti_exp, spd_exp)
        m_pidtrl.dwYpos = m_rollCtrl.dwYpos

        return m_pidtrl

        ###############################做决策-end######################################################################
