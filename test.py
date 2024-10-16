import time

from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym
from datetime import datetime
from stable_baselines3 import PPO
import multiprocessing

from stable_baselines3.common.vec_env import SubprocVecEnv

import train.TrainEnv as TrainEnv


def SubprocFunc():
    multiprocessing.freeze_support()
    # 读取想定
    file = open('/scenario/sc.json', 'r')
    content = file.read()
    file.close()
    train_mode = 0  # 0:重新训练1:继续训练
    group_nums = 1
    vec_env = SubprocVecEnv([TrainEnv.make_train_env(sc=None,
                                                     grp_no=i + 1,
                                                     need_record=True,
                                                     observation_dim=24,
                                                     action_dim=3,
                                                     record_interval=100,
                                                     pidPram=None) for i in range(group_nums)])
    # 如果是继续训练，加载已保存的模型
    if train_mode == 1:
        model_name = "PPO_model_latest"
        model = PPO.load(f"./train/model/{model_name}")  # 加载模型

    model = PPO(policy='MlpPolicy', env=vec_env, verbose=1)
    for i in range(10):  # 这里假设训练100次
        print("##########################第" + str(i) + "次训练开始:##########################")
        model.learn(total_timesteps=2048 * group_nums)  # 假设每次训练10000步
        # 每隔一定步数保存模型
        if i > 10 and i % 2 == 0:  # 每隔2步保存一次
            # model_name = "PPO_model_latest_" + str(i)
            model_name = "PPO_model_latest"
            model.save(f"./train/model/{model_name}")

    # 最后保存一次模型+
    model_name = "PPO_model_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model.save(f"./train/model/{model_name}")


if __name__ == '__main__':
    # SubprocFunc()
    start_time = datetime.now()
    pre_time = start_time
    for i in range(10):
        time.sleep(2)
        now_time = datetime.now()
        print(f'----cycle {i}----start_time {start_time}----now_time {now_time}'
              f'----this_cycle_time {now_time-pre_time}----total_time {now_time-start_time}----')

        with open('algorithm/re_abc/log.txt', 'a', encoding='utf-8') as file:
            file.write(f'----cycle {i}----start_time {start_time}----now_time {now_time}'
              f'----this_cycle_time {(now_time-pre_time)}----total_time {now_time-start_time}----\n')
        pre_time = now_time
