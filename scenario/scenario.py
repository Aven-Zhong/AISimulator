import json
import random
import os

def generate_random_scenario():
    lon1 = round(random.uniform(120.335, 120.345), 3)
    lat1 = round(random.uniform(22.335, 22.345), 3)
    alt1 = random.randint(4000, 6000)
    yaw1 = random.randint(0, 359)
    spd1 = random.randint(150, 250)

    lon2 = round(random.uniform(120.32, 120.33), 3)
    lat2 = round(random.uniform(22.32, 22.33), 3)
    alt2 = random.randint(4000, 6000)
    yaw2 = random.randint(0, 359)
    spd2 = random.randint(150, 250)

    scenario = {
        "start_time": "2024-01-23 10:00:00",
        "stop_time": "2024-04-23 10:20:00",
        "objects": [
            {
                "id": "1001",
                "faction": "red",
                "lon": lon1,
                "lat": lat1,
                "alt": alt1,
                "yaw": yaw1,
                "spd": spd1,
                "missile_num": 0,
                "sensor": True
            },
            {
                "id": "2001",
                "faction": "blue",
                "lon": lon2,
                "lat": lat2,
                "alt": alt2,
                "yaw": yaw2,
                "spd": spd2,
                "missile_num": 0,
                "sensor": True
            }
        ]
    }

    return json.dumps(scenario, indent=4)

def main():
    # 创建保存文件的文件夹
    save_folder = './'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 生成10个不同的 JSON 文件并保存
    for i in range(1, 11):
        # 生成随机场景
        random_scenario = generate_random_scenario()

        # 保存到文件
        file_path = os.path.join(save_folder, f'sc{i}.json')
        with open(file_path, 'w') as file:
            file.write(random_scenario)

        print(f'Saved scenario {i} to {file_path}')

if __name__ == '__main__':
    main()
