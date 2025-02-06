from Geometry import Geometry
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Transformer import Transformer
from Conductor import Conductor

conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
print("Validating Conductor Class: ", conductor1.name, conductor1.diam, conductor1.GMR, conductor1.resistance, conductor1.ampacity)


geometry1 = Geometry("test", 0, 0, 50, 0, 25, 30)
print("\nValidating Geometry Class: ", geometry1.DEQ)

bus1 = Bus('bus1',245)
bus2 = Bus('bus2',245)
bus3 = Bus('bus3',280)
print("\nValidating Bus Class: ", bus1.name,bus1.base_kv,bus1.index,
      bus2.name,bus2.base_kv,bus2.index,bus3.name,bus3.base_kv,bus3.index)

bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
print("\nValidating Bundle Class: ", bundle1.name, bundle1.num_conductors, bundle1.spacing, bundle1.conductor.name)
print(bundle1.DSC, bundle1.DSL)

transformer1 = Transformer('transformer1',bus1.name,bus3.name,500,2,3)
print("\nValidating Transformer Class: ", transformer1.name, transformer1.bus1, transformer1.bus2, transformer1.power_rating)
print(transformer1.impedance,transformer1.admittance)
print(transformer1.y_matrix)

line1 = TransmissionLine("Line 1", bus1.name, bus2.name, bundle1, geometry1, 10)
print("\nValidating Transmission Line Class: ", line1.name, line1.bus1, line1.bus2, line1.length)
print(line1.impedance, line1.admittance)
print(line1.y_matrix)

