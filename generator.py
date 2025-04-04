import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings
#initialize a generator object
class Generator:

    def __init__(self, name: str, bus: Bus, mw_setpoint: float, voltage_setpoint: float,subtransient_x: float):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.subtransient_x=subtransient_x*(Settings.base_power/self.mw_setpoint) #change the base of the subtransient reactance
        