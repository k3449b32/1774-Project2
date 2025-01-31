import numpy as np

class Transformer:
    def __init__(self,name: str,bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        self.name=name
        self.bus1=bus1
        self.bus2=bus2
        self.power_rating=power_rating
        self.impedance_percent=impedance_percent
        self.x_over_r_ratio=x_over_r_ratio

        self.impedance=self.calc_impedance() #set value of PU impedance
        self.admittance=self.calc_admittance() #set the PU admittance

    def calc_impedance(self):
        # divide impedance_percent by 100 to get PU impedance, calculate phase angle
        return (self.impedance_percent/100)*np.exp(np.atan(self.x_over_r_ratio))


    def calc_admittance(self):
        return 1/self.impedance #find admittance, Y=1/Z

    def calc_impedance_matrix(self):
        pass
    def calc_admittance_matrix(self):
        pass

