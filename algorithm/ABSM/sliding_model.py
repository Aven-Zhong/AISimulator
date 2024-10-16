"""
sliding model
"""
import numpy as np


class SlidingModelController:
    def __init__(self, kp, ki, kd, limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0
        self.limit = limit
        self.sliding_surface = 0
        self.adaptive_term = 0

    def set_limits(self, low, high):
        self.limit = (low, high)

    def update(self, error, delta_t):
        self.integral += error * delta_t
        derivative = (error - self.previous_error) / delta_t
        self.previous_error = error

        # update sliding surface
        self.sliding_surface = self.kp * error + self.ki * self.integral + self.kd * derivative

        # 补偿不确定性和干扰的自适应项
        self.adaptive_term += 0.01 * self.sliding_surface

        # 滑模控制率
        control_signal = -np.sign(self.sliding_surface) * (abs(self.sliding_surface) + self.adaptive_term)

        control_signal = max(self.limit[0], min(self.limit[1], control_signal))

        return control_signal
