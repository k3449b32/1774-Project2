from circuit import Circuit
from jacobian import Jacobian
from power_flow import Power_Flow
import numpy as np

# Creating Circuit for 7-bus powerworld system
circuit1 = Circuit("circuit1")

# Creating all buses for the circuit
circuit1.add_bus("Bus1", 20)
circuit1.add_bus("Bus2", 230)
circuit1.add_bus("Bus3", 230)
circuit1.add_bus("Bus4", 230)
circuit1.add_bus("Bus5", 230)
circuit1.add_bus("Bus6", 230)
circuit1.add_bus("Bus7", 18)

# Creating Conductor used in the T-Lines of the circuit
circuit1.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)

# Creating the geometry of the lines used in the circuit
circuit1.add_geometry("Geometry 1", 0, 0, 19.5, 0, 39, 0)

# Creating the Bundling used by the T-Lines in the circuit
circuit1.add_bundle("Bundle 1", 2, 1.5, circuit1.conductors["Partridge"].name)

# Creating the transformers used in the circuit
circuit1.add_transformer("T1", circuit1.buses["Bus1"].name, circuit1.buses["Bus2"].name, 125, 8.5, 10)
circuit1.add_transformer("T2", circuit1.buses["Bus6"].name, circuit1.buses["Bus7"].name, 200, 10.5, 12)

# Printing the values for the transformers
print("T1 Impedance pu: ", circuit1.transformers["T1"].zseries, "Admittance: ", circuit1.transformers["T1"].yseries)
print(circuit1.transformers["T1"].y_matrix)
print("T2 Impedance pu: ", circuit1.transformers["T2"].zseries, "Admittance: ", circuit1.transformers["T2"].yseries)
print(circuit1.transformers["T2"].y_matrix)

