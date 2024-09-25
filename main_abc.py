import gymnasium as gym
from datetime import datetime
from stable_baselines3 import PPO
import multiprocessing

from stable_baselines3.common.vec_env import SubprocVecEnv

import train.TrainEnv as TrainEnv

from re_abc.reabc import Reabc

# 	编写主程序：
# 创建训练所需的环境：由于希望多进程环境训练，所以使用SubprocVecEnv
if __name__ == '__main__':
    # 对于AutoDriver中的10个pid参数运用abc算法寻找较优解
    center_param = [[1, 0, 1], [-5, 0, 0], [2, 0, 0], [-1, 0, 0], [0.5, 0.00001, 0],
                    [0.5, 0.00001, 0], [0.040, 0.0002, 0], [0.005, 0.00001, 0.09], [0.30, 0, 0.5], [0.13, 0, 0.1]]
    reabc = Reabc(center_param)

    maxCycle = 100
    start_time = datetime.now()
    pre_time = start_time
    for i in range(maxCycle):
        reabc.employPhase()
        reabc.onlookerPhase()
        reabc.scoutPhase()
        reabc.recordBest(i)

        now_time = datetime.now()
        print(f'----cycle {i}----start_time {start_time}----now_time {now_time}'
              f'----this_cycle_time {now_time - pre_time}----total_time {now_time - start_time}----')
        pre_time = now_time

        if i % 5 == 0:
            reabc.saveRecord(i)
    reabc.saveRecord(maxCycle)


# start_time = 2024-6-13-01-51-26  end_time = 2024-6-15-08-30-13