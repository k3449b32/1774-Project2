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
        if self.circuit.radians == 0:
            self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order]) * np.pi /180
        else:
            self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order])

        # Bus type classification
        self.slack_bus = [bus for bus, btype in self.bus_types.items() if btype == "slack"][0]
        self.pv_buses = [bus for bus, btype in self.bus_types.items() if btype == "PV"]
        self.pq_buses = [bus for bus, btype in self.bus_types.items() if btype == "PQ"]
        self.non_slack_buses = [bus for bus in self.bus_order if bus != self.slack_bus]

    def refresh_state(self):
        voltages_angles = {bus: self.circuit.get_voltages(self.buses, bus) for bus in self.bus_order}
        self.voltages = np.array([voltages_angles[bus][0] for bus in self.bus_order])
        if self.circuit.radians == 0:
            self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order]) * np.pi / 180  # convert to radians
        else:
            self.angles = np.array([voltages_angles[bus][1] for bus in self.bus_order]) # already in radians

    def compute_jacobian(self):
        """Compute the full Jacobian matrix and return it as a labeled pandas DataFrame."""
        self.refresh_state()  # ✅ Always use current bus state

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
        return jacobian_df

    def invert_jacobian(self):
        """Compute and print the inverse of the Jacobian matrix as a labeled DataFrame."""
        jacobian_df = self.compute_jacobian()
        jacobian_matrix = jacobian_df.to_numpy()

        try:
            inv_jacobian = np.linalg.inv(jacobian_matrix)
        except np.linalg.LinAlgError:
            print("Jacobian matrix is singular and cannot be inverted.")
            return None

        # Use same row/column labels as the original Jacobian
        row_labels = jacobian_df.columns  # Jacobian columns become inverse rows
        col_labels = jacobian_df.index  # Jacobian rows become inverse columns

        inv_df = pd.DataFrame(inv_jacobian, index=row_labels, columns=col_labels)
        print("Inverse Jacobian:")
        print(inv_df)
        return inv_df

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

        return J1

    def compute_J2(self):
        """Compute dP/dV (J2) for non-slack buses (rows) and PQ buses (columns)."""
        J2 = np.zeros((len(self.non_slack_buses), len(self.pq_buses)))
        y_abs = np.abs(self.ybus)
        y_angle = np.angle(self.ybus)
        S = 0
        for i, bus_i in enumerate(self.non_slack_buses):
            idx_i = self.bus_order.index(bus_i)
            for j, bus_j in enumerate(self.pq_buses):
                idx_j = self.bus_order.index(bus_j)

                if idx_i == idx_j:
                    total = 0
                    for m in range(len(self.bus_order)):
                        if m != idx_i:
                            I = self.voltages[idx_i] * y_abs[idx_i,idx_i]*np.cos(y_angle[idx_i,idx_i])
                            term_voltage = self.voltages[m] #GOOD
                            term_y_abs = y_abs[idx_i, m] #
                            angle_diff = self.angles[idx_i] - self.angles[m]
                            theta = y_angle[idx_i, m]
                            cos_term = np.cos(angle_diff - theta)
                            term = term_voltage * term_y_abs * cos_term

                            total += term
                    Vk = self.voltages[idx_i]
                    Gkk = np.real(self.ybus[idx_i, idx_i])
                    diag_term = Vk * Gkk
                    J2[i, j] = 2 * diag_term + total

                else:
                    J2[i, j] = -(-self.voltages[idx_i] * y_abs[idx_i, idx_j] * np.cos(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j]))

        return J2

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

        return J3

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
                    total = 0
                    for m in range(len(self.bus_order)):
                        if m != idx_i:
                            Vm = self.voltages[m]
                            Ykm = y_abs[idx_i, m]
                            angle_diff = self.angles[idx_i] - self.angles[m]
                            theta = y_angle[idx_i, m]
                            sin_term = np.sin(angle_diff - theta)
                            term = Vm * Ykm * sin_term

                            total += term

                    Vk = self.voltages[idx_i]
                    Bkk = -np.imag(self.ybus[idx_i, idx_i])
                    diag_term = Vk * Bkk
                    J4[i, j] = total + 2*diag_term

                else:
                    J4[i, j] = self.voltages[idx_i] * y_abs[idx_i, idx_j] * np.sin(
                        self.angles[idx_i] - self.angles[idx_j] - y_angle[idx_i, idx_j])

        return J4


