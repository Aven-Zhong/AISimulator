import keras
import tensorflow as tf
import numpy as np
from PINN.Env_PINN import AISimEnv1v1_PINN
import json
import random
import math
from const.Obs import ObjState


class PINNModel(keras.Model):
    def __init__(self, input_dim, output_dim):
        super(PINNModel, self).__init__()
        self.dense1 = keras.layers.Dense(64, activation='relu')
        self.dense2 = keras.layers.Dense(64, activation='relu')
        self.dense3 = keras.layers.Dense(output_dim)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.dense3(x)


# 定义训练过程
def train(model, env, target_position, epochs=1000):
    """
    训练模型，优化PID参数
    """
    optimizer = keras.optimizers.Adam()  # 优化器
    for epoch in range(epochs):
        state = get_start_state()  # 获取当前飞行器状态

        # 将状态转换为适合神经网络输入的格式
        state_values = np.array([state['lon'], state['lat'], state['alt'],
                                 state['yaw'], state['spd']])

        with tf.GradientTape() as tape:
            # 通过PINN模型预测PID增益
            pid_params = model(tf.convert_to_tensor(state_values[None, :], dtype=tf.float32))

            # 计算飞行控制损失
            loss_value = loss_fn(pid_params, env, target_position)

        # 反向传播
        gradients = tape.gradient(loss_value, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))

        # 输出训练过程的损失
        if epoch % 100 == 0:
            print(f'Epoch {epoch}, Loss: {loss_value}')


# 获取飞行器初始的状态信息（位置、速度、姿态、角速度等）
def get_start_state():
    state = {"lon": 120.33,
             "lat": 22.33,
             "alt": 5000,
             "yaw": 0,
             "spd": 200}
    return state


def loss_fn(pid_params, env, target_position):
    """
    计算损失函数
    sim_data: 仿真数据，包括位置、姿态、加速度等
    """
    # 利用该pid获取仿真数据
    blue_obs_list = run_simulation(env, pid_params)
    # 从仿真数据中提取位置数据
    lon_list = [obs.lon for obs in blue_obs_list]  # 经度列表
    lat_list = [obs.lat for obs in blue_obs_list]  # 纬度列表
    alt_list = [obs.alt for obs in blue_obs_list]  # 高度列表
    print(lon_list)
    # 物理损失
    # 将飞行器的实际位置与目标位置进行比较，计算误差
    lon_error = tf.reduce_mean(tf.square(tf.convert_to_tensor(lon_list, dtype=tf.float32) - target_position[0]))
    # lat_error = tf.reduce_mean(tf.square(tf.convert_to_tensor(lat_list, dtype=tf.float32) - target_position[1]))
    # alt_error = tf.reduce_mean(tf.square(tf.convert_to_tensor(alt_list, dtype=tf.float32) - target_position[2]))

    return lon_error


def run_simulation(env: AISimEnv1v1_PINN, pidParams):
    blue_objs: list[ObjState] = []
    is_random_sc = False  # 用于判断时采用随机想定 还是固定想定
    if is_random_sc:
        # 采用随机想定
        random_int = random.randint(1, 10)
        new_path = f'./scenario/sc{random_int}.json'
        # print(new_path)

    else:
        # 采用固定想定
        new_path = './scenario/sc.json'

    file_sc = open(new_path, 'r')
    sc_new = file_sc.read()
    file_sc.close()
    print("想定内容如下:\n", sc_new)

    parsed_data = json.loads(sc_new)
    blue_start_status = next((obj for obj in parsed_data['objects'] if obj['id'] == "2001"), None)
    alt_exp = blue_start_status["alt"]
    spd_exp = blue_start_status["spd"]
    yaw_exp = blue_start_status["yaw"]
    exp_status = [alt_exp, spd_exp, yaw_exp]

    env.reset(sc_new, 1, alt_exp, spd_exp, pidParams)

    # print("第", index, "局开始时间:", milliseconds)
    index = 0
    while env.step() == 0 and index < 500:
        env.step()
        obs: ObjState = env.blue_obs.self_aircraft[0]  # ObjState list
        # print(f"lat:{obs.lat} lon:{obs.lon} alt:{obs.alt} alt_exp:{alt_exp} heading:{obs.heading}")
        blue_objs.append(obs)
        index += 1
    # # 分别提取高度、速度、航向
    # altitudes = [obj.alt for obj in blue_objs]
    # speeds = [math.sqrt(obj.v_d ** 2 + obj.v_e ** 2 + obj.v_n ** 2) for obj in blue_objs]
    # yaws = [obj.heading*180/math.pi for obj in blue_objs]

    # 提取模拟的轨迹数据，转化为 TensorFlow 张量
    # altitudes = tf.convert_to_tensor([obj.alt for obj in blue_objs], dtype=tf.float32)
    # speeds = tf.convert_to_tensor([math.sqrt(obj.v_d ** 2 + obj.v_e ** 2 + obj.v_n ** 2) for obj in blue_objs],
    #                               dtype=tf.float32)
    # yaws = tf.convert_to_tensor([obj.heading * 180 / math.pi for obj in blue_objs], dtype=tf.float32)
    return blue_objs

