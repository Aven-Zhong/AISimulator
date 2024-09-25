import random
import sys
from re_abc.food import Food
from datetime import datetime


class Reabc:
    def __init__(self, m_center_params=None, m_NP=100, m_limit=20, m_elite=20):
        """
        @param m_center_params: 以它为中心向周围探索,探索范围为[-1.0,1.0]
        @param m_NP: 种群规模
        @param m_limit: 限制
        @param m_elite: 精英数量
        """
        self.foods: list[Food] = [self.create_food(m_center_params) for _ in range(m_NP)]  # 每个食物源包含控制的10个pid参数
        self.NP: int = m_NP
        self.limit: int = m_limit
        self.eliteCount: int = m_elite
        self.centerParams = m_center_params
        self.bestFood = min(self.foods, key=lambda x: x.fitness)
        self.bestFitness = self.bestFood.fitness

        self.records: list = []


    def create_food(self,center_params):
        pos = [[random.uniform(-1.0, 1.0) + cp for cp in params] for params in center_params]
        food = Food(pos)
        food.calculateFitness()
        return food


    def employPhase(self):
        """
        雇用蜂阶段
        """
        # 精英的确定 按照适应度排序，前elitesCount个为精英
        self.foods.sort(key=lambda f: f.fitness)

        # 雇佣蜂寻找新的食物源
        for i in range(self.NP):
            phi = random.uniform(-1.0, 1.0)
            # 选择一个与之不同的食物源
            neighbor = self.get_random_integer_excluding_x(self.NP, i)
            # 选择一个精英
            elite = self.get_random_integer_excluding_x(self.eliteCount, i)
            # 生成新的食物源

            newPos = []
            for j in range(10):
                pid = []
                for k in range(3):
                    num = (self.foods[neighbor].position[j][k] +
                           phi * (self.foods[elite].position[j][k] - self.foods[neighbor].position[j][k]))
                    # 给num添加限制范围
                    num = max(min(num, self.centerParams[j][k] + 1.0), self.centerParams[j][k] - 1.0)
                    pid.append(num)
                newPos.append(pid)

            newFood = Food(newPos)
            newFood.calculateFitness()
            self.update_food_source(i, newFood)

    def onlookerPhase(self):
        """
        观察蜂阶段 基于排序选择
        """
        # 按适应度排序
        self.foods.sort(key=lambda f: f.fitness)

        # 根据适应度选择食物源
        for i in range(self.NP):
            eliteIndex = self.selectionBySort()
            phi = random.uniform(-1.0, 1.0)

            # 生成新的食物源
            newPos = []
            for j in range(10):
                pid = []
                for k in range(3):
                    num = self.foods[i].position[j][k] + phi * (
                                self.foods[i].position[j][k] - self.foods[eliteIndex].position[j][k])
                    # 给num添加限制范围
                    num = max(min(num, self.centerParams[j][k] + 1.0), self.centerParams[j][k] - 1.0)
                    pid.append(num)
                newPos.append(pid)

            newFood = Food(newPos)
            newFood.calculateFitness()
            self.update_food_source(i, newFood)

    def scoutPhase(self):
        """
        侦察蜂阶段
        """
        for i in range(self.NP):
            if self.foods[i].trial > self.limit:
                # 超过限度，生成新的食物源
                newFood = self.create_food(self.centerParams)
                newFood.calculateFitness()
                self.foods[i] = newFood
                if newFood.fitness < self.bestFitness:
                    self.bestFitness = newFood.fitness
                    self.bestFood = newFood
                self.foods[i].trial = 0

    def get_random_integer_excluding_x(self, m_range: int, x: int) -> int:
        """
        获取0到m_range(不包括m_range)，除了x的整数
        """
        while True:
            # 生成0到NP-1的随机整数
            random_integer = random.randint(0, m_range - 1)
            # 如果该数不是x，则返回该整数
            if random_integer != x:
                return random_integer

    def selectionBySort(self):
        """
        基于排序 按比例选择
        """
        total = 0.0
        probability = []
        for i in range(1, self.NP + 1):
            total += 1 / i
            probability.append(i / 1)
        rand_num = random.uniform(0.0, total)

        sum_prob = 0.0
        for i in range(self.NP):
            sum_prob += probability[i]
            if rand_num < sum_prob:
                return i
        return self.NP - 1  # 为防止浮点数累加误差，确保返回一个有效索引

    def update_food_source(self, index, new_food):
        """
        替换当前食物源如果新食物源适应度更高，并更新全局最优解
        """
        if new_food.fitness < self.foods[index].fitness:
            self.foods[index] = new_food
            self.foods[index].trial = 0  # 重置次数
            if new_food.fitness < self.bestFitness:
                self.bestFood = new_food
                self.bestFitness = new_food.fitness
            self.foods[index].trial += 1

    def recordBest(self, cycle: int = 0):
        """
        记录每个周期的最佳适应度和相应的PID参数
        """
        record_lines = [
            f"Cycle: {cycle}",
            f"Best Fitness: {self.bestFitness}",
            "Position:"
        ]
        record_lines.extend(', '.join(map(str, item)) for item in self.bestFood.position)
        self.records.append("\n".join(record_lines))

    def saveRecord(self, cycleCount):
        """
        将所有周期的记录保存到文本文件中
        """
        # 获取当前时间
        now_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = './re_abc/bestRecord'
        # 存储文件名
        file_name = f'{now_time}__best_cycle_{cycleCount}.txt'
        best_file = path + file_name
        try:
            with open(best_file, 'w',encoding='utf-8') as file:
                file.write('\n\n'.join(self.records))
                print(f"Record saved successfully to {file_name}.")
        except IOError as e:
            print(f"Failed to save record: {e}")

