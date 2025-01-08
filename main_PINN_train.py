import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import keras


def physics_loss(model, inputs):
    with tf.GradientTape() as tape:
        # 假设 inputs 是 [start_roll, target_roll]
        tape.watch(inputs)
        pid_params = model(inputs)
        # 假设 pid_params 是 [Kp, Ki, Kd]
        Kp, Ki, Kd = pid_params[:, 0], pid_params[:, 1], pid_params[:, 2]
        # 计算滚转力矩 L
        error = inputs[:, 1] - inputs[:, 0]  # 目标滚转角 - 起始滚转角
        L = Kp * error + Ki * tf.cumsum(error) + Kd * tf.gradients(error, inputs)[0]

    # 计算二阶导数
    dphi_dt = tape.gradient(model(inputs), inputs)
    d2phi_dt2 = tape.gradient(dphi_dt, inputs)

    # 动力学方程残差
    residual = I_x * d2phi_dt2 - L

    # 返回残差的L2范数
    return tf.reduce_mean(residual ** 2)

# 假设数据已经以以下格式提供
data = [
    [60, [8.385328064132096, 0.003052092324208777, 0.5634218360794518,
         -0.9707341339762501, 0.00040384219108824393, 0.4407716291506472]],
    [30, [8.98658296343083, 0.003787893208417321, 0.2759817252279121,
         -0.9942659938214375, 0.0005095876340961851, 0.5136499204870901]],
    [10, [8.991377841193398, 0.004207507989427218, 0.3585520155533682,
         -0.9978995683505378, 0.0007087817624272419, 0.6511375955497881]],
    [20, [8.998597746020609, 0.004021870837041411, 0.06884790322486549,
         -0.9959876131302494, 0.0005781679743237271, 0.8880857642661126]],
    [40, [8.882962035985546, 0.0035438671383281077, 0.7627606246663766,
         -0.9879722908672679, 0.0004640817896230186, 0.17019666008703804]],
    [50, [8.772053414506237, 0.0033377094284283626, 0.5709207746079302,
         -0.9623349060076511, 0.0004243621565023365, 0.058606413672463095]],
    [70, [8.68459297062013, 0.005954736795483417, 0.13985919625923476,
         -0.8530735533396088, 0.00035438049519370685, 0.13593203049723224]],
    [80, [8.484533528599691, 0.006276982889986182, 0.9821750069790376,
         -0.9861865848704078, 0.0003681950808516188, 0.14971288255531395]],
    [90, [8.223954272562507, 0.006548150076369285, 0.5666741067741039,
         -0.9486247678699951, 0.0003441715836447169, 0.5541528496001994]]
]

# 提取目标角度、PID参数
X = np.array([item[0] for item in data]).reshape(-1, 1)  # 目标角度
y = np.array([item[1] for item in data])  # PID参数


class PINNModel(keras.Model):
    def __init__(self):
        super(PINNModel, self).__init__()
        self.dense1 = keras.layers.Dense(64, activation='relu', input_shape=(1,))
        self.dense2 = keras.layers.Dense(64, activation='relu')
        self.dense3 = keras.layers.Dense(64, activation='relu')
        self.output_layer = keras.layers.Dense(6)  # 输出是6个PID参数

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        outputs = self.output_layer(x)
        return outputs


model = PINNModel()
model.compile(optimizer='adam', loss='mse')

# 训练模型
history = model.fit(X, y, epochs=1000, batch_size=32, validation_split=0.2)

model_name = "PINN_model_latest"
# 保存模型
model.save(f'{model_name}.h5')  # 保存模型到文件

# 假设我们想要预测从0度到任意角度的PID参数
new_target_angle = 45
new_input = np.array([[new_target_angle]])

# 使用模型预测PID参数
predicted_pid_params = model.predict(new_input)
print("Predicted PID parameters:", predicted_pid_params)

# 绘制训练和验证损失
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()
