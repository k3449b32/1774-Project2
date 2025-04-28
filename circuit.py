import numpy as np
import pandas as pd
from geometry import Geometry
from bus import Bus
from transmission_line import TransmissionLine
from bundle import Bundle
from transformer import Transformer
from conductor import Conductor
from generator import Generator
from load import Load
from settings import Settings

class Circuit:

    def __init__(self, name: str):
        self.name = name
        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometry = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}
        self.ybus = None
        self.zbus = None
        self.first_gen = False
        self.bus_order = []
        self.real_power = {}
        self.reactive_power = {}
        self.voltages = {}
        self.radians = 0

    def add_bus(self, name: str, bus_kv: float):
        if name in self.buses:
            raise ValueError("Bus is already in circuit")
        else:
            self.buses[name] = Bus(name, bus_kv)
            self.bus_order.append(name)
            self.real_power[name] = 0
            self.reactive_power[name] = 0

    def add_conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        if name in self.conductors:
            raise ValueError("Conductor is already in circuit")
        else:
            self.conductors[name] = Conductor(name, diam, GMR, resistance, ampacity)

    def add_bundle(self, name: str, num_conductors: float, spacing: float, conductor: str):
        if name in self.bundles:
            raise ValueError("Bundle is already in circuit")
        else:
            self.bundles[name] = Bundle(name, num_conductors, spacing, self.conductors[conductor])

    def add_geometry(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
        if name in self.geometry:
            raise ValueError("Geometry is already in circuit")
        else:
            self.geometry[name] = Geometry(name, xa, ya, xb, yb, xc, yc)

    def add_transformer(self, name: str, bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float, connection_type: str,z_ground: float,is_grounded: str):
        if name in self.transformers:
            raise ValueError("Transformer is already in circuit")
        else:
            self.transformers[name] = Transformer(name, self.buses[bus1], self.buses[bus2], power_rating,
                                                  impedance_percent, x_over_r_ratio, connection_type,z_ground,is_grounded)

    def add_transmission_line(self, name: str, bus1: str, bus2: str, bundle: str, geometry: str, length: float):
        if name in self.transmission_lines:
            raise ValueError("Transmission Line is already in circuit")
        else:
            self.transmission_lines[name] = TransmissionLine(name, self.buses[bus1], self.buses[bus2], self.bundles[bundle], self.geometry[geometry], length)

    def add_load_element(self, name: str, bus: str, real_power: float, reactive_power: float):
        if name in self.loads:
            raise ValueError("Load is already in circuit")
        else:
            self.loads[name] = Load(name, self.buses[bus], real_power, reactive_power)
            if bus not in self.real_power:
                self.real_power[bus] = 0  # Initialize if missing
            self.real_power[bus] -= real_power
            if bus not in self.reactive_power:
                self.reactive_power[bus] = 0  # Initialize if missing
            self.reactive_power[bus] -= reactive_power
        self.calc_ybus()

    def add_generator_element(self, name: str, bus: str, real_power: float, per_unit_voltage: float,
                              subtransient_x, positive_x, negative_x, z_ground, is_grounded):
        if name in self.generators:
            raise ValueError("Generator is already in circuit")
        # ✅ Set slack bus type BEFORE generator is created
        if not self.first_gen:
            self.first_gen = True
            self.buses[bus].bus_type = 'slack'
        else:
            self.buses[bus].bus_type = 'PV'
        # Now create the generator with correct bus type
        self.generators[name] = Generator(name, self.buses[bus], real_power, per_unit_voltage,
                                          subtransient_x, positive_x, negative_x, z_ground, is_grounded)
        # Update net real power
        if bus not in self.real_power:
            self.real_power[bus] = 0
        self.real_power[bus] += real_power
        self.calc_ybus()

    def calc_ybus(self):
        # Step 1: Initialize the Ybus matrix as a zero matrix with dimensions N x N
        N = len(self.buses)  # Number of buses
        self.ybus = np.zeros((N, N), dtype=complex)

        # Step 2: Create a dictionary to map bus names to indices for easier reference
        bus_indices = {bus_name: idx for idx, bus_name in enumerate(self.buses)}

        # Step 3: Iterate through all transmission lines
        for line in self.transmission_lines.values():
            Yprim = line.y_matrix  # Get the primitive admittance matrix
            bus1_idx = bus_indices[line.bus1.name]
            bus2_idx = bus_indices[line.bus2.name]

            # Add the elements of the Yprim matrix into the Ybus matrix
            self.ybus[bus1_idx, bus1_idx] += Yprim.iloc[0, 0]  # Self-admittance for bus1
            self.ybus[bus1_idx, bus2_idx] += Yprim.iloc[0, 1]  # Mutual admittance between bus1 and bus2
            self.ybus[bus2_idx, bus1_idx] += Yprim.iloc[1, 0]  # Mutual admittance between bus2 and bus1
            self.ybus[bus2_idx, bus2_idx] += Yprim.iloc[1, 1]  # Self-admittance for bus2

        # Step 4: Iterate through all transformers
        for transformer in self.transformers.values():
            Yprim = transformer.y_matrix  # Get the primitive admittance matrix
            bus1_idx = bus_indices[transformer.bus1.name]
            bus2_idx = bus_indices[transformer.bus2.name]

            # Add the elements of the Yprim matrix into the Ybus matrix
            self.ybus[bus1_idx, bus1_idx] += Yprim.iloc[0, 0]  # Self-admittance for bus1
            self.ybus[bus1_idx, bus2_idx] += Yprim.iloc[0, 1]  # Mutual admittance between bus1 and bus2
            self.ybus[bus2_idx, bus1_idx] += Yprim.iloc[1, 0]  # Mutual admittance between bus2 and bus1
            self.ybus[bus2_idx, bus2_idx] += Yprim.iloc[1, 1]  # Self-admittance for bus2

        # Step 5: Numerical stability check (ensure no singularities)
        if np.any(np.diag(self.ybus) == 0):  # If any diagonal element is zero, it indicates a singularity
            raise ValueError("Ybus matrix has a singularity (zero diagonal entry). Please check bus connections.")

        # Step 6: Convert Ybus into a pandas DataFrame with bus names as row and column indices
        self.ybus = pd.DataFrame(self.ybus, index=self.buses.keys(), columns=self.buses.keys())

        # Now, the Ybus is stored as a pandas DataFrame with proper bus names

        # Making sure it shows all of the rows and columns properly
        pd.set_option('display.max_rows', None)  # No limit to the number of rows displayed
        pd.set_option('display.max_columns', None)  # No limit to the number of columns displayed
        pd.set_option('display.width', None)  # No width limit (adjust to your console's width)
        pd.set_option('display.max_colwidth', None)  # No limit to the column width

    def calc_zero_negative_ybus(self):
        # Step 1: Initialize the Ybus matrix as a zero matrix with dimensions N x N
        N = len(self.buses)  # Number of buses
        self.zero_ybus = np.zeros((N, N), dtype=complex)  # create the zero ybus
        self.negative_ybus = np.zeros((N, N), dtype=complex)  # create the negative ybus

        # Step 2: Create a dictionary to map bus names to indices for easier reference
        bus_indices = {bus_name: idx for idx, bus_name in enumerate(self.buses)}

        # ===============================================================================================================#
        # Step 3: Iterate through all transmission lines
        for line in self.transmission_lines.values():
            Yprim_zero = line.zero_yprim  # Get the primitive admittance matrix
            Yprim = line.y_matrix
            bus1_idx = bus_indices[line.bus1.name]
            bus2_idx = bus_indices[line.bus2.name]

            # Add the elements of the zero Yprim matrix into the zero Ybus matrix
            self.zero_ybus[bus1_idx, bus1_idx] += Yprim_zero.iloc[0, 0]
            self.zero_ybus[bus1_idx, bus2_idx] += Yprim_zero.iloc[0, 1]
            self.zero_ybus[bus2_idx, bus1_idx] += Yprim_zero.iloc[1, 0]
            self.zero_ybus[bus2_idx, bus2_idx] += Yprim_zero.iloc[1, 1]

            # Add the elements of the yprim matrix into the negative ybus matrix
            self.negative_ybus[bus1_idx, bus1_idx] += Yprim.iloc[0, 0]
            self.negative_ybus[bus1_idx, bus2_idx] += Yprim.iloc[0, 1]
            self.negative_ybus[bus2_idx, bus1_idx] += Yprim.iloc[1, 0]
            self.negative_ybus[bus2_idx, bus2_idx] += Yprim.iloc[1, 1]

        # ==================================================================================================================#
        # Step 4: Iterate through all transformers
        for transformer in self.transformers.values():
            Yprim_zero = transformer.zero_yprim
            Yprim_neg = transformer.negative_yprim
            bus1_idx = bus_indices[transformer.bus1.name]
            bus2_idx = bus_indices[transformer.bus2.name]

            # Only stamp off-diagonals into zero sequence
            self.zero_ybus[bus1_idx, bus2_idx] += Yprim_zero.iloc[0, 1]
            self.zero_ybus[bus2_idx, bus1_idx] += Yprim_zero.iloc[1, 0]

            # Add full negative sequence stamping
            self.negative_ybus[bus1_idx, bus1_idx] += Yprim_neg.iloc[0, 0]
            self.negative_ybus[bus1_idx, bus2_idx] += Yprim_neg.iloc[0, 1]
            self.negative_ybus[bus2_idx, bus1_idx] += Yprim_neg.iloc[1, 0]
            self.negative_ybus[bus2_idx, bus2_idx] += Yprim_neg.iloc[1, 1]

        # ==================================================================================================================#
        # Step 5: Iterate through all generators
        for generator in self.generators.values():
            bus1_idx = bus_indices[generator.bus.name]
            Yprim_zero = generator.zero_yprim
            Yprim_neg = generator.negative_yprim

            self.zero_ybus[bus1_idx, bus1_idx] += Yprim_zero.iloc[0, 0]
            self.negative_ybus[bus1_idx, bus1_idx] += Yprim_neg.iloc[0, 0]

        # ==================================================================================================================#
        # Step 6: Numerical stability check (ensure no singularities)
        if np.any(np.diag(self.zero_ybus) == 0):
            raise ValueError("Ybus matrix has a singularity (zero diagonal entry). Please check bus connections.")
        if np.any(np.diag(self.negative_ybus) == 0):
            raise ValueError("Ybus matrix has a singularity (zero diagonal entry). Please check bus connections.")

        # Step 7: Fix diagonals only for buses that have nonzero off-diagonal admittances
        for i in range(N):
            off_diag = np.copy(self.zero_ybus[i, :])
            off_diag[i] = 0  # exclude self-admittance
            if np.any(off_diag != 0):  # if there are mutual connections
                self.zero_ybus[i, i] = -np.sum(off_diag)

        # Step 7b: Fix diagonals for negative sequence Ybus (just like zero)
        for i in range(N):
            off_diag = np.copy(self.negative_ybus[i, :])
            off_diag[i] = 0
            if np.any(off_diag != 0):
                self.negative_ybus[i, i] = -np.sum(off_diag)

        # Step 8: Convert Ybus into a pandas DataFrame with bus names as row and column indices
        self.zero_ybus = pd.DataFrame(self.zero_ybus, index=self.buses.keys(), columns=self.buses.keys())
        self.negative_ybus = pd.DataFrame(self.negative_ybus, index=self.buses.keys(), columns=self.buses.keys())

        # Step 9: Display settings for full matrix visibility
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    def get_voltages(self, buses, bus_name):
        if bus_name not in buses:
            raise KeyError(f"Bus '{bus_name}' not found in the buses dictionary.")

        v = buses[bus_name].vpu # Retrieve voltage magnitude
        delta = buses[bus_name].delta  # Retrieve voltage angle

        return [v, delta]

    def compute_power_injection(self, buses, ybus):
        # This function takes in buses and ybus (the admittance matrix)
        num_buses = len(buses)  # Total number of buses
        v = np.zeros(num_buses)  # Store voltage magnitudes
        delta = np.zeros(num_buses)  # Store voltage angles

        # Fetch voltages and angles for all buses
        for i, bus_name in enumerate(self.bus_order):  # Ensure a consistent order
            v[i], delta[i] = self.get_voltages(buses, bus_name)  # Corrected storage

        P = np.zeros(num_buses)  # Store real power injection for each bus
        Q = np.zeros(num_buses)  # Store reactive power injection for each bus

        yabs = pd.DataFrame(np.abs(ybus.to_numpy()), index=ybus.index, columns=ybus.columns)
        ydelta = pd.DataFrame(np.angle(ybus.to_numpy()), index=ybus.index, columns=ybus.columns)

        for k, bus_k in enumerate(buses.keys()):  # Iterate through each bus
            for n, bus_n in enumerate(buses.keys()):  # Iterate through mutual admittances
                if self.radians == 0:               # Convert to radians
                    delta_k = delta[k] * np.pi / 180
                    delta_n = delta[n] * np.pi / 180
                else:                               # Already in radians
                    delta_k = delta[k]
                    delta_n = delta[n]
                #print(
                    #f"bus_k={bus_k:<5} bus_n={bus_n:<5}  v[k]={v[k]:.5f}  v[n]={v[n]:.5f}  |Yₖₙ|={yabs.loc[bus_k, bus_n]:.5f}  Δk={delta_k:.5f}  Δn={delta_n:.5f}  θₖₙ={ydelta.loc[bus_k, bus_n]:.5f}",
                    #np.cos(delta_k - delta_n - ydelta.loc[bus_k, bus_n]))
                P[k] += v[k] * yabs.loc[bus_k, bus_n] * v[n] * np.cos(delta_k - delta_n - ydelta.loc[bus_k, bus_n])
                Q[k] += v[k] * yabs.loc[bus_k, bus_n] * v[n] * np.sin(delta_k - delta_n - ydelta.loc[bus_k, bus_n])

        print("Power Injection:")
        print(P)
        print(Q)

        return P, Q  # Return power injection matrices

    def compute_power_mismatch(self, buses, ybus):
        # Compute actual power injections from Y-bus
        P, Q = self.compute_power_injection(buses, ybus)

        # Initialize mismatch vectors as pandas DataFrames with bus names as indices
        delta_P = pd.DataFrame(np.zeros(len(buses)), index=buses.keys(), columns=["Delta_P"])
        delta_Q = pd.DataFrame(np.zeros(len(buses)), index=buses.keys(), columns=["Delta_Q"])

        for i, bus_name in enumerate(self.bus_order):
            bus = self.buses[bus_name]  # Get the Bus object

            if bus.bus_type == "slack":  # Skip slack bus
                continue

            # Compute total generator power at the bus
            P_gen = sum(gen.mw_setpoint for gen in self.generators.values() if gen.bus.name == bus_name)/100

            # Compute total load power at the bus (without mistakenly including generators)
            P_load = sum(-load.real_power for load in self.loads.values() if load.bus.name == bus_name)/100

            # Calculate the power mismatch
            mismatch = P_gen + P_load - P[i]

            # Ensure correct sign based on bus type
            if (buses[bus_name].bus_type == "PQ" or P_gen == 0) and mismatch != 0:
                delta_P.loc[bus_name, "Delta_P"] = -abs(mismatch)  # Force negative if nonzero
            else:
                delta_P.loc[bus_name, "Delta_P"] = mismatch  # Keep as is for PV/slack or if mismatch is zero

            if bus.bus_type == "PQ":
                # Reactive power mismatch only for PQ buses
                Q_load = self.reactive_power.get(bus_name, 0)/100  # Get reactive load power
                delta_Q.loc[bus_name, "Delta_Q"] = Q_load - Q[i]  # No generator Q, only loads

        # Concatenate mismatch vectors for numerical solution
        mismatch_df = pd.DataFrame({
            "Bus": list(buses.keys()),  # First column with bus names
            "Delta_P": delta_P["Delta_P"].values,  # Second column with delta P values
            "Delta_Q": delta_Q["Delta_Q"].values  # Third column with delta Q values
        })

        return mismatch_df


    def modify_y_bus(self):
        #adds subtransient admittance to each bus that has a generator attached, this creates the positive sequence ybus

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

    def calculate_asym_fault(self, fault_type, faulted_bus:str, Zf=0.0):
        import numpy as np
        import pandas as pd

        print("\n>>> ENTERED calculate_asym_fault")

        ordered_buses = list(self.buses.keys())
        b_idx = ordered_buses.index(faulted_bus) #index of the faulted bus

        bus_indices = {bus_name: idx for idx, bus_name in enumerate(ordered_buses)} #get a list of indices from the ordered_buses list



        #convert zero, negative, and negative? ybus matrices from dataframe to numPy arrays
        Y0_np = np.array([
            [self.zero_ybus.loc[bi, bj] for bj in ordered_buses]
            for bi in ordered_buses
        ], dtype=np.complex128)
        Y1_np = np.array([
            [self.ybus.loc[bi, bj] for bj in ordered_buses]
            for bi in ordered_buses
        ], dtype=np.complex128)
        Y2_np = np.array([
            [self.negative_ybus.loc[bi, bj] for bj in ordered_buses]
            for bi in ordered_buses
        ], dtype=np.complex128)

        #calcualte the z0, z1, and z2 buses (they are numpy buses)
        z0_np = np.linalg.inv(Y0_np)
        z1_np = np.linalg.inv(Y1_np)
        z2_np = np.linalg.inv(Y2_np)

        # Just invert diagonal terms directly — all in per-unit already
        Z0_diag_inv = 1 / Y0_np[b_idx][b_idx]
        Z1_diag_inv = 1 / Y1_np[b_idx][b_idx]
        Z2_diag_inv = 1 / Y2_np[b_idx][b_idx]

        print(f"Y0_np[{b_idx},{b_idx}] = {Y0_np[b_idx][b_idx]}")
        print(f"Expected 1 / Y0 = {Z0_diag_inv}")
        print(f"Z0[Bus] = {Z0_diag_inv}")

        V_prefault = self.buses[faulted_bus].vpu * np.exp(1j * np.deg2rad(self.buses[faulted_bus].delta))
        print(f"V_prefault = {V_prefault}")

        if fault_type == "slg":
            denom = Z0_diag_inv + Z1_diag_inv + Z2_diag_inv + 3 * Zf
            I_seq = V_prefault / denom
            I0 = I1 = I2 = I_seq

        elif fault_type == "ll":
            denom = Z1_diag_inv + Z2_diag_inv + Zf
            I1 = V_prefault / denom
            I2 = -I1
            I0 = 0

        elif fault_type == "dlg":
            num = V_prefault * (Z1_diag_inv + Z2_diag_inv + Zf)
            denom = Z0_diag_inv * (Z1_diag_inv + Z2_diag_inv + Zf) + Z1_diag_inv * Z2_diag_inv + Zf * (
                        Z1_diag_inv + Z2_diag_inv)
            I0 = num / denom
            I1 = I0
            I2 = I0

        else:
            raise ValueError("Invalid fault type")

        # Convert sequence to phase
        a = np.exp(2j * np.pi / 3)
        T_inv = np.array([
            [1, 1, 1],
            [1, a ** 2, a],
            [1, a, a ** 2]
        ])
        Iabc = T_inv @ np.array([I0, I1, I2])

        #=============Calculating Voltages===========================================#
        #this part needs to be completly redone!
        #create a vector to hold all the voltages for each bus
        volt_012 = np.zeros((3,len(self.buses)), dtype=complex) #zero sequence voltage, v0



        #this is wrong!
        #iterate through all buses to calculate the zero, negative, and positive sequence voltages
        busK_zmatrix = np.zeros((3,3)) #create an array that will hold the impedance of the kth bus
        I_n = np.array([[I0],[I1],[I2]]) #create a array containing sequence currents of the faulted bus
        vF_matrix = np.array([[0],[1],[0]])


        for bus_k in ordered_buses:
            k_idx = bus_indices[bus_k] #get the index of the current bus

            #obtain the sequence impedances for the kth bus
            zkn0 = z0_np[k_idx][b_idx]
            zkn1 = z1_np[k_idx][b_idx]
            zkn2 = z2_np[k_idx][b_idx]

            #the diagonals of busK_zmatrix will hold the sequence impedances of the kth bus
            busK_zmatrix[0,0] = zkn0
            busK_zmatrix[1,1] = zkn1
            busK_zmatrix[2,2] = zkn2

            vk_012 = vF_matrix-np.matmul(busK_zmatrix,I_n) #calulate the sequence voltages for the current bus

            #add the voltages to the matrix holding all the voltages
            volt_012[0,k_idx] = vk_012[0,0]
            volt_012[1, k_idx] = vk_012[1,0]
            volt_012[2, k_idx] = vk_012[2,0]







        phase_voltages = T_inv @ volt_012

        print("\nPhase Voltage Matrix: Rows are Va, Vb, Vc, columns are buses\n")
        print(phase_voltages)

        print(f"\nAsymmetrical Fault Currents ({fault_type.upper()}) at {faulted_bus}:")
        for phase, val in zip(['A', 'B', 'C'], Iabc):
            mag = abs(val)
            ang = np.angle(val, deg=True)
            print(f"Phase {phase}: {mag:.4f} p.u., ∠ {ang:.2f}°")

        return {"Ia": Iabc[0], "Ib": Iabc[1], "Ic": Iabc[2]}, (I0, I1, I2)


        #1