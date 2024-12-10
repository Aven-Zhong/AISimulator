import math
import matplotlib.pyplot as plt
from PINN_roll.Env_roll import AISimEnv1v1_PINN_roll
import json
import datetime

run_times = 1  # 运行局数

if __name__ == '__main__':

    print('******************欢迎使用成都蓉奥智能空战训练平台(v1.0)**********************')

    # 打开文件
    file = open('./sc.json', 'r')

    # 读取文件内容
    content = file.read()

    # 关闭文件
    file.close()

    # 输出文件内容
    print("想定内容如下:\n", content)

    # 创建训练环境[根据情况处理]
    env = AISimEnv1v1_PINN_roll(content, 1, True, 1, True)
    roll_data = []
    pid_params = [8.99175359169354, 0.10254325666148723, 0.4726095346544904,
                  -0.7469683955814215, 1.1407645716110526e-05, 0.23309216286721124]
    index = 0
    while index < run_times:
        iteration = 1
        fitness = 0.0
        env.reset(content, index, pidParams=pid_params)
        now = datetime.datetime.now()
        milliseconds = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print("第", index, "局开始时间:", milliseconds)
        while env.step() == 0 and iteration < 500:
            env.step()
            roll_cur = env.blue_obs.self_aircraft[0].roll / math.pi * 180
            roll_data.append(roll_cur)
            fitness += abs(roll_cur - 60) * iteration
            iteration += 1
        now = datetime.datetime.now()
        milliseconds = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print("第", index, "局结束时间:", milliseconds)
        print(f"适应度值{fitness}")
        with open('./PINN_roll/file/pid_fitness.txt', 'a') as f:
            f.write(str(pid_params) + str(fitness) + '\n')

        index = index + 1
    x = [i for i in range(len(roll_data))]
    plt.plot(x, roll_data)
    plt.show()
    plt.savefig('./PINN_roll/pic/roll_data.png')
    print('******************欢迎下次继续使用成都蓉奥智能空战训练平台(v1.0)**********************')
