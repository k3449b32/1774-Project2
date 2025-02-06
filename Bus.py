import numpy as np
import pandas as pd

class Bus:

    counter = 1

    def __init__(self, name: str, base_kv: float):
        self.name = name
        self.base_kv = base_kv
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1