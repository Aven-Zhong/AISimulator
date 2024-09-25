from platypus import NSGAII, Problem, Real  # 多目标优化算法库
from scipy.integrate import odeint
import numpy as np


# 定义动态模型
def aircraft_dynamics(x, t, u, A, B):
    return np.dot(A, x) + np.dot(B, u)

class flight_condition:
    def __init__(self):
        self.A = []


class Moea:
    def __init__(self):
        self.controller_params = []
        self.flight_condition = []

        # 定义优化问题
        self.problem = Problem(6, 3)  # 假设控制器有6个参数，3个目标函数
        self.problem.types[:] = Real(0, 1)  # 参数范围假设为0到1之间
        self.problem.constraints[:] = "<=0"  # 约束条件，视具体情况而定
        self.problem.directions[:] = Problem.MINIMIZE  # 定义优化方向，最小化目标
        self.problem.function = self.objectives
        self.pareto_front = []

    def run(self):
        algorithm = NSGAII(self.problem)
        algorithm.run(10000)
        self.pareto_front = algorithm.result

        for solution in self.pareto_front:
            print("Controller parameters:", solution.variables)
            print("Objective values (IAE, ITAE, ITSE):", solution.objectives)

    # 定义性能指标函数
    def iae(self):
        # 计算IAE指标
        A, B, C, D = self.flight_condition
        x0 = np.zeros(A.shape[0])
        t = np.linspace(0, 10, 1000)
        u = lambda t: np.sin(t)  # 输入信号
        x = odeint(aircraft_dynamics, x0, t, args=(u(t), A, B))
        error = x[:, 0]  # 假设第一个状态变量为误差
        iae_value = np.trapz(np.abs(error), t)
        return iae_value

    def itae(self):
        # 计算ITAE指标
        A, B, C, D = self.flight_condition
        x0 = np.zeros(A.shape[0])
        t = np.linspace(0, 10, 1000)
        u = lambda t: np.sin(t)
        x = odeint(aircraft_dynamics, x0, t, args=(u(t), A, B))
        error = x[:, 0]
        itae_value = np.trapz(t * np.abs(error), t)
        return itae_value

    def itse(self):
        # 计算ITAE指标
        A, B, C, D = self.flight_condition
        x0 = np.zeros(A.shape[0])
        t = np.linspace(0, 10, 1000)
        u = lambda t: np.sin(t)
        x = odeint(aircraft_dynamics, x0, t, args=(u(t), A, B))
        error = x[:, 0]
        itse_value = np.trapz(t * error ** 2, t)
        return itse_value

    # 定义目标函数
    def objectives(self, controller_params):
        flight_condition_1 = ...
        flight_condition_2 = ...
        return [self.iae(controller_params, flight_condition_1),
                self.itae(controller_params, flight_condition_1),
                self.itse(controller_params, flight_condition_2)]









