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

        if self.num_conductors == 1:
            self.DSC = 0
            self.DSL = 0

        if self.num_conductors == 2:
            self.DSL = np.sqrt(self.conductor.GMR * (1 / 3.28))
            self.DSC = np.sqrt((self.conductor.diam/2) * 1.5)

        if self.num_conductors == 3:
            self.DSL = np.cbrt(self.conductor.GMR * ((1.5 / 3.28) ** 2))

        if self.num_conductors == 4:
            self.DSL = 1.091 * (((1.5 / 3.28) ** 3) * self.conductor.GMR) ** (1 / 4)