import numpy as np
import pandas as pd

class Bus:

    counter = 0
    ACCEPTABLE_BUS_TYPES = ['Slack', 'PQ', 'PV']

    def __init__(self, name: str, base_kv: float, bus_type: str, vpu: float = 1.0, delta: float = 0.0):

        # Ensure bus_type is valid
        if bus_type not in Bus.ACCEPTABLE_BUS_TYPES:
            raise ValueError(f"Invalid bus type '{bus_type}'. Acceptable types are {Bus.ACCEPTABLE_BUS_TYPES}.")
        self.bus_type = bus_type

        self.bus_type = bus_type
        self.name = name
        self.base_kv = base_kv
        self.vpu = vpu
        self.float=float
        self.delta=delta
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1