import gymnasium as gym
import datetime
from stable_baselines3 import PPO
import multiprocessing

from stable_baselines3.common.vec_env import SubprocVecEnv

import train.TrainEnv as TrainEnv

# 	编写主程序：
# 创建训练所需的环境：由于希望多进程环境训练，所以使用SubprocVecEnv
if __name__ == '__main__':
    multiprocessing.freeze_support()
    # 读取想定
    file = open('./scenario/sc.json', 'r')
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
        model.learn(total_timesteps=2048*group_nums)  # 假设每次训练10000步
        # 每隔一定步数保存模型
        if i > 10 and i % 2 == 0:  # 每隔2步保存一次
            # model_name = "PPO_model_latest_" + str(i)
            model_name = "PPO_model_latest"
            model.save(f"./train/model/{model_name}")


    # 最后保存一次模型+
    model_name = "PPO_model_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model.save(f"./train/model/{model_name}")
