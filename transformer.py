import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings

class Transformer:
    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float, connection_type: str, z_ground: float, is_grounded: str):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.connection_type = connection_type
        self.is_grounded = is_grounded

        # Base impedance and admittance
        self.zseries = self.calc_impedance()
        self.yseries = self.calc_admittance()
        self.y_matrix = self.calc_y_matrix()

        # Sequence impedances
        self.positive_z = self.zseries
        self.negative_z = self.zseries

        if self.is_grounded == "no":
            self.z_ground = 1j * 0.0
            self.zero_z = None
            self.zero_y = 0
        else:
            self.z_ground = 1j * z_ground * (Settings.base_power / self.power_rating)
            self.zero_z = self.zseries + 3 * self.z_ground
            self.zero_y = 1 / self.zero_z

        # Sequence admittances
        self.positive_y = 1 / self.positive_z
        self.negative_y = 1 / self.negative_z

        # Yprim Matrices
        self.negative_yprim = self.y_matrix  # negative-sequence same as positive
        self.zero_yprim = self.create_zero_yprim()

    def calc_impedance(self):
        zpu = self.impedance_percent / 100 * np.exp(1j * np.arctan(self.x_over_r_ratio)) * Settings.base_power / self.power_rating
        return zpu

    def calc_admittance(self):
        return 1 / self.zseries

    def calc_y_matrix(self):
        y_matrix = np.zeros((2, 2), dtype=complex)
        y_matrix[0, 0] = self.yseries
        y_matrix[0, 1] = -self.yseries
        y_matrix[1, 0] = -self.yseries
        y_matrix[1, 1] = self.yseries
        return pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name], columns=[self.bus1.name, self.bus2.name])

    def create_zero_yprim(self):
        yprim_zero = np.zeros((2, 2), dtype=complex)

        if self.connection_type == 'y-y':
            yprim_zero[0, 0] = self.zero_y
            yprim_zero[0, 1] = -self.zero_y
            yprim_zero[1, 0] = -self.zero_y
            yprim_zero[1, 1] = self.zero_y

        elif self.connection_type == 'y-delta':
            yprim_zero[0, 0] = self.zero_y
            # Delta side blocks zero-sequence flow
            yprim_zero[1, 0] = 0
            yprim_zero[0, 1] = 0
            yprim_zero[1, 1] = 0

        elif self.connection_type == 'delta-y':
            # Delta side blocks zero-sequence flow
            yprim_zero[0, 0] = 0
            yprim_zero[1, 0] = 0
            yprim_zero[0, 1] = 0
            yprim_zero[1, 1] = self.zero_y

        elif self.connection_type == 'delta-delta':
            # Fully blocks zero-sequence
            yprim_zero[:, :] = 0

        else:
            raise ValueError("Invalid transformer connection type")

        return pd.DataFrame(yprim_zero, index=[self.bus1.name, self.bus2.name],
                            columns=[self.bus1.name, self.bus2.name])
