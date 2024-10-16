from algorithm.ABSM.lowAgent_ABSM import AltitudeController


class HighAgent_ABSM:
    def __init__(self):
        self.lowAgent_ABSM = AltitudeController()
        self.alt_need_climb = 100

    def action_climb(self, self_aircraft, enemy_aircraft):
        self_aircraft, enemy_aircraft = self_aircraft, enemy_aircraft

        # 每次做决策前，记得更新本机数据
        pre_alt = self.lowAgent_ABSM.flightData.altitude
        self.lowAgent_ABSM.updateFlightData(self_aircraft)  # 更新数据
        cur_alt = self.lowAgent_ABSM.flightData.altitude

        if pre_alt == 0:
            self.alt_need_climb = 100
            alt_exp = cur_alt + 100
        else:
            self.alt_need_climb -= cur_alt - pre_alt
            alt_exp = cur_alt + self.alt_need_climb
        m_ctrl = self.lowAgent_ABSM.climb(alt_exp, 200)

        # m_pidtrl = self.lowAgent_ABSM.autoDriver.altiCtrl(5000, 200)
        # m_rollCtrl = self.lowAgent_ABSM.autoDriver.rollCtrl(0)
        # m_pidtrl.dwYpos = m_rollCtrl.dwYpos

        return m_ctrl
