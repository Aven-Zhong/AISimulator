import json
import numpy as np
import math
from const.Obs import ObjState, EnemyState, Observation, JudgeObs, Action

def input_str_2_observation(input_str, my_aircraft_id):
    """
    输入的json字符串转换为本地观测数据类型
    input_str 参数为我方观测数据
    my_aircraft_id参数为我方飞机ID
    """
    obs_json = json.loads(input_str)
    # print(obs_json)
    # 存储飞机数据
    aircrafts_obj = []
    enemy_aircrafts_obj = []
    # 获取我方态势数据
    sim_time = obs_json["msg_time"]
    msg_lst = obs_json["msg_info"]
    for item in msg_lst:
        if item["data_tp"] == "track":
            track_lst = item["data_info"]
            for item_track in track_lst:
                if item_track["ID"] == my_aircraft_id:
                    aircraft: ObjState = ObjState()
                    aircraft.id = item_track["ID"]
                    aircraft.fac = item_track["Fac"]
                    aircraft.tp = item_track["Type"]
                    aircraft.lat = item_track["Latitude"]
                    aircraft.lon = item_track["Longitude"]
                    aircraft.alt = item_track["Altitude"]
                    aircraft.heading = item_track["Heading"]
                    aircraft.pitch = item_track["Pitch"]
                    aircraft.roll = item_track["Roll"]
                    aircraft.v_d = item_track["V_D"]
                    aircraft.v_e = item_track["V_E"]
                    aircraft.v_n = item_track["V_N"]
                    aircraft.a_x = item_track["accelerations_x"]
                    aircraft.a_y = item_track["accelerations_y"]
                    aircraft.a_z = item_track["accelerations_z"]
                    aircraft.alpha = item_track["alpha"]
                    aircraft.beta = item_track["beta"]
                    aircraft.p = item_track["p"]
                    aircraft.q = item_track["q"]
                    aircraft.r = item_track["r"]
                    aircraft.v_mach = item_track["velocities_mach"]
                    aircraft.v_vc_kts = item_track["velocities_vc_kts"]
                    aircrafts_obj.append(aircraft)
        elif item["data_tp"] == "DetectedInfo":
            data_info_lst = item["data_info"]
            for item_track in data_info_lst:
                if item_track["ID"] == my_aircraft_id:
                    for item_detected in item_track['DetectedTargets']:
                        aircraft: EnemyState = EnemyState()
                        aircraft.id = item_detected["E_ID"]
                        aircraft.tp = item_detected["TYPE"]
                        aircraft.lat = item_detected["Latitude"]
                        aircraft.lon = item_detected["Longitude"]
                        aircraft.alt = item_detected["Altitude"]
                        aircraft.heading = item_detected["Heading"]
                        aircraft.pitch = item_detected["Pitch"]
                        aircraft.roll = item_detected["Roll"]
                        aircraft.v_d = item_detected["V_D"]
                        aircraft.v_e = item_detected["V_E"]
                        aircraft.v_n = item_detected["V_N"]
                        aircraft.x = item_detected["X"]
                        aircraft.y = item_detected["Y"]
                        aircraft.z = item_detected["Z"]
                        aircraft.r_x = item_detected["Relative_X"]
                        aircraft.r_y = item_detected["Relative_Y"]
                        aircraft.r_z = item_detected["Relative_Z"]
                        enemy_aircrafts_obj.append(aircraft)
    obs = Observation(aircrafts_obj, enemy_aircrafts_obj, sim_time)
    return obs


def input_str_2_judge_obs(input_str):
    """
    输入的json字符串转换为裁决方的目标航迹数据
    :param input_str:
    :return:
    """
    jude_json = json.loads(input_str)
    # print(jude_json)
    aircraftlst = []
    simtime = jude_json["msg_time"]
    msg_lst = jude_json["msg_info"]
    for item_track in msg_lst:
        aircraft: ObjState = ObjState()
        aircraft.id = item_track["ID"]
        aircraft.fac = item_track["Fac"]
        aircraft.tp = item_track["Type"]
        aircraft.lat = item_track["Latitude"]
        aircraft.lon = item_track["Longitude"]
        aircraft.alt = item_track["Altitude"]
        aircraft.heading = item_track["Heading"]
        aircraft.pitch = item_track["Pitch"]
        aircraft.roll = item_track["Roll"]
        aircraft.v_d = item_track["V_D"]
        aircraft.v_e = item_track["V_E"]
        aircraft.v_n = item_track["V_N"]
        aircraft.a_x = item_track["accelerations_x"]
        aircraft.a_y = item_track["accelerations_y"]
        aircraft.a_z = item_track["accelerations_z"]
        aircraft.alpha = item_track["alpha"]
        aircraft.beta = item_track["beta"]
        aircraft.p = item_track["p"]
        aircraft.q = item_track["q"]
        aircraft.r = item_track["r"]
        aircraft.v_mach = item_track["velocities_mach"]
        aircraft.v_vc_kts = item_track["velocities_vc_kts"]
        aircraftlst.append(aircraft)

    obs = JudgeObs(aircraftlst, simtime)
    return obs


