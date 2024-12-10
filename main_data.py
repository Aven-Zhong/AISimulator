import numpy as np
import math
import datetime
from scipy.optimize import differential_evolution
from PINN_roll.Env_roll import AISimEnv1v1_PINN_roll
import matplotlib.pyplot as plt


pid_values = []
fitness_values = []


def fitness_func(pidParams):
    # 打开文件
    file = open('./sc.json', 'r')
    # 读取文件内容
    content = file.read()
    # 关闭文件
    file.close()
    # 输出文件内容
    # print("想定内容如下:\n", content)

    # 创建训练环境[根据情况处理]
    env = AISimEnv1v1_PINN_roll(content, 1, False, 1, False)

    # 选择 ITAE 和超调量 MP 为适应度函数的组成部分
    kp1, ki1, kd1, kp2, ki2, kd2 = pidParams
    roll_target = 60
    w1, w2 = 0.3, 0.7  # 权重
    over_shoot = 0.0
    # 仿真500步,使用ITAE进行评估
    env.reset(content, 1, pidParams=[kp1, ki1, kd1, kp2, ki2, kd2])
    itae = 0.0
    index = 1
    while env.step() == 0 and index < 500:
        env.step()
        roll_cur = env.blue_obs.self_aircraft[0].roll / math.pi * 180
        if roll_cur - roll_target > over_shoot:
            over_shoot = roll_cur - roll_target
        itae += abs(roll_cur - roll_target) * index
        index += 1
    fitness = w1 * itae/index/10000 + w2 * over_shoot
    return fitness


# 回调函数，打印每一步的最优值
def callback(pidParams_k, convergence):

    # print(convergence)
    # print("当前参数：", pidParams_k)
    # print("当前最优值：", fitness_func(pidParams_k))
    pid_values.append(pidParams_k)
    fitness_values.append(fitness_func(pidParams_k))



if __name__ == '__main__':
    print('******************欢迎使用成都蓉奥智能空战训练平台(v1.0)**********************')

    # # 打开文件
    # file = open('./sc.json', 'r')
    # # 读取文件内容
    # content = file.read()
    # # 关闭文件
    # file.close()
    # # 输出文件内容
    # print("想定内容如下:\n", content)
    #
    # # 创建训练环境[根据情况处理]
    # env = AISimEnv1v1_PINN_roll(content, 1, False, 1, False)
    #

    start_time = datetime.datetime.now()
    milliseconds = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("开始时间:", milliseconds)
    # cur_roll = 0
    # target_roll = 60

    bounds = [(0.0, 9.0), (0.0, 1.0), (0.0, 1.0), (-1.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
    # 运行差分进化算法
    result = differential_evolution(fitness_func,
                                    bounds,
                                    callback=callback,
                                    strategy='best1bin',
                                    workers=25,
                                    maxiter=1000,
                                    popsize=25,
                                    disp=False)  # 打印内置的收敛信息

    optimal_Kp1, optimal_Ki1, optimal_Kd1, optimal_Kp2, optimal_Ki2, optimal_Kd2= result.x
    print(f"Optimal PID parameters: Kp={optimal_Kp1}, Ki={optimal_Ki1}, Kd={optimal_Kd1}")
    print(f"Optimal PID parameters: Kp={optimal_Kp2}, Ki={optimal_Ki2}, Kd={optimal_Kd2}")
    print(f"最优值: {result.fun}")
    print(f"是否成功退出：{result.success}")
    print(f"迭代次数：{result.nit}")

    print(f"终止原因：{result.message}")
    end_time = datetime.datetime.now()
    milliseconds = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("结束时间:", milliseconds)
    print("总时间", end_time-start_time)

    # 将pid参数和适应度值写入文件
    file_name = end_time.strftime("%Y-%m-%d-%H-%M-%S")
    file_log = open(f'./PINN_roll/file/log/{file_name}.txt', 'a')
    for i in range(len(pid_values)):
        print(pid_values[i], fitness_values[i])
        file_log.write(str(pid_values[i]))
        file_log.write(' ')
        file_log.write(str(fitness_values[i]))
        file_log.write('\n')
    file_log.close()
    print('******************欢迎下次继续使用成都蓉奥智能空战训练平台(v1.0)**********************')