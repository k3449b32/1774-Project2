from Geometry import Geometry
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Transformer import Transformer

Obj = Geometry("test", 0, 0, 50, 0, 25, 30)
print("Validating Geometry Class:", Obj.DEQ)

bus1 = Bus('bus1',245)
bus2 = Bus('bus2',245)
bus3 = Bus('bus3',280)

print(bus1.name,bus1.base_kv,bus1.counter)

transformer1 = Transformer('transformer1',bus1,bus2,500,2,3)
print(transformer1.name, transformer1.bus1.name,
transformer1.bus2.name, transformer1.power_rating)

print(transformer1.impedance,transformer1.admittance)



bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)