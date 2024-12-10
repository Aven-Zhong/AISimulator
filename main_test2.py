from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


def fitness_func(Params):
    a = Params[0]
    b = Params[1]

    return abs(a**2 + 2*b + 0.2)


def callback(Params_k, convergence):
    global iteration
    iteration += 1
    print(f"第{iteration}代, {Params_k}最优解: {fitness_func(Params_k)}")



if __name__ == '__main__':

    # 用于记录迭代次数的变量
    iteration = 0
    bounds = [(-1.0, 1.0), (-1.0, 1.0)]
    # 运行差分进化算法
    result = differential_evolution(fitness_func,
                                    bounds,
                                    strategy='best1bin',
                                    maxiter=1000,
                                    popsize=15,
                                    callback=callback)

    optimal_a, optimal_b = result.x
    print(f"最优解: {optimal_a} {optimal_b}")
    print(f"最优值: {result.fun}")
