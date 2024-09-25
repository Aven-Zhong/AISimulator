# 真实航迹状态[本机、导弹都使用该结构]
class ObjState:
    def __init__(self):
        self.id = ""  # 编号(字符串)
        self.fac = 1  # 阵营
        self.tp = "F16"  # 具体型号

        self.lat = 0.  # 纬度 (°)
        self.lon = 0.  # 经度 (°)
        self.alt = 0.  # 高度 (m)

        self.heading = 0.  # 偏航角(弧度(-PI,PI))
        self.pitch = 0.  # 俯仰角(弧度(-PI,PI))
        self.roll = 0.  # 滚转角(弧度(-PI,PI))

        self.v_d = 0.  # 地向速度 (m/s)
        self.v_e = 0.  # 东向速度 (m/s)
        self.v_n = 0.  # 北向速度 (m/s)

        self.a_x = 0.  # 加速度分量
        self.a_y = 0.  # 加速度分量
        self.a_z = 0.  # 加速度分量

        self.alpha = 0.  # 迎角 (rad)
        self.beta = 0.  # 侧滑角 (rad)

        self.p = 0.  # 滚转角速度(弧度每秒)
        self.q = 0.  # 俯仰角速度(弧度每秒)
        self.r = 0.  # 侧滑角速度(弧度每秒)

        self.v_mach = 0.  # 马赫数
        self.v_vc_kts = 0.  # 节（海里每小时）

# 探测到的飞机/导弹状态
class EnemyState:
    def __init__(self):
        self.id = ""  # 飞机编号(字符串)
        self.tp = "Aircraft"  # 飞机

        self.lat = 0.  # 纬度 (°)
        self.lon = 0.  # 经度 (°)
        self.alt = 0.  # 高度 (m)

        self.heading = 0.  # 偏航角(弧度(-PI,PI))
        self.pitch = 0.  # 俯仰角(弧度(-PI,PI))
        self.roll = 0.  # 滚转角(弧度(-PI,PI))

        self.v_d = 0.  # 地向速度 (m/s)
        self.v_e = 0.  # 东向速度 (m/s)
        self.v_n = 0.  # 北向速度 (m/s)

        self.r_x = 0.  # 两机相对x轴距离
        self.r_y = 0.  # 两机相对y轴距离
        self.r_z = 0.  # 两机相对z轴距离

        self.x = 0.
        self.y = 0.
        self.z = 0.

# 观测数据
class Observation:
    def __init__(self, self_aircraft=[], enemy_aircraft=[], sim_time=0.):
        self.sim_time: float = sim_time  # 仿真时间
        self.self_aircraft = self_aircraft  # 本机状态
        self.enemy_aircraft = enemy_aircraft  # 观测到的敌机状态


# 裁决方观测数据
class JudgeObs:
    def __init__(self, obj_list=[], sim_time=0.):
        self.sim_time = sim_time
        self.obj_list = obj_list


# 飞机操控动作定义
class Action:
    def __init__(self, elevator: float = 0., aileron: float = 0., throttle: float = 0., rudder: float = 0.):
        self.elevator: float = elevator  # 俯仰 [-1,1] X
        self.aileron: float = aileron  # 滚转 [-1,1] Y
        self.throttle: float = throttle  # 油门杆位移 [0,1] Z
        self.rudder: float = rudder  # 偏航 [-1,1] R

#pid的输入期望值
class Action_pid:
    def __init__(self, alt: float = 0., spd: float = 0., turn: float = 0.):
        self.alt: float = alt  # 高度
        self.spd: float = spd  # 速度
        self.turn: float = turn  # 转向