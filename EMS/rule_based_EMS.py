import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd



# variables on the go 
PV_OUTPUT = 0 # read from inverter -- substitution "solar generation"
moer_data = pd.read_csv('WT_nonEMS.csv') # Load the MOER data from the CSV file
Cooler_indoor_temp = 0 # read from data logger -- substitution "cooler.Tk"
EV_connected = True # read from charger -- substitution "ev.connected"
Cooler_power = 0 # calcaulted from inverter data: total consumption - charger consumption (this variable not necessary)
CoolEV_power = 0 # read from inverter -- substitution "total_power "

# Constants
SIMULATION_HOURS = 24  # Total simulation time in hours
TIME_STEP_MINUTES = 5  # Simulation time step in minutes
TIME_STEPS = (SIMULATION_HOURS * 60) // TIME_STEP_MINUTES  # Total number of 5-minute intervals
SOLAR_PEAK_HOURS = (8, 18)  # Solar energy available from 8 AM to 6 PM
SOLAR_MAX_OUTPUT = 10.0  # kW, peak solar output during the day





# Extract the 'Value' column as the MOER list (MOER in lbs/MWh)
moer = moer_data['Value'].tolist()
moer_kwh_list = [value / 1000 for value in moer]

DELIVERY_SCHEDULE = []

# Cooler characteristics
COOLER_POWER_CONSUMPTION = 3.67  # kW, cooler power consumption when on
AMBIENT_TEMPERATURE_F = 75  # Ambient temperature in Fahrenheit
COOLER_SETPOINT_F = 55  # idealCooler setpoint in Fahrenheit, indoor tempertaure will flucatuate between 53 ~ 57
SAFE_TEMP_SETPOINT_HIGH = 57 # indoor temperature will fluctuate between 55 ~ 59 
SAFE_TEMP_SETPOINT_LOW = 53 # indoor temperaturen will fluctuate between 51 ~ 55 
saved_emissions_moer = np.zeros(TIME_STEPS)  # Track saved emissions (MOER)

# Simulation arrays for tracking data
solar_generation = np.zeros(TIME_STEPS)
ev_charge = np.zeros(TIME_STEPS)
cooler_power = np.zeros(TIME_STEPS)  # Track cooler power usage
battery_level = np.zeros(TIME_STEPS)
internal_temperature = np.zeros(TIME_STEPS)  # Track cooler temperature
grid_power = np.zeros(TIME_STEPS)  # Track real-time grid power usage
solar_power_to_grid = np.zeros(TIME_STEPS)  # Track excess solar power pushed to the grid
ev_grid_load = np.zeros(TIME_STEPS)  # EV grid load in Watt-minutes
cooler_grid_load = np.zeros(TIME_STEPS)  # Cooler grid load in Watt-minutes
ev_ems_emissions = np.zeros(TIME_STEPS)  # EV EMS CO₂ emissions (lbs)
ev_avg_emissions = np.zeros(TIME_STEPS)  # EV average CO₂ emissions (lbs)
cooler_ems_emissions = np.zeros(TIME_STEPS)  # Cooler EMS CO₂ emissions (lbs)
cooler_avg_emissions = np.zeros(TIME_STEPS)  # Cooler average CO₂ emissions (lbs)
ems_emissions = np.zeros(TIME_STEPS)
daily_ems_emissions = np.zeros(TIME_STEPS)
# EV class with efficiency and charging limits
# EV class with fixed charging rate and energy source allocation
class EV:
    def __init__(self):
        self.batt_charge = 0  # Initial battery charge (kWh)
        self.batt_capacity = 0  # Battery capacity (kWh)
        self.ev_range = 0  # EV range (miles)
        self.connected = False  # Whether EV is connected for charging
        self.charge_eff = 0.9  # Charging efficiency (0-1)
        self.discharge_eff = 0.9  # Discharge efficiency (0-1)
        self.charger_output_pwr_max = 0  # Max charger output (kW)

    def initialize_ev(self, batt_charge, batt_capacity, ev_range, connected, charge_eff, discharge_eff, charger_output_pwr_max):
        self.batt_charge = batt_charge  # Current charge in kWh
        self.batt_capacity = batt_capacity  # Capacity in kWh
        self.ev_range = ev_range  # Total range in miles
        self.connected = connected  # Is the EV connected to the charger
        self.charge_eff = charge_eff  # Charging efficiency
        self.discharge_eff = discharge_eff  # Discharging efficiency
        self.charger_output_pwr_max = charger_output_pwr_max  # Max charger power (kW)

    # Function to charge the EV
    def charge(self, available_power):
        if self.batt_charge < self.batt_capacity:
            # Fixed charging rate during night or solar charging
            charging_power = min(available_power, self.charger_output_pwr_max)
            charge_energy = charging_power * self.charge_eff * (TIME_STEP_MINUTES / 60)  # Scale by 5 min steps
            charge_amount = min(self.batt_capacity - self.batt_charge, charge_energy)
            self.batt_charge += charge_amount
            return charging_power
        return 0


