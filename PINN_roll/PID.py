import sys



class PID:
    def __init__(self, m_kp=0, m_ki=0, m_kd=0, m_dt=1):
        self.kp = m_kp
        self.ki = m_ki
        self.kd = m_kd
        self.dt = m_dt

        self.integral = 0
        self.itag = True
        self.out = 0

        # Physical limits
        self.low_limit = -sys.float_info.max
        self.high_limit = sys.float_info.max

        # Derivative parameters
        self.preerror = 0
        self.alpha = 0

        self.setPoint = 0.0
        self.value = 0.0

    def setLimits(self, low, high):
        self.low_limit = low
        self.high_limit = high

    def setFilter(self, m_alpha):
        self.alpha = m_alpha

    def setPid(self, m_setPoint, m_value):
        self.setPoint = m_setPoint
        self.value = m_value

    def setParam(self, m_kp, m_ki, m_kd, m_dt):
        self.kp = m_kp
        self.ki = m_ki
        self.kd = m_kd
        self.dt = m_dt

    def update(self):
        error = self.setPoint - self.value
        P = self.getP(error)
        I = self.getI(error)
        D = self.getD(error)
        self.out = P + I + D
        adjustedOut = self.adjustedOut(self.out)
        return adjustedOut

    def getP(self, error):
        return self.kp * error

    def getI(self, error):
        self.setITag(error)
        if self.itag:
            self.integral += self.ki * error * self.dt
        return self.integral

    def getD(self, error):
        filtered_D = 0.0
        tmp = self.kd * (error - self.preerror) / self.dt
        self.preerror = error
        # Add low-pass filter
        filtered_D = self.alpha * filtered_D + (1 - self.alpha) * tmp
        return filtered_D

    def adjustedOut(self, m_out):
        if m_out > self.high_limit:
            return self.high_limit
        elif m_out < self.low_limit:
            return self.low_limit
        else:
            return m_out

    def setITag(self, error):
        if self.out > self.high_limit or self.out < self.low_limit:
            if (error > 0 and self.out > 0) or (error < 0 and self.out < 0):
                self.itag = False
                return
        self.itag = True

    def reset(self):
        self.integral = 0
        self.itag = True
        self.preerror = 0
        self.alpha = 0

