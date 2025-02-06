import numpy as np
import pandas as pd
from Conductor import Conductor

class Bundle:

    def __init__(self, name: str, num_conductors: float, spacing: float, conductor: Conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing #converting to feet for calculations below
        self.conductor = conductor
        # Automatically calling the method to calculate DSC and DSL
        self.DSC, self.DSL = self.calc_dsl_dsc()

    def calc_dsl_dsc(self):
        if self.num_conductors == 1:
            return self.conductor.radius, self.conductor.GMR
        elif self.num_conductors == 2:
            DSL = np.sqrt(self.conductor.GMR * self.spacing)
            DSC = np.sqrt(self.conductor.radius * self.spacing)
        elif self.num_conductors == 3:
            DSL = np.cbrt(self.conductor.GMR * (self.spacing ** 2))
            DSC = np.cbrt(self.conductor.radius * self.spacing ** 2)
        elif self.num_conductors == 4:
            DSL = (1.091 * (self.conductor.GMR * self.spacing ** 3) ** (1 / 4))
            DSC = (1.091 * ((self.conductor.radius) * self.spacing ** 3) ** (1 / 4))
        else:
            raise ValueError("Unsupported number of conductors.")
        return DSL, DSC