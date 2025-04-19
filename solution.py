from circuit import Circuit
from jacobian import Jacobian
#solution class to run a power flow study or fault study based on mode specified by the user
#if solve_mode is power_flow, Solution will calculate y_bus and then jacobian
#if solve_mode is fault_study, Solution will run whatever is needed to calculate fault_study
#the Solution class takes in a circuit object and string that specifies which mode to run the simulation in

#in the file where this code is being tested: add buses, loads, generators, etc to circuit
#declare a solution object, then do solutionObject.solve()

class Solution:
    def __init__(self, circuit:Circuit):
        self.circuit=circuit


    def solve_power_flow(self):

        self.circuit.calc_ybus()
        jacobian = Jacobian(self.circuit)
        jacobian.compute_jacobian()


    def solve_fault(self,bus_name,mode):
        self.mode=mode

        if mode == '3_phase_fault':
            self.circuit.calc_ybus()
            self.circuit.modify_y_bus()
            fault_current,fault_voltage = self.circuit.calculate_fault(bus_name)
            print("\nybus:\n", self.circuit.ybus, "\n")
            print("\nfault_current:\n", fault_current)
            print("\nfault_voltage:\n", fault_voltage)
