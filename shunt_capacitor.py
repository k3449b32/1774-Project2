import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings

class Shunt_capacitor:
    def __init__(self, name: str,bus: Bus,mvar: float):
        self.name = name
        self. bus = bus
        self. mvar = mvar

        self.w = 2 * np.pi * Settings.frequency
        self.v_base = self.bus.base_kv
        self.s_base = Settings.base_power
        self.y_base = 1/(self.v_base ** 2 / self.s_base)


        self.y = self.calc_admittance()



    def calc_admittance(self):  # calculates impedance based frequency and inductance, returns in PU
        y = 1j*(self.mvar/self.v_base**2)
        y = y / self.y_base
        return y