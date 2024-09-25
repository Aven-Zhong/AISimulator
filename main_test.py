import sys

sys.path.append('Env')
import train.TrainEnv as TrainEnv
from Env import AISimEnv1v1
import json
import datetime

run_times = 100000  # 运行局数

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
    env = AISimEnv1v1(content, 1, True, True, 1)

    index = 0
    while index < run_times:
        env.reset(content, index)
        now = datetime.datetime.now()
        milliseconds = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print("第", index, "局开始时间:", milliseconds)
        while env.step() == 0:
            env.step()
            # env.get_output()
        now = datetime.datetime.now()
        milliseconds = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print("第", index, "局结束时间:", milliseconds)
        index = index + 1

    print('******************欢迎下次继续使用成都蓉奥智能空战训练平台(v1.0)**********************')
