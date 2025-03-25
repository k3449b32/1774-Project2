import numpy as np
import pandas as pd
from bus import Bus
#initialize a generator object
class Generator:

    def __init__(self, name: str, bus: Bus, mw_setpoint: float, voltage_setpoint: float):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        