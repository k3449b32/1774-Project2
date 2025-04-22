from circuit import Circuit
from jacobian import Jacobian
import numpy as np
import pandas as pd

class Power_Flow:

    def __init__(self, circuit: Circuit, jacobian: Jacobian):
        self.circuit = circuit
        self.jacobian = jacobian

    def solve(self, buses, ybus, tol=10**-9, max_iter=50):
        converged = False

        for iteration in range(max_iter):
            print(f"\n--- Iteration {iteration + 1} ---")
            self.circuit.radians = 1
            # Step 1: Calculate power mismatches
            mismatch_df = self.circuit.compute_power_mismatch(buses, ybus)
            print(mismatch_df)

            # Step 2: Build mismatch vector (ΔP + ΔQ) matching Jacobian's order
            delta_P = []
            delta_Q = []

            # Non-slack buses (PV and PQ) for ΔP
            for bus_name in self.circuit.bus_order:
                bus_type = buses[bus_name].bus_type
                if bus_type != 'slack':
                    delta_P.append(mismatch_df.loc[mismatch_df["Bus"] == bus_name, "Delta_P"].values[0])

            # PQ buses only for ΔQ
            for bus_name in self.circuit.bus_order:
                bus_type = buses[bus_name].bus_type
                if bus_type == 'PQ':
                    delta_Q.append(mismatch_df.loc[mismatch_df["Bus"] == bus_name, "Delta_Q"].values[0])

            # Form combined mismatch vector
            mismatch_vector = np.array(delta_P + delta_Q)

            # Step 3: Check convergence
            max_mismatch = np.max(np.abs(mismatch_vector))
            print("Mismatch Vector:\n", mismatch_vector)
            print("Max mismatch:", max_mismatch)

            if max_mismatch < tol:
                print("\n✅ Power flow converged.")
                converged = True
                break

            # Step 4: Compute Jacobian
            J = self.jacobian.compute_jacobian().values
            print(J)

            # Step 5: Solve J * Δx = mismatch
            delta_x = np.linalg.solve(J, mismatch_vector)
            print("Delta x:\n", delta_x)
            if iteration < 10:
                delta_x[:len(self.jacobian.non_slack_buses)] *= 0.3  # Dampen angles
                delta_x[len(self.jacobian.non_slack_buses):] *= 0.5  # Dampen voltages
            # Step 6: Update angles (Δθ in radians) and voltages (ΔV)
            delta_idx = 0
            for bus in self.jacobian.non_slack_buses:
                buses[bus].delta += (delta_x[delta_idx])

                delta_idx += 1
            for bus in self.jacobian.pq_buses:
                buses[bus].vpu += delta_x[delta_idx]
                # Optional: Clamp voltage to avoid divergence
                buses[bus].vpu = max(min(buses[bus].vpu, 1.5), 0.5)
                delta_idx += 1

            # NaN safeguard
            for bus in buses.values():
                if np.isnan(bus.vpu) or np.isnan(bus.delta):
                    print(f"\n❌ NaN detected at {bus.name}. Aborting iteration.")
                    return buses

        if not converged:
            print("\n❌ Power flow did NOT converge after max iterations.")

        # Final results (convert delta to degrees for output only)
        print("\nFinal Bus Voltages:")
        for bus in self.circuit.bus_order:
            v = buses[bus].vpu
            delta_deg = np.degrees(buses[bus].delta)  # Convert radians to degrees for printing
            print(f"{bus}: V = {v:.5f} p.u., δ = {delta_deg:.5f}°")

        return buses