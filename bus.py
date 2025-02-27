import numpy as np
import pandas as pd

class Bus:

    counter = 0

    def __init__(self, name: str, base_kv: float):

        # obtain, name, base voltage
        self.name = name
        self.base_kv = base_kv
        self.vpu = 1.0 # initialize vpu to 1
        self.delta = 0 # initialize phase angle to 0
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1