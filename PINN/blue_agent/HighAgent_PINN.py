from PINN.blue_agent.LowAgent_PINN import LowAgent_PINN


class HighAgent_PINN:
    def __init__(self):
        self.lowAgent = LowAgent_PINN()

    def action_feizhixian(self, self_aircraft, enemy_aircraft):
        self.lowAgent.updateFlightData(self_aircraft)  # 更新PID的数据
        m_pidCtrl = self.lowAgent.autoDriver.altiCtrl(5000, 200)
        m_rollCtrl = self.lowAgent.autoDriver.rollCtrl(20)
        m_pidCtrl.dwYpos = m_rollCtrl.dwYpos

        return m_pidCtrl




