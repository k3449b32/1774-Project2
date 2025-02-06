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
        self.y_matrix = self.calc_y_matrix()

    def calc_impedance(self): #method to calculate impedance
        return (self.impedance_percent/100)*np.exp(1j*np.atan(self.x_over_r_ratio))

    def calc_admittance(self): #method to calculate admittance
        return 0

    def calc_yprim(self): #method to calculate admittance matrix
        pass

    def calc_y_matrix(self):
        y_matrix = np.zeros((2,2), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = self.admittance
        y_matrix[0,1] = -self.admittance
        y_matrix[1,0] = -self.admittance
        y_matrix[1,1] = self.admittance
        return y_matrix

