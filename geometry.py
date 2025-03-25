import numpy as np
import pandas as pd

class Geometry: #calculates the DEQ, based on geometric parameters entered by the user

    def __init__(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        self.name = name
        self.xa = xa
        self.ya = ya
        self.xb = xb
        self.yb = yb
        self.xc = xc
        self.yc = yc
        self.DEQ = self.calc_deq()

    def calc_deq(self):

        def calculate_distance(x1, y1, x2, y2):
            return np.sqrt((y1 - y2) ** 2 + (x1 - x2) ** 2)

        Dab = calculate_distance(self.xa, self.ya, self.xb, self.yb)
        Dbc = calculate_distance(self.xb, self.yb, self.xc, self.yc)
        Dac = calculate_distance(self.xa, self.ya, self.xc, self.yc)

        # Using the distances between conductors to calculate DEQ then returning the value
        DEQ = np.cbrt(Dab * Dbc * Dac)
        return DEQ