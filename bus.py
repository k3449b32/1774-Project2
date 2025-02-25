import numpy as np
import pandas as pd

class Bus:

    counter = 0
    ACCEPTABLE_BUS_TYPES = ['Slack', 'PQ', 'PV']

    def __init__(self, name: str, base_kv: float):





        self.bus_type = 'PQ' #set bus type to PQ
        if self.bus_type not in Bus.ACCEPTABLE_BUS_TYPES:
            raise ValueError(f"Invalid bus type '{self.bus_type}'. Acceptable types are {Bus.ACCEPTABLE_BUS_TYPES}.")

        #obtain, name, base voltage
        self.name = name
        self.base_kv = base_kv
        self.vpu = 1.0 #initialize vpu to 1
        self.float=float
        self.delta=0 #initialize phase angle to 0
        # Keeping an index of all bus instances
        self.index = Bus.counter
        Bus.counter += 1