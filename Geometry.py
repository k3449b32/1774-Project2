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

        # Initializing distances between conductors
        Dab = 0
        Dbc = 0
        Dac = 0

        # Calculating the distances between conductors
        if self.xa == self.xb:
            Dab = abs(self.xa - self.xb)
        if self.ya == self.yb:
            Dab = abs(self.ya - self.yb)
        else:
            Dab = ((self.ya - self.yb)**2 + (self.xa - self.xb)**2) ** (1/2)

        if self.xb == self.xc:
            Dbc = abs(self.xb - self.xc)
        if self.yb == self.yc:
            Dbc = abs(self.yb - self.yc)
        else:
            Dbc = ((self.yb - self.yc)**2 + (self.xb - self.xc)**2) ** (1/2)

        if self.xa == self.xc:
            Dac = abs(self.xa - self.xc)
        if self.ya == self.yb:
            Dac = abs(self.ya - self.yc)
        else:
            Dac = ((self.ya - self.yc)**2 + (self.xa - self.xc)**2) ** (1/2)

        # Using the distances between conductors to calculate DEQ then returning the value
        DEQ = (Dab * Dbc * Dac) ** (1 / 3)
        return DEQ
