import numpy as np
import pandas as pd
from Conductor import Conductor
from Bundle import Bundle
from Geometry import Geometry
from Bus import Bus

class TransmissionLine:

    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length

        self.e_nought=8.85*10**-12 #value of e nought
        self.r = self.bundle.conductor.resistance/self.bundle.num_conductors #obtain resistance of line, do not know if in ohms/mi or ohms/ft

        self.deq=self.geometry.Find_DEQ() #obtain the DEQ (geometric mean distance, or GMD) of the transmission line
        self.dsc=self.bundle.DSC #obtain dsc
        self.dsl=self.bundle.DSL #obtain dsl

        self.L=0 #initialize distributed inductance as zero
        self.C=0 #initialize distributed capacitance as zero

        self.impedance=self.calc_impedance() #get value of impedance
        self.admittance=self.calc_admittance() #get value of admittance

    def calc_impedance(self): #z'=R'+jwL'
        self.L=(2*(10**-7))*np.log(self.deq/self.dsl) #calculate distributed inductance in ohms/meter
        return self.r+1j*2*np.pi*60*self.L*3.28 #calcualte distributed impedance, multiplied by 3.28 ft to convert from ohms/meter to ohms/feet
    def calc_admittance(self):
        self.C=(2*np.pi*self.e_nought)/(np.log((self.deq/self.dsc))) #calculate distributed capacitance in ohms/meter
        return 2*np.pi*self.C*3.28 #return distributed admittance converted to ohms/feet, conductance omitted