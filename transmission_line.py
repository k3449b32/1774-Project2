import numpy as np
import pandas as pd
from conductor import Conductor
from bundle import Bundle
from geometry import Geometry
from bus import Bus
import config

class TransmissionLine:
    f = config.frequency  # obtain the frequency from config.py


    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length

        z_base = self.bus1.base_kv ** 2 / config.power_base #calculate the z_base, IDK how to get the voltage

        self.e_nought = 8.85*10**-12 #value of e nought
        self.r = self.bundle.conductor.resistance/self.bundle.num_conductors #obtain resistance of line, assuming ohms/mile

        self.impedance_pu = self.calc_impedance() / z_base # get value of impedance in ohms
        self.shunt_admittance = self.calc_admittance()*z_base # get value of admittance in siemens
        self.series_admittance = 1/self.impedance_pu
        self.y_matrix = self.calc_y_matrix() # automatically creating the admittance matrix

    def calc_impedance(self): #z'=R'+jwL'
        L = (2*(10**-7))*np.log(self.geometry.DEQ / self.bundle.DSL) #calculate distributed inductance in Henrys/meter
        return (self.r + 1j*2*np.pi*TransmissionLine.f*L*1609) * self.length #calcualte distributed impedance, converting to ohms/miles

    def calc_admittance(self):
        C = (2*np.pi*self.e_nought)/(np.log((self.geometry.DEQ / self.bundle.DSC))) #calculate distributed capacitance in Farads/meter
        return 1j*2*np.pi*TransmissionLine.f*C*1609 * self.length #return distributed admittance converted to siemens/miles, conductance omitted

    def calc_y_matrix(self):
        y_matrix = np.zeros((2,2), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = self.shunt_admittance / 2 + self.series_admittance
        y_matrix[0,1] = -self.series_admittance
        y_matrix[1,0] = -self.series_admittance
        y_matrix[1,1] = self.shunt_admittance / 2 + self.series_admittance
        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name], columns=[self.bus1.name, self.bus2.name])

        return df_y_matrix