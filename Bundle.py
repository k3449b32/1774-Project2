import numpy as np
import pandas as pd
from Conductor import Conductor

class Bundle:

    def __init__(self, name: str, num_conductors: float, spacing: float, conductor: Conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC = 0
        self.DSL = 0
        # Automatically calling the method to calculate DSC and DSL
        self.Find_DSL_DSC()

    def Find_DSL_DSC(self):
        #calculate Dsl and Dsc according to number of conductors, divide all values by 3.28 to convert from feet to meters
        if self.num_conductors == 1:
            self.DSC = self.conductor.diam/2/3.28
            self.DSL = self.conductor.GMR/3.28

        if self.num_conductors == 2:
            self.DSL = np.sqrt(self.conductor.GMR * self.spacing)/3.28
            self.DSC = np.sqrt((self.conductor.diam/2) * self.spacing)/3.28

        if self.num_conductors == 3:
            self.DSL = np.cbrt(self.conductor.GMR * (self.spacing ** 2))/3.28
            self.DSC = np.cbrt((self.conductor.diam/2) * self.spacing ** 2)/3.28

        if self.num_conductors == 4:
            self.DSL = (1.091 * (self.conductor.GMR * self.spacing ** 3) ** (1/4))/3.28
            self.DSC = (1.091*((self.conductor.diam / 2) * self.spacing ** 3) ** (1/4))/3.28