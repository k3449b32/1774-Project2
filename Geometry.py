import numpy as np
import pandas as pd

class Geometry:

    def __init__(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        self.name = name
        self.xa = xa
        self.ya = ya
        self.xb = xb
        self.yb = yb
        self.xc = xc
        self.yc = yc
        self.DEQ = self.Find_DEQ()

    def Find_DEQ(self):
        DEQ = 0
        return DEQ
