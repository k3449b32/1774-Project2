import numpy as np
import pandas as pd
from conductor import Conductor
from bundle import Bundle
from geometry import Geometry
from bus import Bus
from settings import Settings


class TransmissionLine:
    f = Settings.frequency  # obtain the frequency from settings.py

    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float,
                 is_grounded=True):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.is_grounded = is_grounded  # NEW: specifies whether this line contributes to zero-sequence path

        z_base = self.bus1.base_kv ** 2 / Settings.base_power  # calculate the z_base

        self.e_nought = 8.854 * 10 ** -12  # value of e nought
        self.r = self.bundle.conductor.resistance / self.bundle.num_conductors  # obtain resistance of line, assuming ohms/mile

        self.impedance_pu = self.calc_impedance() / z_base  # get value of impedance in ohms
        self.shunt_admittance = self.calc_admittance() * z_base  # get value of admittance in siemens
        self.series_admittance = 1 / self.impedance_pu
        self.y_matrix = self.calc_y_matrix()  # automatically creating the admittance matrix

        # define sequence impedances
        self.z_positive = self.impedance_pu
        self.z_negative = self.impedance_pu
        self.z_zero = 2.5 * self.impedance_pu if self.is_grounded else None  # grounded lines only

        # define sequence admittances
        self.y_positive = 1 / self.z_positive
        self.y_negative = 1 / self.z_negative
        self.y_zero = 1 / self.z_zero if self.is_grounded else 0

        # calculate yprim matrices for zero, positive, and negative sequences
        self.zero_yprim = self.calc_zero_yprim()  # positive and negative use y_matrix

    def calc_impedance(self):  # z'=R'+jwL'
        L = (2 * (10 ** -7)) * np.log(
            self.geometry.DEQ / self.bundle.DSL)  # calculate distributed inductance in Henrys/meter
        return (self.r + 1j * 2 * np.pi * Settings.frequency * L * 1609.34) * self.length  # convert to ohms/mile

    def calc_admittance(self):
        C = (2 * np.pi * self.e_nought) / (
            np.log((self.geometry.DEQ / self.bundle.DSC)))  # distributed capacitance in Farads/meter
        return (
                    1j * 2 * np.pi * Settings.frequency * C * 1609.34) * self.length  # convert to siemens/mile, conductance omitted

    def calc_y_matrix(self):
        y_matrix = np.zeros((2, 2), dtype=complex)  # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0, 0] = self.shunt_admittance / 2 + self.series_admittance
        y_matrix[0, 1] = -self.series_admittance
        y_matrix[1, 0] = -self.series_admittance
        y_matrix[1, 1] = self.shunt_admittance / 2 + self.series_admittance
        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name],
                                   columns=[self.bus1.name, self.bus2.name])

        return df_y_matrix

    def calc_zero_yprim(self):
        if not self.is_grounded:
            # zero-sequence current cannot flow through ungrounded lines
            return pd.DataFrame(np.zeros((2, 2), dtype=complex), index=[self.bus1.name, self.bus2.name],
                                columns=[self.bus1.name, self.bus2.name])

        y_matrix = np.zeros((2, 2), dtype=complex)  # initializing a 2x2 matrix of zeros
        # creating admittance matrix (will need editing in future for the unknown admittances the buses connect to)
        y_matrix[0, 0] = self.y_zero
        y_matrix[0, 1] = -self.y_zero
        y_matrix[1, 0] = -self.y_zero
        y_matrix[1, 1] = self.y_zero
        # Create DataFrame with custom indices and columns
        df_y_matrix = pd.DataFrame(y_matrix, index=[self.bus1.name, self.bus2.name],
                                   columns=[self.bus1.name, self.bus2.name])
        return df_y_matrix