# Cooler class with ON/OFF behavior
class Cooler:
    def __init__(self, Ta, setpoint, power):
        self.is_on = False  # Cooler is initially off
        self.min_temp = setpoint - 2  # Minimum temperature before cooler turns off
        self.max_temp = setpoint + 2  # Maximum temperature before cooler turns on
        self.p_consume = power  # Power consumed by the cooler (kW)
        self.Ta = Ta  # Ambient temperature
        self.Tk = 55  # Current internal temperature
        self.h = 0.016  # Time step
        self.COP = 2  # Coefficient of performance
        self.Ri = 10  # Thermal resistance
        self.Ci = 0.2  # Capacitance of the cooler
        self.state = "NORMAL"  # Cooler state (custom)
        self.safestate = "SAFE"  # Safe state (custom)

    # Temperature calculation based on the cooler's properties
    def temp_cal(self):
        exponent = -self.h / (self.Ci * self.Ri)
        alpha = np.exp(exponent)
        Tg = self.Ri * self.p_consume * self.COP
        self.Tk = alpha * self.Tk + (1 - alpha) * (self.Ta - self.is_on * Tg)

    # Determine if the cooler should be on or off based on the temperature
    def set_temp(self):
        if self.Tk > self.max_temp:
            self.is_on = True
        elif self.Tk < self.min_temp:
            self.is_on = False

    # Update cooler state and calculate the internal temperature
    def update(self):
        self.set_temp()
        self.temp_cal()

    # Return the power consumed by the cooler (only if it's on)
    def instant_power(self):
        return self.p_consume if self.is_on else 0
    
    def change_setpoint(self, setpoint):
        self.min_temp = setpoint - 2
        self.max_temp = setpoint + 2


# Function to simulate solar power generation based on time step (5-minute intervals)
def generate_solar_power(time_step):
    hour_of_day = (time_step * TIME_STEP_MINUTES) / 60
    if SOLAR_PEAK_HOURS[0] <= hour_of_day <= SOLAR_PEAK_HOURS[1]:
        # Assuming a sinusoidal generation curve
        return SOLAR_MAX_OUTPUT * np.sin(np.pi * (hour_of_day - SOLAR_PEAK_HOURS[0]) / (SOLAR_PEAK_HOURS[1] - SOLAR_PEAK_HOURS[0]))
    return 0


# Initialize EV with parameters
ev = EV()
ev.initialize_ev(20, 131, 320, True, 0.9, 0.9, 19.2)

# Initialize Cooler
cooler = Cooler(Ta=AMBIENT_TEMPERATURE_F, setpoint=COOLER_SETPOINT_F, power=COOLER_POWER_CONSUMPTION)

# Select cleanest MOER periods between 6 PM and 10 AM
night_periods = []
for time_step in range(TIME_STEPS):
    hour = (time_step * TIME_STEP_MINUTES) // 60
    if hour >= 18 or hour < 10:  # 6 PM to 10 AM window
        night_periods.append((moer[time_step], time_step))

# Sort by MOER and select top 84 cleanest periods for EV charging
night_periods.sort(key=lambda x: x[0])
cleanest_periods = [period[1] for period in night_periods[:84]]

