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