import keras
import tensorflow as tf
from PINN.Env_PINN import AISimEnv1v1_PINN
import datetime
import numpy as np
from PINN.PINNModel import PINNModel
import matplotlib.pyplot as plt
import PINN.const_pinn.tools as tools

run_times = 100  # 运行局数

if __name__ == '__main__':

    print('******************欢迎使用成都蓉奥智能空战训练平台(v1.0)**********************')

    # 读取想定
    file = open('./scenario/sc.json', 'r')
    content = file.read()
    file.close()

    # 输出文件内容
    print("想定内容如下:\n", content)

    # 创建训练环境[根据情况处理]
    env = AISimEnv1v1_PINN(content, 1, True, 1, True)

    # target_path = np.linspace([0, 0, 10000], [1, 1, 10000], 2000)  # [lat, lon, alt]
    # target_attitude = np.zeros((2000, 3))  # [roll, pitch, yaw]，假设目标姿态为全 0

    # 损失函数权重
    lambda_params = [1.0, 0.5, 0.1, 0.01]

    # 飞机质量和重力加速度
    mass = 13000  # kg
    gravity = 9.81  # m/s^2

    # 初始化PINN模型
    layers = [5, 50, 50, 50, 3]
    pinn = PINNModel(layers)

    # 损失函数
    mse = keras.losses.MeanSquaredError()
    # 优化器
    optimizer = keras.optimizers.Adam(learning_rate=1e-4)
    # 打包
    pinn.compile(optimizer, loss=mse)

    # 动态绘图设置
    plt.ion()
    fig = plt.figure(figsize=(6, 5))

    # 训练迭代
    iterations = 20000

    for epoch in range(iterations):
        # 使用仿真环境生成数据 pos_1、pos_2、...pos_n
        sim_data =

        # 1. path loss
        # 2. Attitude Loss
        # 3. Physics Loss
        # 4. Control Smoothness Loss

        # 1.生成随机想定，想定即为神经网络的输入
        x_in = 0
        # 2.获取神经网络的输出：pid参数

        with tf.GradientTape() as tape:
        # 获取 PID 参数
            pid_params = pinn(tf.constant([[0.0]]))
            pid_params = tf.squeeze(pid_params)

        # 计算损失
        loss = loss_fn(pid_params)


    # 计算梯度并优化
    gradients = tape.gradient(loss, pid_net.trainable_variables)
    optimizer.apply_gradients(zip(gradients, pid_net.trainable_variables))

    # 动态绘图
    if (epoch + 1) % 100 == 0:
        fig.clf()
        fig.suptitle(f"Epoch: {epoch + 1}, Loss: {loss.numpy():.3e}")
        ax = fig.add_subplot(111)

        # 绘制路径
        ax.plot(target_path[:, 0], target_path[:, 1], label="True Path", color="blue")
        ax.scatter(sim_data["position"][:, 0], sim_data["position"][:, 1], c="red", label="Predicted Path")
        ax.legend()
        plt.pause(0.1)
    plt.show()


def loss_fn(pidParams):
        """
        计算损失函数
        sim_data: 仿真数据，包括位置、姿态、加速度等
        """
        # 1.生成随机想定
        sc = tools.generate_random_scenario()
        # 2.重置仿真环境
        env.reset(sc,1, pidParams)

        while env.step() == 0:
            env.step()



        # 1. Path Loss
        position = tf.convert_to_tensor(sim_data["position"], dtype=tf.float32)
        path_loss = tf.reduce_mean(tf.square(position - self.target_path))

        # 2. Attitude Loss
        attitude = tf.convert_to_tensor(sim_data["attitude"], dtype=tf.float32)
        attitude_loss = tf.reduce_mean(tf.square(attitude - self.target_attitude))

        # 3. Physics Loss
        acceleration = tf.convert_to_tensor(sim_data["a"], dtype=tf.float32)
        alpha = tf.convert_to_tensor(sim_data["alpha"], dtype=tf.float32)
        forces = self.mass * acceleration
        lift = forces[:, 2] * tf.cos(alpha)  # Z 方向升力
        drag = forces[:, 0] * tf.cos(alpha)  # X 方向阻力
        physics_loss = tf.reduce_mean(tf.square(lift) + tf.square(drag))

        # 4. Control Smoothness Loss
        control_inputs = tf.convert_to_tensor(sim_data["controls"], dtype=tf.float32)
        control_diff = control_inputs[1:] - control_inputs[:-1]
        smoothness_loss = tf.reduce_mean(tf.square(control_diff))

        # 综合损失
        total_loss = (self.lambda_params[0] * path_loss +
                      self.lambda_params[1] * attitude_loss +
                      self.lambda_params[2] * physics_loss +
                      self.lambda_params[3] * smoothness_loss)
        return total_loss

