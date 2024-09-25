import zipfile
import math
import os
from datetime import datetime
from const.Obs import JudgeObs, ObjState

'''
本脚本用于生成 Tacview 回放记录 ACMI 格式的文件 @ wsy
更多高阶玩儿法请参考官方文档：https://www.tacview.net/documentation/acmi/en/
'''


class Record_acmi:
    def __init__(self, path='./record/', grp_no=0):
        self.path = path  # 文件存储路径
        self.grp_no = grp_no  # 环境组号
        self.data_to_write = ""  # 存储状态文本数据（每一局结束后再进行文件写入，以降低I/O开销）
        self.acmi_file_name = ""  # 存储当前acmi文件名称
        self.acmi_file = ""  # 存储当前acmi文件路径
        self.zip_file = ""  # 存储zip文件路径
        self.record_flag = False  # 用于判断本局是否开始记录观测数据

    def reset(self, episode: int):
        """
        环境进行 reset 时需调用本函数进行文件初始化；需传入 episode 参数
        """
        self.record_flag = False
        # 获取当前时间
        formatted_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # ISO 8601 标准
        now_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # 存储文件名
        file_name = f'F-16_{now_time}_group{self.grp_no}_episode{episode}_acmi'
        self.zip_file = self.path + file_name + '.zip'
        self.acmi_file_name = file_name + '.txt'
        self.acmi_file = self.path + self.acmi_file_name
        # 进行 acmi 格式文件初始化
        with open(self.acmi_file, 'a', encoding='utf-8') as file:
            data_to_write = f"FileType=text/acmi/tacview\nFileVersion=2.2\n"
            data_to_write += f"0,ReferenceTime={formatted_time}\n"
            file.write(data_to_write)

    def step(self, judgeObs: JudgeObs):
        """
        环境进行 step 时需调用本函数进行状态数据记录；需传入裁决方观测数据 judgeObs
        """
        # 记录时间
        self.data_to_write += f"#{judgeObs.sim_time}\n"
        for item in judgeObs.obj_list:
            plane_data: ObjState = item
            # 记录观测数据
            camp = 'Red' if plane_data.fac == 1 else 'Blue'
            obs_data = f"{plane_data.id},T={plane_data.lon}|{plane_data.lat}|{plane_data.alt}|{plane_data.roll*180/math.pi}|" \
                       f"{plane_data.pitch*180/math.pi}|{plane_data.heading*180/math.pi}"
            if not self.record_flag:
                # 以下飞机属性只需要写入一次即可
                obs_data += f",Name=F-16,Type=Medium+Air+FixedWing,CallSign=F-16 {plane_data.id},Color={camp}\n"
            else:
                obs_data += f"\n"
            self.data_to_write += obs_data
        if not self.record_flag:
            self.record_flag = True

    def terminal(self):
        """
        每一局结束时需调用本函数进行状态数据的写入（每一局结束后再进行文件写入，以降低I/O开销）
        """
        # 将数据写入文件中
        with open(self.acmi_file, 'a', encoding='utf-8') as file:
            file.write(self.data_to_write)
        # 将文件压缩成 zip
        # 【可选项】 txt/zip 都可直接拖入 Tacview 进行回放
        with zipfile.ZipFile(self.zip_file, 'a') as zip_file:
            zip_file.write(self.acmi_file, arcname=self.acmi_file_name)
        os.remove(self.acmi_file)  # 压缩后需删除原文件

        # 清空数据
        self.data_to_write = ""

