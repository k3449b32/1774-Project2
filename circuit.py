import numpy as np
import pandas as pd
from geometry import Geometry
from bus import Bus
from transmission_line import TransmissionLine
from bundle import Bundle
from transformer import Transformer
from conductor import Conductor

class Circuit:

    def __init__(self, name: str):
        self.name = name
        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometry = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.ybus = None

    def add_bus(self, name: str, bus_kv: float):
        if name in self.buses:
            raise ValueError("Bus is already in circuit")
        else:
            self.buses[name] = Bus(name, bus_kv)

    def add_conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        if name in self.conductors:
            raise ValueError("Conductor is already in circuit")
        else:
            self.conductors[name] = Conductor(name, diam, GMR, resistance, ampacity)

    def add_bundle(self, name: str, num_conductors: float, spacing: float, conductor: str):
        if name in self.bundles:
            raise ValueError("Bundle is already in circuit")
        else:
            self.bundles[name] = Bundle(name, num_conductors, spacing, self.conductors[conductor])

    def add_geometry(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        if name in self.geometry:
            raise ValueError("Geometry is already in circuit")
        else:
            self.geometry[name] = Geometry(name, xa, ya, xb, yb, xc, yc)

    def add_transformer(self, name: str, bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        if name in self.transformers:
            raise ValueError("Transformer is already in circuit")
        else:
            self.transformers[name] = Transformer(name, self.buses[bus1], self.buses[bus2], power_rating, impedance_percent, x_over_r_ratio)

    def add_transmission_line(self, name: str, bus1: str, bus2: str, bundle: str, geometry: str, length: float):
        if name in self.transmission_lines:
            raise ValueError("Transmission Line is already in circuit")
        else:
            self.transmission_lines[name] = TransmissionLine(name, self.buses[bus1], self.buses[bus2], self.bundles[bundle], self.geometry[geometry], length)

    def calc_ybus(self):
        # Step 1: Initialize the Ybus matrix as a zero matrix with dimensions N x N
        N = len(self.buses)  # Number of buses
        self.ybus = np.zeros((N, N), dtype=complex)

        # Step 2: Create a dictionary to map bus names to indices for easier reference
        bus_indices = {bus_name: idx for idx, bus_name in enumerate(self.buses)}

        # Step 3: Iterate through all transmission lines
        for line in self.transmission_lines.values():
            Yprim = line.y_matrix  # Get the primitive admittance matrix
            bus1_idx = bus_indices[line.bus1.name]
            bus2_idx = bus_indices[line.bus2.name]

            # Add the elements of the Yprim matrix into the Ybus matrix
            self.ybus[bus1_idx, bus1_idx] += Yprim.iloc[0, 0]  # Self-admittance for bus1
            self.ybus[bus1_idx, bus2_idx] += Yprim.iloc[0, 1]  # Mutual admittance between bus1 and bus2
            self.ybus[bus2_idx, bus1_idx] += Yprim.iloc[1, 0]  # Mutual admittance between bus2 and bus1
            self.ybus[bus2_idx, bus2_idx] += Yprim.iloc[1, 1]  # Self-admittance for bus2

        # Step 4: Iterate through all transformers
        for transformer in self.transformers.values():
            Yprim = transformer.y_matrix  # Get the primitive admittance matrix
            bus1_idx = bus_indices[transformer.bus1.name]
            bus2_idx = bus_indices[transformer.bus2.name]

            # Add the elements of the Yprim matrix into the Ybus matrix
            self.ybus[bus1_idx, bus1_idx] += Yprim.iloc[0, 0]  # Self-admittance for bus1
            self.ybus[bus1_idx, bus2_idx] += Yprim.iloc[0, 1]  # Mutual admittance between bus1 and bus2
            self.ybus[bus2_idx, bus1_idx] += Yprim.iloc[1, 0]  # Mutual admittance between bus2 and bus1
            self.ybus[bus2_idx, bus2_idx] += Yprim.iloc[1, 1]  # Self-admittance for bus2

        # Step 5: Numerical stability check (ensure no singularities)
        if np.any(np.diag(self.ybus) == 0):  # If any diagonal element is zero, it indicates a singularity
            raise ValueError("Ybus matrix has a singularity (zero diagonal entry). Please check bus connections.")

        # Step 6: Convert Ybus into a pandas DataFrame with bus names as row and column indices
        self.ybus = pd.DataFrame(self.ybus, index=self.buses.keys(), columns=self.buses.keys())

        # Now, the Ybus is stored as a pandas DataFrame with proper bus names

        # Making sure it shows all of the rows and columns
        pd.set_option('display.max_rows', None)  # No limit to the number of rows displayed
        pd.set_option('display.max_columns', None)  # No limit to the number of columns displayed
        pd.set_option('display.width', None)  # No width limit (adjust to your console's width)
        pd.set_option('display.max_colwidth', None)  # No limit to the column width