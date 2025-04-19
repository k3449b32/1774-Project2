import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings

class Transformer:


    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float,connection_type,z_ground):
        #connection types are y-y, y-delta, delta-y, delta-delta
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.zseries = self.calc_impedance()
        self.yseries = self.calc_admittance()
        self.y_matrix = self.calc_y_matrix()
        self.z_ground=z_ground
        self.positive_z = self.zseries
        self.negative_z = self.zseries
        self.zero_z = 3*self.z_ground+self.zseries

        self.positive_y=1/self.positive_z
        self.negative_y=1/self.negative_z
        self.zero_y=1/self.zero_z
        self.y_ground = 1/self.z_ground

        self.connection_type=connection_type


        #calculate zero, positive, and negative sequence yprim
        #the positive and negative y_prim are the same as the power flow yprim
        self.zero_yprim=self.zero_yprim()
        self.positive_yprim = self.y_matrix
        self.negative_yprim = self.y_matrix

    def calc_impedance(self): #method to calculate impedance
        zpu = self.impedance_percent/100 * np.exp(1j * np.atan(self.x_over_r_ratio)) * Settings.base_power/self.power_rating
        return zpu

    def calc_admittance(self): #method to calculate admittance
        return 1/self.zseries

    def calc_y_matrix(self):
        y_matrix = np.zeros((2,2), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = self.yseries
        y_matrix[0,1] = -self.yseries
        y_matrix[1,0] = -self.yseries
        y_matrix[1,1] = self.yseries
        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name], columns=[self.bus1.name, self.bus2.name])

        return df_y_matrix

    def zero_yprim(self):
        yprim_zero = np.zeros((2,2), dtype=complex)
        if(self.connection_type == 'y-y'):
            yprim_zero[0, 0] = self.zero_y
            yprim_zero[0, 1] = -self.zero_y
            yprim_zero[1, 0] = -self.zero_y
            yprim_zero[1, 1] = self.zero_y

        if(self.connection_type == 'y-delta'):
            yprim_zero[0, 0] = self.y_ground
            yprim_zero[0, 1] = 0
            yprim_zero[1, 0] = 0
            yprim_zero[1, 1] = 0

        if(self.connection_type == 'delta_y'):
            yprim_zero[0, 0] = 0
            yprim_zero[0, 1] = 0
            yprim_zero[1, 0] = 0
            yprim_zero[1, 1] = self.y_ground

        if (self.connection_type == 'delta_delta'):
            yprim_zero[0, 0] = 0
            yprim_zero[0, 1] = 0
            yprim_zero[1, 0] = 0
            yprim_zero[1, 1] = 0

        else:
            raise ValueError("Invalid transformer connection type")


