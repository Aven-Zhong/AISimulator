# 用于实现记录[to do]
import csv

from const.Obs import JudgeObs, ObjState


class Record:
    def __init__(self, path='./record', grp_no=0):
        self.seq = 0
        self.path = path
        self.grp_no = grp_no

    def step(self, data):
        # 记录这步所需的内容[to do]
        lst: JudgeObs = data
        for item in lst.objlst:
            plane_data: ObjState = item
            camp = 'Red' if plane_data.fac == 1 else 'Blue'
            save_path = f'{self.path}/{camp}/F-16 ({plane_data.id})[{camp}]_{self.grp_no}_{self.seq}.csv'
            buffer = [round(lst.simtime, 5),
                      round(plane_data.lon, 8),
                      round(plane_data.lat, 8),
                      round(plane_data.alt, 3),
                      round(plane_data.roll, 5),
                      round(plane_data.pitch, 5),
                      round(plane_data.heading, 5)]
            with open(save_path, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                if lst.simtime < 0.02:  # 写入数据名称
                    csv_writer.writerow(['Time', 'Longitude', 'Latitude', 'Altitude', 'Roll (deg)', 'Pitch (deg)', 'Yaw (deg)'])
                csv_writer.writerow(buffer)

    def set_seq(self, seq):
        self.seq = seq