# Creating the T-Lines used in the circuit
circuit1.add_transmission_line("Line 1", circuit1.buses["Bus2"].name, circuit1.buses["Bus4"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 2", circuit1.buses["Bus2"].name, circuit1.buses["Bus3"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 25)
circuit1.add_transmission_line("Line 3", circuit1.buses["Bus3"].name, circuit1.buses["Bus5"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 20)
circuit1.add_transmission_line("Line 4", circuit1.buses["Bus4"].name, circuit1.buses["Bus6"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 20)
circuit1.add_transmission_line("Line 5", circuit1.buses["Bus5"].name, circuit1.buses["Bus6"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 6", circuit1.buses["Bus4"].name, circuit1.buses["Bus5"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 35)

circuit1.add_generator_element("Generator 1", circuit1.buses["Bus1"].name, 100, circuit1.buses["Bus1"].vpu, 0.1 )
circuit1.add_generator_element("Generator 2", circuit1.buses["Bus7"].name, 200, circuit1.buses["Bus7"].vpu, 0.1 )

circuit1.add_load_element("Load 1", circuit1.buses["Bus3"].name, 110, 50)
circuit1.add_load_element("Load 2", circuit1.buses["Bus4"].name, 100, 70)
circuit1.add_load_element("Load 3", circuit1.buses["Bus5"].name, 100, 65)

print("\nLine 1 Impedance pu: ", circuit1.transmission_lines["Line 1"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 1"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 1"].shunt_admittance, "\n",circuit1.transmission_lines["Line 1"].y_matrix)
print("\nLine 2 Impedance pu: ", circuit1.transmission_lines["Line 2"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 2"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 2"].shunt_admittance, "\n",circuit1.transmission_lines["Line 2"].y_matrix)
print("\nLine 3 Impedance pu: ", circuit1.transmission_lines["Line 3"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 3"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 3"].shunt_admittance, "\n",circuit1.transmission_lines["Line 3"].y_matrix)
print("\nLine 4 Impedance pu: ", circuit1.transmission_lines["Line 4"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 4"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 4"].shunt_admittance, "\n",circuit1.transmission_lines["Line 4"].y_matrix)
print("\nLine 5 Impedance pu: ", circuit1.transmission_lines["Line 5"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 5"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 5"].shunt_admittance, "\n",circuit1.transmission_lines["Line 5"].y_matrix)
print("\nLine 6 Impedance pu: ", circuit1.transmission_lines["Line 6"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 6"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 6"].shunt_admittance, "\n",circuit1.transmission_lines["Line 6"].y_matrix)

circuit1.calc_ybus()
print("\nybus:\n",circuit1.ybus,"\n")


# injecting voltages and angles for buses
#voltage_data = [1.00000, 0.93692, 0.92049, 0.92980, 0.92673, 0.93968, 1.00000]
#angle_data = [0.00, -4.44372, -5.46427, -4.70277, -4.83394, -3.9515, 2.15156]
#for i, bus_name in enumerate(circuit1.bus_order):
#    circuit1.buses[bus_name].set_voltage_and_delta(voltage_data[i], angle_data[i])

# injection = circuit1.compute_power_injection(circuit1.buses, circuit1.ybus)
print("\nPower Mismatch\n", circuit1.compute_power_mismatch(circuit1.buses, circuit1.ybus))

jacobian = Jacobian(circuit1)
print(jacobian.compute_jacobian())

# Solve the power flow and print results
powerflow = Power_Flow(circuit1, jacobian)
print("\n--- Solving Power Flow ---")
powerflow.solve(circuit1.buses, circuit1.ybus)
print(jacobian.compute_jacobian())
print("\nPower Mismatch\n", circuit1.compute_power_mismatch(circuit1.buses, circuit1.ybus))


# injecting voltages and angles for buses
#voltage_data = [1.00000, 0.93692, 0.92049, 0.92980, 0.92673, 0.93968, 1.00000]
#angle_data = [0.00, -4.45, -5.47, -4.70, -4.84, -3.95, 2.15]
#for i, bus_name in enumerate(circuit1.bus_order):
#    circuit1.buses[bus_name].set_voltage_and_delta(voltage_data[i], angle_data[i])

#print("\nPower Mismatch\n", circuit1.compute_power_mismatch(circuit1.buses, circuit1.ybus))

#voltage_data = [1.00000, 0.94276, 0.92683, 0.93594, 0.93315, 0.9460, 1.00000]
#angle_data = [0.00, -3.7213, -4.58287, -3.93422, -4.03836, -3.28016, 2.00501]
#for i, bus_name in enumerate(circuit1.bus_order):
#    circuit1.buses[bus_name].set_voltage_and_delta(voltage_data[i], angle_data[i])

#print("\nPower Mismatch\n", circuit1.compute_power_mismatch(circuit1.buses, circuit1.ybus))

#print("\nReal Power (MW) at each bus:")
#for bus, p in circuit1.real_power.items():
#    print(f"Bus {bus}: {p} MW")

#print("\nReactive Power (MVAR) at each bus:")
#for bus, q in circuit1.reactive_power.items():
#   print(f"Bus {bus}: {q} MVAR")

#x = .93692*1*(np.sqrt(14.6329**2+1.46329**2))*np.cos(-4.44372*np.pi/180 - 0 - (np.atan(14.6329/(-1.46329)))+np.pi)
#y = .93692*.93692*(np.sqrt(37.777303**2+127.050299**2))*np.cos((np.atan(-127.050299/(37.777303))))
#z = .93692*.92049*(np.sqrt(32.13782**2+10.375432**2))*np.cos(-4.44372*np.pi/180 - (-5.46427*np.pi/180) - (np.atan((32.13782/-10.375432)))+np.pi)
#a = .93692*.9298*(np.sqrt(25.93858**2+80.34455**2))*np.cos(-4.44372*np.pi/180 - (-4.70277*np.pi/180) - (np.atan((80.34455/-25.93858)))+np.pi)
#b = x+y+z+a
#print(x,y,z,a,b)