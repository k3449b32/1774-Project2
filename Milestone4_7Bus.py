from circuit import Circuit

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
print("Impedance pu: ", circuit1.transformers["T1"].zseries, "Admittance: ", circuit1.transformers["T1"].yseries)
print(circuit1.transformers["T1"].y_matrix)
print("Impedance pu: ", circuit1.transformers["T2"].zseries, "Admittance: ", circuit1.transformers["T2"].yseries)
print(circuit1.transformers["T2"].y_matrix)

# Creating the T-Lines used in the circuit
circuit1.add_transmission_line("Line 1", circuit1.buses["Bus2"].name, circuit1.buses["Bus4"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 2", circuit1.buses["Bus2"].name, circuit1.buses["Bus3"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 3", circuit1.buses["Bus3"].name, circuit1.buses["Bus5"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 4", circuit1.buses["Bus4"].name, circuit1.buses["Bus6"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 5", circuit1.buses["Bus5"].name, circuit1.buses["Bus6"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
circuit1.add_transmission_line("Line 6", circuit1.buses["Bus4"].name, circuit1.buses["Bus5"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)