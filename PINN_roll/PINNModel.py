import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import keras


class PINNModel(keras.Model):
    def __init__(self, input_dim=4, output_dim=3):
        super(PINNModel, self).__init__()
        self.input_dim = keras.layers.Input(shape=(input_dim,))
        self.dense1 = keras.layers.Dense(64, activation='tanh')
        self.dense2 = keras.layers.Dense(64, activation='tanh')
        self.dense3 = keras.layers.Dense(output_dim)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.dense3(x)


def get_data():
    data_path = "../data/data_train_1.txt"
