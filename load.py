import numpy as np
import pandas as pd
from bus import Bus
#load class
class Load:

    def __init__(self, name: str, bus: Bus, real_power: float, reactive_power: float):
        self.name = name
        self.bus = bus
        self.real_power = real_power
        self.reactive_power = reactive_power