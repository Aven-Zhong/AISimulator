import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import keras

"""
求解PDE：
f`(x) =f(x)
f(0) = 1
"""


# 模型定义
class Net(keras.Model):
    def __init__(self, NN):
        super(Net, self).__init__()
        self.input_layer = keras.layers.Dense(NN, input_dim=1)
        self.hidden_layer = keras.layers.Dense(NN)
        self.output_layer = keras.layers.Dense(1)

    def call(self, x):
        out = tf.tanh(self.input_layer(x))
        out = tf.tanh(self.hidden_layer(out))
        out = self.output_layer(out)
        return out


net = Net(20)  # 3层 20\20\1

# 损失函数
mse = keras.losses.MeanSquaredError()
# 优化器
optimizer = keras.optimizers.Adam(learning_rate=1e-4)
# 打包
net.compile(optimizer, loss=mse)

plt.ion()  # 动态图
fig = plt.figure(figsize=(6, 5))

iterations = 20000
for epoch in range(iterations):

    with tf.GradientTape() as tape:
        # Boundary Loss f(0)=1
        x_0 = tf.zeros((2000, 1))  # 表示2000个0
        y_0 = net(x_0)
        mse_i = mse(y_0, tf.ones((2000, 1)))  # 损失函数，表示边界损失

        # ODE Loss
        x_in = tf.Variable(tf.random.uniform((2000, 1), dtype=tf.float32, minval=0.0, maxval=2.0))

        with tf.GradientTape() as t:
            y_hat = net(x_in)  # f(x)

        dy_dx = t.gradient(y_hat, x_in)  # f`(x)
        mse_f = mse(y_hat, dy_dx)
        loss = mse_i + mse_f

    gradients = tape.gradient(loss, net.trainable_variables)
    optimizer.apply_gradients(zip(gradients, net.trainable_variables))

    if (epoch + 1) % 100 == 0:
        fig.clf()  # 清空当前Figure对象
        fig.suptitle("epoch: %d" % (epoch + 1))
        ax = fig.add_subplot(111)
        y_real = tf.exp(x_in)  # y 真实值
        y_pred = net(x_in)  # y 预测值
        ax.scatter(x_in.numpy(), y_real.numpy(), label="true")
        ax.scatter(x_in.numpy(), y_pred.numpy(), c='red', label="pred")
        ax.legend()
        plt.pause(0.1)
plt.show()