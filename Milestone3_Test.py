from circuit import Circuit

circuit1 = Circuit("circuit1")
circuit1.add_bus("Bus1", 230)
circuit1.add_bus("Bus2", 500)
circuit1.add_transformer("T1", circuit1.buses["Bus1"].name, circuit1.buses["Bus2"].name, 125, 8.5, 10)
print("Impedance pu: ", circuit1.transformers["T1"].impedance_pu, "Admittance: ", circuit1.transformers["T1"].admittance_pu)
print(circuit1.transformers["T1"].y_matrix)

circuit1.add_geometry("Geometry 1", 0, 0, 50, 0, 25, 30)
circuit1.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
circuit1.add_bundle("Bundle 1", 2, 1.5, circuit1.conductors["Partridge"].name)

circuit1.add_transmission_line("Line 1", circuit1.buses["Bus1"].name, circuit1.buses["Bus2"].name,
                               circuit1.bundles["Bundle 1"].name, circuit1.geometry["Geometry 1"].name, 10)
print("\nImpedance pu: ", circuit1.transmission_lines["Line 1"].impedance_pu, "Series Admittance pu: ", circuit1.transmission_lines["Line 1"].series_admittance,
      "\nShunt Admittance pu: ", circuit1.transmission_lines["Line 1"].shunt_admittance, "\n",circuit1.transmission_lines["Line 1"].y_matrix)

circuit1.calc_ybus()
print("\n",circuit1.ybus)