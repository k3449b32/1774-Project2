import numpy as np
import pandas as pd
from geometry import Geometry
from bus import Bus
from transmission_line import TransmissionLine
from bundle import Bundle
from transformer import Transformer
from conductor import Conductor
from generator import Generator
from load import Load

class Circuit:

    def __init__(self, name: str):
        self.name = name
        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometry = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}
        self.ybus = None
        self.first_gen = False
        self.bus_order = []
        self.real_power = {}
        self.reactive_power = {}
        self.voltages = {}
        self.angles = {}

    def add_bus(self, name: str, bus_kv: float):
        if name in self.buses:
            raise ValueError("Bus is already in circuit")
        else:
            self.buses[name] = Bus(name, bus_kv)
            self.bus_order.append(name)

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

    def add_load_element(self, name: str, bus: str, real_power: float, reactive_power: float):
        if name in self.loads:
            raise ValueError("Load is already in circuit")
        else:
            self.loads[name] = Load(name, self.buses[bus], real_power, reactive_power)
            self.real_power[bus] -= real_power
            self.reactive_power[bus] -= reactive_power
        self.calc_ybus()


    def add_generator_element(self, name: str, bus: str, real_power: float, per_unit_voltage: float):
        if name in self.generators:
            raise ValueError("Generator is already in circuit")
        self.generators[name] = Generator(name, self.buses[bus], real_power, per_unit_voltage)
        self.real_power[bus] += real_power
        # If there is no generator made the first generator is a slack generator and the boolean variable changes
        if not self.first_gen:
            self.first_gen = True
            self.buses[bus] = 'slack'
        # If there already is a generator in the circuit then the next generator is created as PV
        else:
            self.buses[bus] = 'PV'
        self.calc_ybus()

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

        # Making sure it shows all of the rows and columns properly
        pd.set_option('display.max_rows', None)  # No limit to the number of rows displayed
        pd.set_option('display.max_columns', None)  # No limit to the number of columns displayed
        pd.set_option('display.width', None)  # No width limit (adjust to your console's width)
        pd.set_option('display.max_colwidth', None)  # No limit to the column width
        self.ybus = self.ybus.round(2)

    def get_voltages(self, buses, bus_name):
        if bus_name not in buses:
            raise KeyError(f"Bus '{bus_name}' not found in the buses dictionary.")

        bus_obj = buses[bus_name]  # Get the bus object
        v = bus_obj.V  # Retrieve voltage magnitude
        delta = bus_obj.delta  # Retrieve voltage angle

        return [v, delta]

    def compute_power_injection(self,buses, ybus):
        #this function takes in buses, ybus (the adimittance matrix)
        bus=buses

        for bus_name in bus:  # Iterate through bus names (keys of the dictionary)
            [v, delta] = self.get_voltages(bus, bus_name)  # Pass bus name instead of index

        P = np.zeros(Bus.counter)  # store real power injection for each bus
        Q = np.zeros(Bus.counter)  # store reactive power injection for each bus

        yabs=ybus.np.abs() #a matrix containing the absolute value of the elements in the ybus matrix
        ydelta=ybus.np.angle() #get the angles of the ybus matrix

        for k in range(Bus.counter): #iterate through each bus k
            for n in range(Bus.counter): #iterate through the mutual admittances between bus k and each bus n
                P[k]=P[k]+v[k]*yabs.iloc[k,n]*v[n]*np.cos(delta[k]-delta[n]-ydelta.iloc[k,n]) #find p injection
                Q[k]=Q[k]+v[k]*yabs.iloc[k,n]*v[n]*np.sin(delta[k]-delta[n]-ydelta.iloc[k,n]) #find q injection

        print(P)
        print(Q)
        return P, Q #return power injection matrices

    def compute_power_mismatch(self, buses, ybus):
        # Get power injections
        P_calc, Q_calc = self.compute_power_injection(buses, ybus)

        # Initialize mismatch vectors
        delta_P = np.zeros(len(buses))
        delta_Q = np.zeros(len(buses))

        for i, bus_name in enumerate(self.bus_order):
            bus = self.buses[bus_name]

            if bus.bus_type == "slack":
                # Slack bus has no power mismatch
                continue

            # Real power mismatch for all non-slack buses
            delta_P[i] = self.real_power[bus_name] - P_calc[i]

            if bus.bus_type == "PQ":
                # Reactive power mismatch only for PQ buses
                delta_Q[i] = self.reactive_power[bus_name] - Q_calc[i]

        # Concatenate mismatch vectors for numerical solution
        mismatch_vector = np.concatenate((delta_P, delta_Q))

        return mismatch_vector