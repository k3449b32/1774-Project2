import numpy as np
import pandas as pd
#initizalize a bus object
class Bus:

    counter = 0

    def __init__(self, name: str, base_kv: float):

        # obtain, name, base voltage
        self.name = name
        self.base_kv = base_kv
        self.vpu = 1.0 # initialize vpu to 1
        self.delta = 0 # initialize phase angle to 0
        self.bus_type = 'PQ'
        self.real_power = 0
        self.reactive_power = 0
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1
        self.radians = 0

    def set_voltage_and_delta(self, voltage: float, delta: float):
        self.vpu = voltage
        self.delta = delta