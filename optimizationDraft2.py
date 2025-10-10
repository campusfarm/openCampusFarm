import cvxpy as cp
import numpy as np

print('hello world')

#define general variables
time_step = 1 #hr
time_steps = 24 #hr

#define EV variables
s = 6 #time steps until weekday at 7am
n = 12 #time steps until next delivery
ME = np.random.uniform(0.2, 1.0, size=time_steps) #(CO2 / kWh)
EV_SOC_capacity = 100 #(kWh) #max SOC battery power for EV
initial_SOC = 50 #initial SOC
SOC_delivery = 100
SOC_day = 60
EV_P_max = 19 #kW, max charging power of the EV charger

#define Cooler variables

#decision variables - adjustable quanitites
EV_P = cp.Variable(time_steps) #each time step make a decison on what P_EV will eventually be
SOC = cp.Variable(time_steps) #each time step make a decision on what SOC will be reached

#constraints - use += for each constraint to ensure 
constraints = [SOC[0] == initial_SOC] #initial SOC will be SOC at t=0
constraints += [SOC <= EV_SOC_capacity, SOC >= 0]
constraints += [EV_P <= EV_P_max, EV_P >= 0]

#update SOC with each time step
for t in range(1, time_steps):
     constraints += [SOC[t] == SOC[t-1] + (EV_P[t-1] * time_step)] 

constraints += [SOC[s] >= SOC_day] # SOC at s time steps away must be at least the daily min
constraints += [SOC[n] >= SOC_delivery] #SOC at n time steps away must be 95%

time_step_emissions = ME * EV_P
total_emissions = cp.sum(time_step_emissions)
problem = cp.Problem(cp.Minimize(total_emissions), constraints)
problem.solve()

if problem.status == cp.OPTIMAL:
    print("Optimal solution found! Total emissions:", problem.value, "kg CO2")
    print("Optimal charging schedule (kW):", EV_P.value)
    print("SOC at each time step (kWh):", SOC.value)
else:
     print("No optimal solution found." )