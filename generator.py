import numpy as np
import pandas as pd
from bus import Bus
from settings import Settings
#initialize a generator object
class Generator:
    def __init__(self, name: str, bus: Bus, mw_setpoint: float, voltage_setpoint: float,
                 subtransient_x: float, subtransient_x2: float = None, subtransient_x0: float = None,
                 zg: float = 0.0, grounded=True):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.grounded = grounded

        base = Settings.base_power / self.mw_setpoint

        self.xd1 = 1j * subtransient_x * base  # Positive-sequence
        self.xd2 = 1j * (subtransient_x2 if subtransient_x2 is not None else subtransient_x) * base  # Negative-seq
        self.xd0 = 1j * (subtransient_x0 if subtransient_x0 is not None else subtransient_x) * base  # Zero-seq

        self.zg = 1j * zg * base if grounded else np.inf

        self.sub_admittance = 1 / self.xd1 if self.xd1 != 0 else 0

    def y_prim(self, sequence):
        if sequence == "positive":
            return 1 / self.xd1
        elif sequence == "negative":
            return 1 / self.xd2
        elif sequence == "zero":
            if not self.grounded or self.zg == np.inf:
                return 0  # no path to ground
            return 1 / (self.xd0 + self.zg)
        else:
            raise ValueError("Invalid sequence type")
