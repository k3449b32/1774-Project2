# Test Generator
from circuit import Circuit
circuit1 = Circuit("circuit1")
circuit1.add_bus("Bus1", 200)
circuit1.add_bus("Bus2", 200)


circuit1.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)

# Creating the geometry of the lines used in the circuit
circuit1.add_geometry("Geometry 1", 0, 0, 19.5, 0, 39, 0)

# Creating the Bundling used by the T-Lines in the circuit
circuit1.add_bundle("Bundle 1", 2, 1.5, circuit1.conductors["Partridge"].name)

circuit1.add_load_element("load1","Bus2",100,20)
circuit1.add_generator_element("gen1","Bus1",100,1.0)

print("\nGenerator parameters: ", circuit1.transmission_lines["Line 1"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 1"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 1"].shunt_admittance, "\n",circuit1.transmission_lines["Line 1"].y_matrix)
print("\nLoad parameters: ", circuit1.transmission_lines["Line 1"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 1"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 1"].shunt_admittance, "\n",circuit1.transmission_lines["Line 1"].y_matrix)



