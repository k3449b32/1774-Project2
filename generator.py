import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings
#initialize a generator object
class Generator:

    def __init__(self, name: str, bus: Bus, mw_setpoint: float, voltage_setpoint: float,subtransient_x: float,x_zero: float, x_negative: float, ground_z: float, is_grounded: str):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.subtransient_x=1j*subtransient_x*(Settings.base_power/self.mw_setpoint) #change the base of the subtransient reactance
            #subtransient is also positive sequence admittance??????
        self.sub_admittance=1/self.subtransient_x #
        self.ground_status = is_grounded


        self.ground_z = ground_z

        self.x_zero = (1j*x_zero*+3*1j*ground_z)*(Settings.base_power/self.mw_setpoint) #initialize values for zero and negative sequence impedance
        self.x_negative = 1j*x_negative*(Settings.base_power/self.mw_setpoint)
#!!!!!!!!!!! is ground impedance multiplied by 1j???????????????

        if self.ground_status == 'no': #if generator is not grounded, y is 0
            self.y_zero = 0
        else:
            self.y_zero = 1 / x_zero

        self.y_negative = 1/x_negative



        self.zero_yprim = self.calc_y_matrix(self.y_zero)
        self.negative_yprim = self.calc_y_matrix(self.y_negative)
        #is there a positive sequence yprim??!?


    def calc_y_matrix(self,y):
        y_matrix = np.zeros((2,2), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = y
        y_matrix[0,1] = -y
        y_matrix[1,0] = -y
        y_matrix[1,1] = y
        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus.name, self.bus2.name], columns=[self.bus1.name, self.bus2.name])
        return df_y_matrix

#how to build y_prim matrix!!!!??!!