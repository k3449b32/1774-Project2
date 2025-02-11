from circuit import Circuit
import numpy as np
import pandas as pd

# Creating Instance of circuit class
circuit1 = Circuit("circuit1")

# Validating all dictionaries are initialized in circuit class
print("Validating all dictionaries are initialized in circuit class")
print(circuit1.name) # Expected output: "Test Circuit"
print(type(circuit1.name)) # Expected output: <class ‘str’>
print(circuit1.buses) # Expected output: {}
print(type(circuit1.buses)) # Expected output: <class ‘dict’>
print(circuit1.conductors) # Expected output: {}
print(type(circuit1.conductors)) # Expected output: <class ‘dict’>
print(circuit1.bundles) # Expected output: {}
print(type(circuit1.bundles)) # Expected output: <class ‘dict’>
print(circuit1.geometry) # Expected output: {}
print(type(circuit1.geometry)) # Expected output: <class ‘dict’>
print(circuit1.transformers) # Expected output: {}
print(type(circuit1.transformers)) # Expected output: <class ‘dict’>
print(circuit1.transmissionlines) # Expected output: {}
print(type(circuit1.transmissionlines)) # Expected output: <class ‘dict’>

# Testing the circuit classes add and retrieve methods
circuit1.add_bus("Bus1", 230)
circuit1.add_bus("Bus2", 500)
circuit1.add_bus("Bus3", 500)
print("\n", type(circuit1.buses["Bus1"])) # Expected output: <class ‘Bus.Bus’>
print(circuit1.buses["Bus1"].name, circuit1.buses["Bus1"].base_kv,
      circuit1.buses["Bus2"].name, circuit1.buses["Bus2"].base_kv,
      circuit1.buses["Bus3"].name, circuit1.buses["Bus3"].base_kv)
    # Expected output: "Bus1" 230 "Bus2" 500 "Bus3" 500
print(circuit1.buses)

circuit1.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
print("\n", type(circuit1.conductors["Partridge"])) # Expected output: <class ‘Bus.Bus’>
print(circuit1.conductors["Partridge"].name, circuit1.conductors["Partridge"].diam, circuit1.conductors["Partridge"].GMR,
      circuit1.conductors["Partridge"].resistance, circuit1.conductors["Partridge"].ampacity)
    # Expected output: "Partridge" 0.642 0.0217 0.385 460

circuit1.add_bundle("Bundle 1", 2, 1.5, circuit1.conductors["Partridge"])
print("\n", type(circuit1.bundles["Bundle 1"]))
print(circuit1.bundles["Bundle 1"].name, circuit1.bundles["Bundle 1"].num_conductors, circuit1.bundles["Bundle 1"].spacing,
      circuit1.bundles["Bundle 1"].conductor.name, circuit1.bundles["Bundle 1"].DSL, circuit1.bundles["Bundle 1"].DSC)
    # Expected Output: "Bundle 1" 2 1.5 "Partridge" 0.2003122562401013 0.18041618552668717

circuit1.add_geometry("Geometry 1", 0, 0, 50, 0, 25, 30)
print("\n", type(circuit1.geometry["Geometry 1"]))
print(circuit1.geometry["Geometry 1"].name, circuit1.geometry["Geometry 1"].xa, circuit1.geometry["Geometry 1"].ya,
      circuit1.geometry["Geometry 1"].xb, circuit1.geometry["Geometry 1"].yb, circuit1.geometry["Geometry 1"].xc,
      circuit1.geometry["Geometry 1"].yc, circuit1.geometry["Geometry 1"].DEQ)
    # Expected Output: "Geometry 1" 0 0 50 0 25 30 42.40463044244056

circuit1.add_transformer('Transformer 1',circuit1.buses["Bus1"],circuit1.buses["Bus2"],500,2,3)
print("\n", type(circuit1.transformers["Transformer 1"]))
print(circuit1.transformers["Transformer 1"].name, circuit1.buses[circuit1.transformers["Transformer 1"].bus1.name].name,
      circuit1.buses[circuit1.transformers["Transformer 1"].bus2.name].name,
      circuit1.transformers["Transformer 1"].power_rating, circuit1.transformers["Transformer 1"].impedance_percent,
      circuit1.transformers["Transformer 1"].x_over_r_ratio, circuit1.transformers["Transformer 1"].impedance,
      circuit1.transformers["Transformer 1"].admittance, "\n", circuit1.transformers["Transformer 1"].y_matrix)
    # Expected Output: "Transformer 1" Bus1 Bus2 500 2 3 (0.006324+0.01897j) 0
    #  15.811388 - 47.434165j  -15.811388 + 47.434165j
    # -15.811388 + 47.434165j   15.811388 - 47.434165j

circuit1.add_transmission_line("Line 1", circuit1.buses["Bus2"],circuit1.buses["Bus3"], circuit1.bundles["Bundle 1"],
                              circuit1.geometry["Geometry 1"], 300)
print("\n", type(circuit1.transmissionlines["Line 1"]))
print(circuit1.transmissionlines["Line 1"].name, circuit1.transmissionlines["Line 1"].bus1.name,
      circuit1.transmissionlines["Line 1"].bus2.name, circuit1.transmissionlines["Line 1"].bundle.name,
      circuit1.transmissionlines["Line 1"].geometry.name, circuit1.transmissionlines["Line 1"].length,
      circuit1.transmissionlines["Line 1"].impedance, circuit1.transmissionlines["Line 1"].shunt_admittance,
      "\n", circuit1.transmissionlines["Line 1"].y_matrix)
    # Expected Output: Line 1 Bus2 Bus3 Bundle 1 Geometry 1 300 (57.75+236.5265215380633j) 0.0015824780682032612j
    #  0.142692 - 0.391017j  -0.142692 + 0.490974j
    # -0.142692 + 0.490974j   0.142692 - 0.391017j

# Print all added components through the circuit class
print("\n", list(circuit1.buses.keys()),list(circuit1.conductors.keys()),list(circuit1.bundles.keys()),
      list(circuit1.geometry.keys()),list(circuit1.transformers.keys()),list(circuit1.transmissionlines.keys()))
    # Expected Output: ['Bus1', 'Bus2', 'Bus3'] ['Partridge'] ['Bundle 1'] ['Geometry 1'] ['Transformer 1'] ['Line 1']