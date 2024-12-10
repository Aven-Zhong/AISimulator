# pid控制 AutoDriver类  
# 基础控制

| FlightData        | 意义                      | CtrlInfo | 意义 |
|-------------------|:------------------------|----------|:---|
| latitude = 0      | 纬度                      | m_dwXpos | 俯仰 |
| longitude = 0     | 经度                      | m_dwYpos | 滚转 |
| altitude = 0      | 高度                      | m_dwZpos | 油门 |
| theta = 0         | θ(俯仰角): 飞机的前端相对于水平线的上   | m_dwRpos | 侧滑 |
| phi = 0           | ϕ(滚转角): 飞机绕纵轴的旋转，影响机翼的倾 | 
| psi = 0           | ψ(偏航角): 飞机绕垂直轴的旋转，影响飞机的 | 
| alpha = 0         | α(攻角): 飞机前进方向与来流方向之间的   | 
| beta = 0          | β(侧滑角): 飞机的前进方向与来流方向在水  | 
| omega = [0, 0, 0] | 飞机的角速度向量，通常包括           | 
| VE = [0, 0, 0]    | 飞机相对于地球的速度向量，包括东        | 
| Vc = 0            | 飞机的空速，即飞机相对于周围空气的速度     |

| 序号 |            pid名称             |         params         |        limits |
|----|:----------------------------:|:----------------------:|--------------:|
| 1  |   m_fPitchCtrl_m_fPitch_u    |       (1, 0, 1)        |     (-20, 20) |
| 2  |     m_fPitchCtrl_u_ctrl      |       (-5, 0, 0)       |       (-1, 1) |
| 3  |       rollCtrl_roll_u        |       (2, 0, 0)        |       (-9, 9) |
| 4  |       rollCtrl_u_ctrl        |       (-1, 0, 0)       |       (-1, 1) |
| 5  |       slipCtrl_slipPID       |   (0.5, 0.00001, 0)    |       (-1, 1) |
| 6  |      acceSpdCtrl_u_ctrl      |   (0.5, 0.00001, 0)    |        (0, 1) |
| 7  |      vertSpdCtrl_Vspd_u      |   (0.040, 0.0002, 0)   | (-1.57, 1.57) |
| 8  |        altiCtrl_alt_u        | (0.005, 0.00001, 0.09) | (-1.57, 1.57) |
| 9  | m_fPitchCtrlSpd_spd_m_fPitch |     (0.30, 0, 0.5)     | (-1.57, 1.57) |
| 10 |       psiCtrl_psi_roll       |     (0.13, 0, 0.1)     |      (-9, 9)) |



# 动作控制

| 俯仰角控制 |              输入               |           pid           |          输出 |
|-------|:-----------------------------:|:-----------------------:|------------:|
| 1     |  theta_exp, flightData.theta  | m_fPitchCtrl_m_fPitch_u |          uc |
| 2     | uc, flightData.omega[1] (角速度) |   m_fPitchCtrl_u_ctrl   | ctrl.dwXpos |

| 滚转角控制 |              输入               |       pid       |          输出 |
|-------|:-----------------------------:|:---------------:|------------:|
| 3     |   roll_exp, flightData.phi    | rollCtrl_roll_u |          uc |
| 4     | uc, flightData.omega[0] (角速度) | rollCtrl_u_ctrl | ctrl.dwYpos |

| 侧滑角控制 |            输入             |       pid        |          输出 |
|-------|:-------------------------:|:----------------:|------------:|
| 5     | slip_exp, flightData.beta | slipCtrl_slipPID | ctrl.dwRpos |


| 垂直速度控制 |            输入             |       pid        |          输出 |
|--------|:-------------------------:|:----------------:|------------:|
| 5      | vert_spd_exp, flightData.VE[2] | vertSpdCtrl_Vspd_u | u_m_fPitch |
| 5      | vert_spd_exp, flightData.VE[2] | vertSpdCtrl_Vspd_u | u_m_fPitch |


def vertSpdCtrl(self, vert_spd_exp, spd_exp):
    # 垂直速度控制
    ctrl = CtrlInfo()
    self.vertSpdCtrl_Vspd_u.setPid(vert_spd_exp, self.flightData.VE[2])
    u_m_fPitch = -self.vertSpdCtrl_Vspd_u.update()
    ctrl.dwXpos = self.thetaCtrl(u_m_fPitch).dwXpos
    ctrl.dwZpos = self.acceSpdCtrl(spd_exp, u_m_fPitch).dwZpos
    return ctrl

def altiCtrl(self, alti_exp, spd_exp):
    # 高度控制
    ctrl = CtrlInfo()
    self.altiCtrl_alt_u.setPid(alti_exp, self.flightData.altitude)
    u_m_fPitch = self.altiCtrl_alt_u.update()
    ctrl.dwXpos = self.thetaCtrl(u_m_fPitch).dwXpos
    ctrl.dwZpos = self.acceSpdCtrl(spd_exp, u_m_fPitch).dwZpos
    ctrl.dwYpos = self.rollCtrl(0).dwYpos
    # print(ctrl.dwYpos)
    # print("PID里的当前高度：", self.flightData.altitude)
    # print("期望高度：", alti_exp)
    return ctrl

def thetaCtrlSpd(self, spd_exp):
    # 俯仰控制速度
    ctrl = CtrlInfo()
    self.m_fPitchCtrlSpd_spd_m_fPitch.setPid(spd_exp, self.flightData.Vc)
    theta_exp = -self.m_fPitchCtrlSpd_spd_m_fPitch.update()
    ctrl.dwXpos = self.thetaCtrl(theta_exp).dwXpos
    return ctrl

def acceSpdCtrl(self, spd_exp, theta_exp):
    # 油门控制速度
    ctrl = CtrlInfo()
    self.acceSpdCtrl_u_ctrl.setPid(spd_exp, self.flightData.Vc)
    ctrl.dwZpos = self.acceSpdCtrl_u_ctrl.update()
    ctrl.dwXpos = self.thetaCtrl(theta_exp).dwXpos
    return ctrl

def oilCtrl(self, spd_exp):
    # 油门控制速度
    ctrl = CtrlInfo()
    self.acceSpdCtrl_u_ctrl.setPid(spd_exp, self.flightData.Vc)
    ctrl.dwZpos = self.acceSpdCtrl_u_ctrl.update()
    return ctrl

def psiCtrl(self, psi_ctrl, alt_exp, spd_exp):
    # 偏航角控制
    ctrl = CtrlInfo()
    self.psiCtrl_psi_roll.setPid(psi_ctrl, self.flightData.psi)
    roll_exp = self.psiCtrl_psi_roll.update()
    ctrl.dwYpos = self.rollCtrl(roll_exp).dwYpos
    ctrl.dwRpos = self.slipCtrl(0).dwRpos
    ctrl_ = self.altiCtrl(alt_exp, spd_exp)
    ctrl.dwXpos = ctrl_.dwXpos
    ctrl.dwZpos = ctrl_.dwZpos
    return ctrl

def rasCtrl(self, roll_exp, alt_exp, spd_exp):
    ctrl = CtrlInfo()
    ctrl.dwYpos = self.rollCtrl(roll_exp).dwYpos
    ctrl.dwRpos = self.slipCtrl(0).dwRpos
    ctrl_ = self.altiCtrl(alt_exp, spd_exp)
    ctrl.dwXpos = ctrl_.dwXpos
    ctrl.dwZpos = ctrl_.dwZpos
    return ctrl


训练滚转角
输入：obs 误差 倒数 积分
