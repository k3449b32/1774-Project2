import numpy as np
import pandas as pd

class Conductor:

    def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        self.name = name
        self.diam = diam
        self.GMR = GMR
        self.resistance = resistance
        self.ampacity = ampacity
        self.radius = diam/24