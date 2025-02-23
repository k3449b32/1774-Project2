import numpy as np
import pandas as pd

class Bus:

    counter = 0

    def __init__(self, name: str, base_kv: float, vpu:float,delta: float, bus_type: str):
        self.bus_type = bus_type
        self.name = name
        self.base_kv = base_kv
        self.float=float
        self.delta=delta
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1