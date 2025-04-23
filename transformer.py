import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings

import numpy as np
import pandas as pd
from settings import Settings  # assumes you're importing your global settings

class Transformer:
    def __init__(self, name: str, bus1, bus2, power_rating: float,
                 impedance_percent: float, x_over_r_ratio: float,
                 connection_type="Y-Y", grounding_impedance=0.0):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.connection_type = connection_type
        self.grounding_impedance = grounding_impedance  # in ohms, default is solid ground

        self.zseries = self.calc_impedance()            # Series impedance in p.u.
        self.yseries = 1 / self.zseries if self.zseries != 0 else 0  # Admittance in p.u.

        self.y_matrix = self.calc_y_matrix()  # Default Y matrix (positive-sequence)

    def calc_impedance(self):
        # Convert percent impedance to p.u. and scale to base power
        z_pu = (self.impedance_percent / 100) * np.exp(1j * np.arctan(self.x_over_r_ratio))
        return z_pu * Settings.base_power / self.power_rating

    def y_prim(self, sequence):
        """
        Returns the sequence admittance for this transformer.
        Only allows zero-sequence flow if windings are grounded.
        """
        if sequence in ["positive", "negative"]:
            return self.yseries

        elif sequence == "zero":
            if "Y" in self.connection_type:
                if self.grounding_impedance == 0.0:
                    return self.yseries  # solidly grounded Y connection
                else:
                    z_grounded = self.zseries + 1j * self.grounding_impedance * Settings.base_power / self.power_rating
                    return 1 / z_grounded if z_grounded != 0 else 0
            else:
                return 0  # Δ connections block zero-sequence
        else:
            raise ValueError("Invalid sequence type")

    def calc_y_matrix(self):
        """ Default positive-sequence admittance matrix """
        y = self.y_prim("positive")

        y_matrix = np.zeros((2, 2), dtype=complex)
        y_matrix[0, 0] = y
        y_matrix[1, 1] = y
        y_matrix[0, 1] = -y
        y_matrix[1, 0] = -y

        return pd.DataFrame(y_matrix,
                            index=[self.bus1.name, self.bus2.name],
                            columns=[self.bus1.name, self.bus2.name])


