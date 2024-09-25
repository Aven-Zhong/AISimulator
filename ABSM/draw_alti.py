import zipfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def parse_data(data):
    records = []
    for line in data.splitlines():
        if line.startswith('2001'):
            plane_id, content = line.split(',', 1)
            attributes = content.split(',')
            coords = attributes[0].split('T=')[1].split('|')[:3]
            longitude, latitude, altitude = map(float, coords)
            records.append(altitude)
    return records



if __name__ == "__main__":
    file_path = "../record/"
    fine_name = "F-16_2024-07-04_23-18-59_group1_episode0_acmi.zip"
    step:int = 1
    x_data = []
    y_data = []
    with zipfile.ZipFile(file_path+fine_name, "r") as z:
        for file_info in z.infolist():
            print(f"Reading {file_info.filename}...")  # 打印当前文件名
            with z.open(file_info) as file:
                # 2. 处理数据
                content = file.read().decode('utf-8')
                datas = parse_data(content)

                for data in datas:
                    x_data.append(step)
                    y_data.append(data)
                    step += 1

    x_points = np.array(x_data)
    y_points = np.array(y_data)

    plt.plot(x_points, y_points)
    plt.xlabel("step")
    plt.ylabel("altitude")
    plt.show()
