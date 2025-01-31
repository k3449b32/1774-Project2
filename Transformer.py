import numpy as np
import pandas as pd
from Bus import Bus

class Transformer:

    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.impedance = self.calc_impedance()
        self.admittance = self.calc_admittance()

    def calc_impedance(self): #method to calculate impedance
        return (self.impedance_percent/100)*np.exp(1j*np.atan(self.x_over_r_ratio))

    def calc_admittance(self): #method to calculate admittance
        return 1/self.impedance

    def calc_yprim(self): #method to calculate admittance matrix
        pass