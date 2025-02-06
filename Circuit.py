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
        bus = Bus(name, bus_kv)
        self.buses[bus.name] = bus

    def add_Conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        conductor = Conductor(name, diam, GMR, resistance, ampacity)
        self.conductors[conductor.name] = conductor

    def add_Bundle(self, name: str, num_conductors: float, spacing: float, conductor: Conductor):
        bundle = Bundle(name, num_conductors, spacing, conductor)
        self.bundles[bundle.name] = bundle

    def add_Geometry(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        geometry = Geometry(name, xa, ya, xb, yb, xc, yc)
        self.geometry[geometry.name] = geometry

    def add_Transformer(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        transformer = Transformer(name, bus1,bus2, power_rating, impedance_percent, x_over_r_ratio)
        self.transformers[transformer.name] = transformer

    def add_TransmissionLine(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
        transmissionline = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
        self.transmissionlines[transmissionline.name] = transmissionline