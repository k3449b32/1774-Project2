from circuit import Circuit

circuit1 = Circuit("circuit1")
circuit1.add_bus("Bus1", 230)
circuit1.add_bus("Bus2", 500)
circuit1.add_bus("Bus3", 500)
circuit1.add_transformer("T1", circuit1.buses["Bus1"].name, circuit1.buses["Bus2"].name, 125, 8.5, 10)
print("Impedance pu: ", circuit1.transformers["T1"].zseries, "Admittance: ", circuit1.transformers["T1"].yseries)
print(circuit1.transformers["T1"].y_matrix)