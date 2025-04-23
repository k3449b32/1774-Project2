from circuit import Circuit
from jacobian import Jacobian
import numpy as np
import pandas as pd
#solution class to run a power flow study or fault study based on mode specified by the user
#if solve_mode is power_flow, Solution will calculate y_bus and then jacobian
#if solve_mode is fault_study, Solution will run whatever is needed to calculate fault_study
#the Solution class takes in a circuit object and string that specifies which mode to run the simulation in

#in the file where this code is being tested: add buses, loads, generators, etc to circuit
#declare a solution object, then do solutionObject.solve()

class Solution:
    def __init__(self, circuit:Circuit):
        self.circuit=circuit

    def do_power_flow(self, buses, ybus, tol=10 ** -9, max_iter=50):
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

    def modify_y_bus(self):
        #adds subtransient admittance to each bus that has a generator attached

        bus_indices = {bus_name: idx for idx, bus_name in enumerate(self.buses)}


        for generator in self.generators.values(): #iterate through the generator dictionary
            bus1_idx = bus_indices[generator.bus.name] #obtain the bus for each generator, and modify the corresponding position in the y matrix
            self.ybus.iloc[bus1_idx,bus1_idx] += generator.sub_admittance


    def calculate_fault(self,faulted_bus):
        #calculates the current and voltage at each bus under fault conditions, as well as the zbus matrix
        self.zbus=np.linalg.inv(self.ybus)
        self.zbus = pd.DataFrame(self.zbus, index=self.ybus.keys(), columns=self.ybus.keys())
        #bus_indices = {bus_name: idx for idx, bus_name in enumerate(self.buses)}
        #fault_current=np.zeros(len(self.buses),dtype=complex)
        fault_voltage=np.zeros(len(self.buses),dtype=complex)

        #faulted_bus = list(self.buses.keys())[0]
        #f_bus_index=self.buses[faulted_bus]

        znn = self.zbus.loc[faulted_bus, faulted_bus]
        i_f = 1.0 / znn


        for idx, bus_name in enumerate(self.buses):

            zkn = self.zbus.loc[bus_name, faulted_bus]



            e_k=1-zkn/znn
            fault_voltage[idx]=e_k


        return i_f,fault_voltage

    def solve_fault(self, faulted_bus, fault_type="3phase"):
        if fault_type == "3phase":
            self.modify_y_bus()
            i_f, v_post = self.calculate_fault(faulted_bus)
            print(f"3ϕ Fault Current: {i_f}")
            print(f"Post-fault voltages: {v_post}")
        elif fault_type in ["LG", "LL", "LLG"]:
            self.run_asym_fault(faulted_bus, fault_type)
        else:
            raise ValueError("Unsupported fault type")


