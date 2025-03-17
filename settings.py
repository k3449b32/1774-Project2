import numpy as np

#config
class Settings:

    frequency: float = 60
    base_power: float = 100

    def compute_power_mismatch(self, bus, ybus, voltages):

