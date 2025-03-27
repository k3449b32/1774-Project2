from circuit import Circuit
import numpy as np
import pandas as pd

class Jacobian:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.buses = circuit.buses
        self.ybus = circuit.ybus.to_numpy()
        self.bus_order = circuit.bus_order
        self.bus_types = {bus: circuit.buses[bus].bus_type for bus in circuit.bus_order}

        # Get voltage magnitudes and angles using circuit.get_voltages()
        voltages_angles = {bus: circuit.get_voltages(self.buses, bus) for bus in self.bus_order}
        self.voltages = np.array([voltages_angles[bus][0] for bus in self.bus_order])  # vpu
        self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order])*np.pi/180  # delta

    def compute_jacobian(self):
        """
        Compute the full Jacobian matrix by calculating J1, J2, J3, and J4
        """
        J1 = self.compute_J1()
        J2 = self.compute_J2()
        J3 = self.compute_J3()
        J4 = self.compute_J4()

        # Construct full Jacobian matrix
        self.jacobian_matrix = np.block([[J1, J2], [J3, J4]])
        return self.jacobian_matrix

    def compute_J1(self):
        """Compute dP/dδ (J1) for non-slack buses and print itself."""

        num_buses = len(self.bus_order)
        J1 = np.zeros((num_buses - 1, num_buses - 1))  # Exclude slack bus

        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)

        for i, bus_i in enumerate(self.bus_order):
            if self.bus_types[bus_i] == "slack":
                continue  # Skip slack bus

            for j, bus_j in enumerate(self.bus_order):
                if self.bus_types[bus_j] == "slack":
                    continue  # Skip slack bus

                k = i - 1 if self.bus_types[bus_i] != "slack" else None
                n = j - 1 if self.bus_types[bus_j] != "slack" else None

                if k is None or n is None:
                    continue

                if i == j:
                    # Diagonal elements: sum of terms for all other buses
                    J1[k, k] = -sum(
                        self.voltages[i] * self.voltages[m] * y_abs[i, m] * np.sin(
                            self.angles[i] - self.angles[m] - y_angle[i, m])
                        for m in range(num_buses) if m != i
                    )
                else:
                    # Off-diagonal elements
                    J1[k, n] = self.voltages[i] * self.voltages[j] * y_abs[i, j] * np.sin(
                        self.angles[i] - self.angles[j] - y_angle[i, j])

        # Round J1 to 5 decimal places and print
        J1_rounded = np.round(J1, 5)
        print("J1 Matrix (rounded to 5 decimal places):\n", J1_rounded)

        return J1_rounded

    def compute_J2(self):
        """
        Compute J2 (dP/dV) matrix
        """
        num_buses = len(self.buses)
        J2 = np.zeros((num_buses - 1, num_buses - 1))  # Exclude slack bus

        return J2

    def compute_J3(self):
        """
        Compute J3 (dQ/dδ) matrix
        """
        num_buses = len(self.buses)
        J3 = np.zeros((num_buses - 1, num_buses - 1))  # Exclude slack bus

        return J3

    def compute_J4(self):
        """
        Compute J4 (dQ/dV) matrix
        """
        num_buses = len(self.buses)
        J4 = np.zeros((num_buses - 1, num_buses - 1))  # Exclude slack bus

        return J4
