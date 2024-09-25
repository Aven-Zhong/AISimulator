# 实时可视化显示
import logging
import socket

from const.Obs import Observation

red_aircraft_id = "1001"
blue_aircraft_id = "2001"


class VisServer:
    def __init__(self, host='127.0.0.1', port=42674):
        self.server_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 定义IP和地址端口号
        self.host = host
        self.port = port
        self.server_sk.bind((self.host, self.port))

        # 开始监听连接
        self.server_sk.listen()
        print('等待客户端连接...')
        self.c, self.addr = self.server_sk.accept()

        self.red_id = red_aircraft_id
        self.blue_id = blue_aircraft_id
        self._handshake()
        self._init_aircraft()

    def step(self, obs_data: Observation):
        b_data = self._obs_2_acmi(obs_data)
        self.c.send(b_data)

    def close(self):
        self.c.close()
        self.server_sk.close()

    def _handshake(self):
        shake_pkg = 'XtraLib.Stream.0\nTacview.RealTimeTelemetry.0\nsimulation_viewer\n\0'
        self.c.send(shake_pkg.encode(encoding='utf-8'))
        shake_rcv = self.c.recv(1024)
        if shake_rcv is not None:
            file_head = 'FileType=text/acmi/tacview\nFileVersion=2.2\n'
            self.c.send(file_head.encode(encoding='utf-8'))
            reference_time = '0,2025-09-25T06:00:00Z\n'
            self.c.send(reference_time.encode(encoding='utf-8'))
        else:
            logging.error(f'与tacview客户端握手失败,地址：{self.addr}')

    def _init_aircraft(self):
        init_red = f'{self.red_id},T=120.33|22.33|5000.0|0.0|-0.0|0.0,Name=F-16C,Type=Medium+Air+FixedWing,color=Red\n'
        init_blue = f'{self.blue_id},T=120.34|22.33|5000.0|0.0|-0.0|0.0,Name=F-16C,Type=Medium+Air+FixedWing,color=Blue\n'
        self.c.send(init_red.encode(encoding='utf-8'))
        self.c.send(init_blue.encode(encoding='utf-8'))

    def _obs_2_acmi(self, obs: Observation):
        sim_time = obs.sim_time
        obs = obs.my_aircraft
        aid = self.red_id if obs.fac == 1 else self.blue_id
        lon = obs.lon
        lat = obs.lat
        alt = obs.alt
        roll = obs.roll
        pitch = obs.pitch
        yaw = obs.heading
        acmi_data = f'#{sim_time}\n{aid},T={lon}|{lat}|{alt}|{roll}|{pitch}|{yaw}\n'
        encoding_data = acmi_data.encode(encoding='utf-8')
        return encoding_data
