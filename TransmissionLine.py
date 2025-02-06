import numpy as np
import pandas as pd
from Conductor import Conductor
from Bundle import Bundle
from Geometry import Geometry
from Bus import Bus

class TransmissionLine:

    z_base = 230**2/100

    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length

        self.e_nought=8.85*10**-12 #value of e nought
        self.r = self.bundle.conductor.resistance/self.bundle.num_conductors #obtain resistance of line, assuming ohms/mile

        self.deq=self.geometry.Find_DEQ() #obtain the DEQ (geometric mean distance, or GMD) of the transmission line
        self.dsc=self.bundle.DSC #obtain dsc
        self.dsl=self.bundle.DSL #obtain dsl

        self.L=0 #initialize distributed inductance as zero
        self.C=0 #initialize distributed capacitance as zero

        self.impedance=self.calc_impedance() * self.length # get value of impedance in ohms
        self.admittance=self.calc_admittance() * self.length # get value of admittance in siemens

        self.y_matrix = self.calc_y_matrix() # automatically creating the admittance matrix

    def calc_impedance(self): #z'=R'+jwL'
        self.L=(2*(10**-7))*np.log(self.deq/self.dsl) #calculate distributed inductance in ohms/meter
        return self.r + 1j*2*np.pi*60*self.L*1609 #calcualte distributed impedance, converting to ohms/miles

    def calc_admittance(self):
        self.C=(2*np.pi*self.e_nought)/(np.log((self.deq/self.dsc))) #calculate distributed capacitance in siemens/meter
        return 1j*2*np.pi*60*self.C*1609 #return distributed admittance converted to siemens/miles, conductance omitted

    def calc_y_matrix(self):
        y_matrix = np.zeros((2,2), dtype=complex) # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0,0] = self.admittance
        y_matrix[0,1] = -self.admittance
        y_matrix[1,0] = -self.admittance
        y_matrix[1,1] = self.admittance
        return y_matrix