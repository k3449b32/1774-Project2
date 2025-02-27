import numpy as np

#config
class Settings:
    frequency: float=60
    base_power: float=100
    def __init__(self):
        pass

    def compute_power_injection(self, bus, ybus, voltages):

        # Extract the voltage at the bus
        voltage_i = voltages[bus.index]

        # Initialize complex power
        S_i = 0j  # Complex number initialization

        # Loop over all buses to calculate the sum of Yij * Vj* for the given bus
        for j in range(len(ybus)):
            V_j_conjugate = np.conj(voltages[j])  # Complex conjugate of voltage at bus j
            S_i += ybus[bus.index, j] * voltage_i * V_j_conjugate

        # Real power injection is the real part of the complex power
        P_i = np.real(S_i)

        # Reactive power injection is the imaginary part of the complex power
        Q_i = np.imag(S_i)

        # For different bus types, handle the computation differently:
        if bus.bus_type == "Slack":
            # For Slack bus, no power mismatch calculation is needed
            return 0, 0  # Slack bus has fixed power injection (no mismatch needed)

        elif bus.bus_type == "PQ":
            # For PQ bus, return both real and reactive power injections
            return P_i, Q_i

        elif bus.bus_type == "PV":
            # For PV bus, return only real power injection (reactive power is not computed)
            return P_i, 0


