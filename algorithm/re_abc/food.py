import sys
import pandas as pd
import numpy as np
import datetime
from stable_baselines3 import PPO
import multiprocessing
import zipfile
import os
import shutil

from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.vec_env import DummyVecEnv
import train.TrainEnv as TrainEnv


from train.blue_agent.PID_ctrl.PID_definition import PID



class Food:
    def __init__(self, m_position):
        self.position = m_position
        self.fitness = sys.float_info.max
        self.trial = 0
        self.dataFrames = []  # 用于计算直线误差的数据

        # 将./train/record中的文件移动到re_abc/record中 防止上次的记录影响到本次计算
        self.move_file("./train/record", "./re_abc/record")

    def calculateFitness(self):
        """
        计算适应度，飞机飞直线，计算直线偏离
        """

        # 传入pid参数 TrainEnv:TrainEnv.make_train_env -> TrainEnv:self.blue = Agent_1V1_Blue(BLUE_AGENT_ID)
        # -> Agent:self.blue_agent = highAgent() -> highAgent:self.lowAgent = lowAgent()
        # lowAgent:->self.autoDriver = AutoDriver() -> PID_baseControl:AutoDriver

        multiprocessing.freeze_support()
        # 读取想定
        file = open('/scenario/sc.json', 'r')
        content = file.read()
        file.close()
        train_mode = 0  # 0:重新训练1:继续训练
        group_nums = 5
        vec_env = SubprocVecEnv([TrainEnv.make_train_env(sc=None,
                                                         grp_no=i + 1,
                                                         need_record=True,
                                                         observation_dim=24,
                                                         action_dim=3,
                                                         record_interval=100,
                                                         pidPram=self.position) for i in range(group_nums)])
        # 如果是继续训练，加载已保存的模型
        if train_mode == 1:
            model_name = "PPO_model_latest"
            model = PPO.load(f"./train/model/{model_name}")  # 加载模型

        model = PPO(policy='MlpPolicy', env=vec_env, verbose=1)
        for i in range(100):  # 这里假设训练100次
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

        # 对obs_data进行处理 计算fitness时 1.读取record文件中的所有数据， 2.处理数据 3.将record中的文件移动到./re_abc/record/acmi{i}

        # 1.读取数据 2.处理数据
        self.read_data()

        # 根据dataFrames计算适应度值 使用平均数
        self.fitness = self.calculate_average_error()


        # 3.移动文件
        self.move_file("./train/record", "./re_abc/record")


    def parse_data(self, data):
        records = []
        for line in data.splitlines():
            if line.startswith('2001'):
                plane_id, content = line.split(',', 1)
                attributes = content.split(',')
                coords = attributes[0].split('T=')[1].split('|')[:3]
                longitude, latitude, altitude = map(float, coords)
                records.append({'longitude': longitude, 'latitude': latitude, 'altitude': altitude})
        return pd.DataFrame(records)



    def calculate_3d_deviation(self, df):
        # 用简化模型直接使用经度和纬度差值
        start = df.iloc[0][['longitude', 'latitude', 'altitude']]
        end = df.iloc[-1][['longitude', 'latitude', 'altitude']]

        # 计算直线方向向量
        line_vector = end - start
        line_vector /= np.linalg.norm(line_vector)

        # 计算每个点到直线的距离
        def point_to_line_distance(row):
            point_vector = row[['longitude', 'latitude', 'altitude']] - start
            point_to_line_vector = point_vector - np.dot(point_vector, line_vector) * line_vector
            return np.linalg.norm(point_to_line_vector)

        df['deviation'] = df.apply(point_to_line_distance, axis=1)
        return df

    def read_data(self):
        """
        读取"./train/record"中的所有轨迹记录，并将之处理为pd.dataFrame文件
        """
        file_path = "./train/record"
        zip_files = [file for file in os.listdir(file_path) if file.endswith('.zip')]
        for zip_file in zip_files:
            path = os.path.join(file_path, zip_file)
            with zipfile.ZipFile(path, "r") as z:
                for file_info in z.infolist():
                    print(f"Reading {file_info.filename}...")  # 打印当前文件名
                    with z.open(file_info) as file:
                        # 2. 处理数据
                        content = file.read().decode('utf-8')
                        df = self.parse_data(content)
                        if not df.empty:
                            df = self.calculate_3d_deviation(df)
                            self.dataFrames.append(df)
                        else:
                            print("没有蓝色方数据可供分析")

    def calculate_average_error(self):
        """
        计算平均误差
        @return: 平均误差
        """
        errors = []
        # weights = []
        for dataFrame in self.dataFrames:
            errors.append(dataFrame['deviation'].mean())
        #    weights.append(len(dataFrame))
        # weighted_sum_error = sum(error * weight for error, weight in zip(errors, weights))
        # total_weight = sum(weights)
        if len(errors) == 0:
            return sys.float_info.max
        return sum(errors) / len(errors)


    def move_file(self, m_source_dir, m_target_dir):
        """
        将源文件夹中的文件全部移动到目标文件夹
        @param m_source_dir: 源文件夹
        @param m_target_dir: 目标文件夹
        """
        # 确保目标目录存在
        if not os.path.exists(m_target_dir):
            os.makedirs(m_target_dir)
        # 遍历源目录中的所有文件和目录
        for filename in os.listdir(m_source_dir):
            source_path = os.path.join(m_source_dir, filename)
            target_path = os.path.join(m_target_dir, filename)

            # 移动文件或目录
            shutil.move(source_path, target_path)
            print(f"Moved {source_path} to {target_path}")