# Simulation loop for 5-minute time steps
for time_step in range(TIME_STEPS):
    hour = (time_step * TIME_STEP_MINUTES) // 60
    # Update cooler state (temperature changes based on whether it's on or off)
    cooler.update()
    
    # Solar energy generation
    solar_gen = generate_solar_power(time_step)
    solar_generation[time_step] = solar_gen
    
    # Cooler consumes energy every time step based on its state (on/off)
    cooler_power[time_step] = cooler.instant_power()
    
    # Track cooler internal temperature
    internal_temperature[time_step] = cooler.Tk

    ev_charge_power = 0
    # Determine EV charging logic
    if (hour >= 18 or hour < 10) and ev.connected == True:  # Night time (6 PM - 10 AM)
        if time_step in cleanest_periods:  # Charge EV only in cleanest periods
            ev_charge_power = ev.charge(ev.charger_output_pwr_max) 
    elif (10 <= hour < 18) and ev.connected == True:  # Daytime (10 AM - 6 PM)
        # Charge EV with solar energy if available after powering the cooler
        if solar_gen > cooler_power[time_step]:
          #  ev_charge_power = ev.charge(solar_gen - cooler_power[time_step]) # Question? Is ev charge power fixed number? 

            # case where EV_charge_power is fixed:
            ev_charge_power = ev.charge(ev.charger_output_pwr_max)
        else:
            ev_charge_power = 0
    elif ev.connected == False:
        ev_charge_power = 0
    
    # Total power needed by cooler and EV
    # total_power_needed = cooler_power[time_step] + ev_charge_power
    # case where EV_charge_power is fixed:
    total_power_needed = cooler_power[time_step] + ev_charge_power
    
    # Allocate available solar power first, then grid power if necessary
    if solar_gen >= total_power_needed:
        solar_power_to_grid[time_step] = solar_gen - total_power_needed  # Excess solar to grid
        grid_power[time_step] = 0  # No need for grid power

        if cooler.Tk >= SAFE_TEMP_SETPOINT_LOW - 2: # coolth 
            cooler.change_setpoint(SAFE_TEMP_SETPOINT_LOW) 
        else:
            cooler.change_setpoint(COOLER_SETPOINT_F)
    else:
        grid_power[time_step] = total_power_needed - solar_gen  # Use the grid to meet unmet demand
        solar_power_to_grid[time_step] = 0  # No excess solar power

        if cooler.Tk <= SAFE_TEMP_SETPOINT_HIGH + 2: # eco
            cooler.change_setpoint(SAFE_TEMP_SETPOINT_HIGH) # indoor temp will hit 59 max but still safe 
        else:
            cooler.change_setpoint(COOLER_SETPOINT_F) # back to default 
    
    # Store the actual charging power (which should always be the max charge rate)
    ev_charge[time_step] = ev_charge_power
    
    # Update battery level
    battery_level[time_step] = ev.batt_charge

    # Convert MOER from lbs/MWh to lbs/kWh
    moer_kwh = moer[time_step] / 1000
    
    # Emissions Calculation for grid usage
    if solar_power_to_grid[time_step] <= 0:
        saved_emissions_moer[time_step] = 0
    elif solar_power_to_grid[time_step] > 0:
        # Saved emissions when excess power is pushed to the grid (Grid power is negative)
        saved_emissions_moer[time_step] = solar_power_to_grid[time_step] * moer_kwh * 5 / 60

    # marginal for the whole system 
    ems_emissions[time_step] = max(0,moer_kwh_list[time_step] * grid_power[time_step] * 5 / 60)

# Summing saved emissions after the day is over
daily_saved_emissions_moer = np.sum(saved_emissions_moer)
daily_ems_emissions = np.sum(ems_emissions)

# Writing the results to a CSV file
with open('emissions_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Time_Step', 'Grid_Power', 'Solar_Power_to_Grid', 'Saved_Emissions_MOER', 'Saved_Emissions_AOER']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for time_step in range(TIME_STEPS):
        writer.writerow({
            'Time_Step': time_step,
            'Grid_Power': grid_power[time_step],
            'Solar_Power_to_Grid': solar_power_to_grid[time_step],
            'Saved_Emissions_MOER': saved_emissions_moer[time_step]
        })

# Plotting the results
plt.figure(figsize=(10, 6))

plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, solar_generation, label='Solar Generation (kW)', color='yellow')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, ev_charge, label='EV Charging (kW)', color='green')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, cooler_power, label='Cooler Power (kW)', color='blue')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, battery_level, label='EV Battery Level (kWh)', color='red')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, internal_temperature, label='Cooler Internal Temp (F)', color='orange')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, grid_power, label='Grid Power (kW)', color='purple')
plt.plot(np.arange(TIME_STEPS) * TIME_STEP_MINUTES / 60, solar_power_to_grid, label='Solar Power to Grid (kW)', color='cyan')

# Highlight clean periods for EV charging
for time_step in cleanest_periods:
    start_hour = time_step * TIME_STEP_MINUTES / 60
    end_hour = (time_step + 1) * TIME_STEP_MINUTES / 60
    plt.axvspan(start_hour, end_hour, color='green', alpha=0.3)

plt.text(0, 1.1, f"Total Saved Emissions: {daily_saved_emissions_moer:.2f} lbs CO₂", fontsize=12, color='green', transform=plt.gca().transAxes)
plt.text(0.5, 1.1, f"Total System Emissions: {daily_ems_emissions:.2f} lbs CO₂", fontsize=12, color='green', transform=plt.gca().transAxes)
plt.title('24-hour Solar, EV, Cooler Simulation')
plt.xlabel('Hour of the Day')
plt.ylabel('Power (kW) and Temperature (F)')
plt.legend()
plt.grid(True)
plt.show()


# Printing the total saved emissions at the end of the day
print(f"Total Saved Emissions: {daily_saved_emissions_moer:.2f} lbs CO₂")
print(f"Total System Emissions: {daily_ems_emissions:.2f} lbs CO₂")