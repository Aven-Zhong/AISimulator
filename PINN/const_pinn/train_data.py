from const.Obs import JudgeObs, ObjState
import math


# 用于生成训练数据的类
class TrainData:
    def __init__(self, path='/PINN/train_data/'):
        self.path = path
        self.data_to_write = ""  # 存储状态文本数据（每一局结束后再进行文件写入，以降低I/O开销）
        self.train_file_name = ""  # 存储当前文件名称
        self.train_file = ""  # 存储当前文件路径

        # 计算平均误差来评定直线
        self.error_sum = 0
        self.count = 0

    def reset(self, pidParams: list):
        self.train_file_name = f"p{pidParams[0]}_i{pidParams[1]}_d{pidParams[2]}"
        self.train_file = self.path + self.train_file_name + '.txt'
        self.data_to_write = f"{pidParams[0]},{pidParams[1]},{pidParams[2]}\n"

    def step(self, judgeObs: JudgeObs):
        for item in judgeObs.obj_list:
            plane_data: ObjState =item
            # obs_data =f"{plane_data.id},T={plane_data.lon}|{plane_data.lat}|{plane_data.alt}|{plane_data.roll*180/math.pi}|" \
            #            f"{plane_data.pitch*180/math.pi}|{plane_data.heading*180/math.pi}"
            # heading = plane_data.heading
            # 写入蓝方数据
            if plane_data.id == "2001":
                obs_data = f"{plane_data.lon}|{plane_data.lat}|{plane_data.alt}|{plane_data.roll*180/math.pi}|" \
                      f"{plane_data.pitch*180/math.pi}|{plane_data.heading*180/math.pi}\n"
                self.error_sum += abs(plane_data.alt - 5000)
                self.data_to_write += obs_data
                self.count += 1

    def terminal(self):
        """
        每一局结束时需调用本函数进行状态数据的写入（每一局结束后再进行文件写入，以降低I/O开销）
        """
        if self.count == 0:
            # 当count为0时，说明没有数据，则不写入文件
            return

        self.data_to_write = f"{self.error_sum / self.count}\n" + self.data_to_write
        # 将数据写入文件中去
        with open(self.train_file, 'a', encoding='utf-8') as file:
            file.write(self.data_to_write)

        self.data_to_write = ""
        self.count = 0
