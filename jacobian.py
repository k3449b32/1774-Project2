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

        voltages_angles = {bus: circuit.get_voltages(self.buses, bus) for bus in self.bus_order}
        self.voltages = np.array([voltages_angles[bus][0] for bus in self.bus_order])  # vpu
        self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order]) * np.pi / 180  # delta

        # Bus type classification
        self.slack_bus = [bus for bus, btype in self.bus_types.items() if btype == "slack"][0]
        self.pv_buses = [bus for bus, btype in self.bus_types.items() if btype == "PV"]
        self.pq_buses = [bus for bus, btype in self.bus_types.items() if btype == "PQ"]
        self.non_slack_buses = [bus for bus in self.bus_order if bus != self.slack_bus]

    def compute_jacobian(self):
        """Compute the full Jacobian matrix and return it as a labeled pandas DataFrame."""
        np.set_printoptions(linewidth=np.inf, suppress=True)  # Full width printing

        J1 = self.compute_J1()
        J2 = self.compute_J2()
        J3 = self.compute_J3()
        J4 = self.compute_J4()

        jacobian_matrix = np.block([[J1, J2], [J3, J4]])

        # Build row and column labels like PowerWorld
        row_labels = [f"dP({bus})" for bus in self.non_slack_buses] + [f"dQ({bus})" for bus in self.pq_buses]
        col_labels = [f"dθ({bus})" for bus in self.non_slack_buses] + [f"dV({bus})" for bus in self.pq_buses]

        jacobian_df = pd.DataFrame(jacobian_matrix, index=row_labels, columns=col_labels)

        print("\nJacobian matrix:\n", jacobian_df)
        return jacobian_df

    def compute_J1(self):
        """Compute dP/dδ (J1) for all non-slack buses."""
        n = len(self.non_slack_buses)
        J1 = np.zeros((n, n))
        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)

        for i, bus_i in enumerate(self.non_slack_buses):
            idx_i = self.bus_order.index(bus_i)
            for j, bus_j in enumerate(self.non_slack_buses):
                idx_j = self.bus_order.index(bus_j)

                if idx_i == idx_j:
                    J1[i, j] = -sum(
                        self.voltages[idx_i] * self.voltages[m] * y_abs[idx_i, m] *
                        np.sin(self.angles[idx_i] - self.angles[m] - y_angle[idx_i, m])
                        for m in range(len(self.bus_order)) if m != idx_i
                    )
                else:
                    J1[i, j] = self.voltages[idx_i] * self.voltages[idx_j] * y_abs[idx_i, idx_j] * np.sin(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j])

        J1_rounded = np.round(J1, 5)
        print("\nJ1 Matrix:\n", J1_rounded)
        return J1_rounded

    def compute_J2(self):
        """Compute dP/dV (J2) for non-slack buses (rows) and PQ buses (columns)."""
        J2 = np.zeros((len(self.non_slack_buses), len(self.pq_buses)))
        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)

        for i, bus_i in enumerate(self.non_slack_buses):
            idx_i = self.bus_order.index(bus_i)
            for j, bus_j in enumerate(self.pq_buses):
                idx_j = self.bus_order.index(bus_j)

                if idx_i == idx_j:
                    J2[i, j] = sum(
                        self.voltages[idx_i] * y_abs[idx_i, m] *
                        np.cos(self.angles[idx_i] - self.angles[m] - y_angle[idx_i, m])
                        for m in range(len(self.bus_order)) if m != idx_i
                    )
                else:
                    J2[i, j] = -self.voltages[idx_i] * y_abs[idx_i, idx_j] * np.cos(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j])

        J2_rounded = -np.round(J2, 5) #switching sign to match Powerworld
        print("\nJ2 Matrix:\n", J2_rounded)
        return J2_rounded

    def compute_J3(self):
        """Compute dQ/dδ (J3) for PQ buses (rows) and non-slack buses (columns)
           using PowerWorld sign convention (positive diagonals)."""
        J3 = np.zeros((len(self.pq_buses), len(self.non_slack_buses)))
        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)

        for i, bus_i in enumerate(self.pq_buses):
            idx_i = self.bus_order.index(bus_i)
            for j, bus_j in enumerate(self.non_slack_buses):
                idx_j = self.bus_order.index(bus_j)

                if idx_i == idx_j:
                    # Remove the negative sign here for PowerWorld convention
                    J3[i, j] = sum(
                        self.voltages[idx_i] * self.voltages[m] * y_abs[idx_i, m] *
                        np.cos(self.angles[idx_i] - self.angles[m] - y_angle[idx_i, m])
                        for m in range(len(self.bus_order)) if m != idx_i
                    )
                else:
                    # Keep off-diagonal elements negative
                    J3[i, j] = -self.voltages[idx_i] * self.voltages[idx_j] * y_abs[idx_i, idx_j] * np.cos(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j])

        J3_rounded = np.round(J3, 5)
        print("\nJ3 Matrix:\n", J3_rounded)
        return J3_rounded

    def compute_J4(self):
        """Compute dQ/dV (J4) for PQ buses only, using PowerWorld sign convention (positive diagonals)."""
        J4 = np.zeros((len(self.pq_buses), len(self.pq_buses)))
        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)

        for i, bus_i in enumerate(self.pq_buses):
            idx_i = self.bus_order.index(bus_i)
            for j, bus_j in enumerate(self.pq_buses):
                idx_j = self.bus_order.index(bus_j)

                if idx_i == idx_j:
                    # Flip sign for PowerWorld convention
                    J4[i, j] = -sum(
                        self.voltages[idx_i] * y_abs[idx_i, m] *
                        np.sin(self.angles[idx_i] - self.angles[m] - y_angle[idx_i, m])
                        for m in range(len(self.bus_order)) if m != idx_i
                    )
                else:
                    # Off-diagonal elements stay the same
                    J4[i, j] = self.voltages[idx_i] * y_abs[idx_i, idx_j] * np.sin(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j])

        J4_rounded = np.round(J4, 5)
        print("\nJ4 Matrix:\n", J4_rounded)
        return J4_rounded

