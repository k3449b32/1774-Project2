import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings

class Shunt_inductor:
    def __init__(self, name: str,bus: Bus,L: float):
        self.name = name
        self.bus = bus
        self.L = L
        self.w = 2*np.pi*Settings.frequency
        self.z = self.calc_impedance()

    def calc_impedance(self): #calculates impedance based frequency and inductance, returns in PU
        z=1j*self.w*self.L
        return z