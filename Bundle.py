import numpy as np
import pandas as pd

class Bundle:

    def __init__(self, name: str, num_conductors: float, spacing: float, conductor: float):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC = 0
        self.DSL = 0

    def Find_DSL_DSC(self):
        self.DSC = 0
        self.DSL = 0