# action转换为simulator可识别的指令
def action_2_order(aid, action: Action):
    """
    action转换为simulator可识别的指令
    :param aid:
    :param action:
    :return:
    """
    order = "驾驶操控," + aid + ",2,0,Delay,Force,0|" + str(action.elevator) + "`" + str(action.aileron) + "`" + str(
        action.throttle) + "`" + str(action.rudder)
    return order


def obs_2_space(obs: Observation):
    """
    将态势实体对象转化为gym-Env要求的格式（list、ndarray、……）
    :param obs: 对象化的obs
    :return: 满足状态空间要求的obs
    """
    # 目前只做 1v1 的训练
    self_obs: ObjState = obs.self_aircraft[0]
    # 检查是否有敌机数据
    if not obs.enemy_aircraft:  # 检查敌机列表是否为空
        print("Warning: No enemy aircraft data available.")
        enemy_obs: EnemyState = EnemyState()
        return np.zeros(24)
    else:
        enemy_obs: EnemyState = obs.enemy_aircraft[0]
    # 获得距离、攻击角、逃逸角
    distance, self_attack_angle, target_escape_angle = cal_dis_attack_escape(self_obs, enemy_obs)
    # 高度
    self_alt = self_obs.alt / 10000
    enemy_alt = enemy_obs.alt / 10000
    # 速度差[0, 600]
    self_v_real = get_speed(self_obs) / 600.0
    enemy_v_real = get_speed(enemy_obs) / 600.0
    # 速度分量
    self_v_n = self_obs.v_n / 600.0
    self_v_e = self_obs.v_e / 600.0
    self_v_d = self_obs.v_d / 600.0
    # 加速度分量
    self_a_x = self_obs.a_x / 100.0
    self_a_y = self_obs.a_y / 100.0
    self_a_z = self_obs.a_z / 100.0
    # 偏航[0, 2*pi]、俯仰[-pi/2, pi/2]、滚转[-pi, pi]
    self_heading = self_obs.heading / (2 * math.pi)
    self_pitch = self_obs.pitch / (math.pi / 2)
    self_roll = self_obs.roll / math.pi
    enemy_heading = enemy_obs.heading / (2 * math.pi)
    enemy_pitch = enemy_obs.pitch / (math.pi / 2)
    enemy_roll = enemy_obs.roll / math.pi
    # 其他参数
    self_alpha = self_obs.alpha / (2 * math.pi)  # 迎角/攻角
    self_beta = self_obs.beta / (2 * math.pi)  # 侧滑角/滑移角
    self_p = self_obs.p / (2 * math.pi)  # 滚转角速度(弧度每秒)
    self_q = self_obs.q / math.pi  # 俯仰角速度(弧度每秒)
    self_r = self_obs.r / math.pi  # 侧滑角速度(弧度每秒)

    # 状态向量-24
    state = np.array(
        [distance / 10000, self_attack_angle / math.pi, target_escape_angle / math.pi, self_alt,
         enemy_alt, self_v_real, enemy_v_real, self_v_n, self_v_e, self_v_d, self_a_x, self_a_y, self_a_z,
         self_heading, self_pitch, self_roll, enemy_heading, enemy_pitch, enemy_roll,
         self_alpha, self_beta, self_p, self_q, self_r], dtype=np.float32)
    return state


def cal_dis_attack_escape(self_info: ObjState, detect_info: EnemyState):
    """
    计算距离、攻击角、逃逸角
    """
    # 计算两机距离
    distance = math.sqrt(
        detect_info.r_x * detect_info.r_x + detect_info.r_y * detect_info.r_y + detect_info.r_z * detect_info.r_z)
    # 计算攻击角[0-pi]、逃逸角[0-pi]
    self_speed_vector = cal_speed_vector(self_info)
    detect_speed_vector = cal_speed_vector(detect_info)
    self_attack_angle = math.acos((self_speed_vector[0] * detect_info.r_x + self_speed_vector[1] * detect_info.r_y +
                                   self_speed_vector[2] * detect_info.r_z) / distance)
    target_escape_angle = math.acos(
        (detect_speed_vector[0] * detect_info.r_x + detect_speed_vector[1] * detect_info.r_y +
         detect_speed_vector[2] * detect_info.r_z) / distance)
    return distance, self_attack_angle, target_escape_angle


def cal_speed_vector(info: ObjState):
    """
    返回归一化的速度矢量
    """
    speed = get_speed(info)
    return [info.v_e / speed, info.v_n / speed, info.v_d / speed]

def get_speed(info: ObjState):
    """
    返回速度
    """
    speed = math.sqrt(info.v_d * info.v_d + info.v_e * info.v_e + info.v_n * info.v_n)
    return speed
