class CtrlInfo:
    def __init__(self, m_dwXpos=0.0, m_dwYpos=0.0, m_dwRpos=0.0, m_dwZpos=0.0):
        self.dwXpos = m_dwXpos  # 俯仰
        self.dwYpos = m_dwYpos  # 滚转
        self.dwZpos = m_dwZpos  # 油门
        self.dwRpos = m_dwRpos  # 侧滑


class FlightData:
    def __init__(self):
        self.latitude = 0  # 纬度
        self.longitude = 0  # 经度
        self.altitude = 0  # 高度
        self.theta = 0  # θ(俯仰角): 飞机的前端相对于水平线的上下倾斜
        self.phi = 0  # ϕ(滚转角): 飞机绕纵轴的旋转，影响机翼的倾斜
        self.psi = 0  # ψ(偏航角): 飞机绕垂直轴的旋转，影响飞机的左右转向
        self.alpha = 0  # α(攻角): 飞机前进方向与来流方向之间的角度，关键影响飞机的升力和阻力
        self.beta = 0  # β(侧滑角): 飞机的前进方向与来流方向在水平面内的角度，用于描述飞机是否正对着前进方向飞行。
        self.omega = [0, 0, 0]  # 飞机的角速度向量，通常包括绕三个主轴（X, Y, Z 轴）的角速度，这些角速度分别对应于滚转、俯仰和偏航运动的速率
        self.VE = [0, 0, 0]  # 飞机相对于地球的速度向量，包括东向速度、北向速度和垂直速度
        self.Vc = 0  # 飞机的空速，即飞机相对于周围空气的速度


# 飞机操控动作定义
class Action:
    def __init__(self, elevator: float = 0., aileron: float = 0., throttle: float = 0., rudder: float = 0.):
        self.elevator: float = elevator  # 俯仰 [-1,1] X
        self.aileron: float = aileron  # 滚转 [-1,1] Y
        self.throttle: float = throttle  # 油门杆位移 [0,1] Z
        self.rudder: float = rudder  # 偏航 [-1,1] R