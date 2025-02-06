import numpy as np
import pandas as pd
from Geometry import Geometry
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Transformer import Transformer
from Conductor import Conductor

class Circuit:

    def __init__(self, name: str):
        self.name = name
        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometry = {}
        self.transformers = {}
        self.transmissionlines = {}

    def add_Bus(self, name: str, bus_kv: float):
        self.buses[name] = Bus(name, bus_kv)

    def add_Conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        self.conductors[name] = Conductor(name, diam, GMR, resistance, ampacity)

    def add_Bundle(self, name: str, num_conductors: float, spacing: float, conductor: Conductor):
        self.bundles[name] = Bundle(name, num_conductors, spacing, conductor)

    def add_Geometry(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        self.geometry[name] = Geometry(name, xa, ya, xb, yb, xc, yc)

    def add_Transformer(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        self.transformers[name] = Transformer(name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio)

    def add_TransmissionLine(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        self.transmissionlines[name] = TransmissionLine(name, bus1, bus2, bundle, geometry, length)