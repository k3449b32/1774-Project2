import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings
#initialize a generator object
class Generator:
    #all impedance inputs are to be given in P.U.
    def __init__(self, name: str, bus: Bus, mw_setpoint: float, voltage_setpoint: float,subtransient_x: float,z_zero: float, z_negative: float, ground_z: float, is_grounded: str):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint


        self.subtransient_x=1j*subtransient_x*(Settings.base_power/self.mw_setpoint) #change the base of the subtransient reactance
            #subtransient is also positive sequence admittance??????
        self.sub_admittance=1/self.subtransient_x #
        self.ground_status = is_grounded


        self.ground_z = ground_z*(Settings.base_power/self.mw_setpoint)

        self.z_zero = (1j*z_zero)*(Settings.base_power/self.mw_setpoint) #initialize values for zero and negative sequence impedance
        self.z_negative = 1j*z_negative*(Settings.base_power/self.mw_setpoint)

        #the total zero sequence admittance is z_zero + 3 * grounding impedance
        self.z_zero_total = z_zero + 3*self.ground_z
#!!!!!!!!!!! is ground impedance multiplied by 1j???????????????

        if self.ground_status == 'no': #if generator is not grounded, y will be zero
            self.y_zero = 0
        else:
            self.y_zero = 1 / self.z_zero_total

        #calculate the negative sequence admittance
        self.y_negative = 1/self.z_negative



        self.zero_yprim = self.calc_y_matrix(self.y_zero)
        self.negative_yprim = self.calc_y_matrix(self.y_negative)
        #is there a positive sequence yprim??!?


    def calc_y_matrix(self,y):
        y_matrix = np.zeros((1,1), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = y

        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus.name], columns=[self.bus.name])
        return df_y_matrix

