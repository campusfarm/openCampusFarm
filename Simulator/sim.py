from dataclasses import dataclass
from enum import Enum, auto
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class EVState(Enum):
    CHARGED = auto()
    NOT_CHARGED = auto()
    DRIVING = auto()
    # INIT = auto()


class PowerState(Enum):
    GRID_SUPPORT = auto()
    OFF_GRID = auto()
    COMBO = auto()
    INIT = auto()

class tempState(Enum):
    COOLTH = auto()
    ECONOMIC = auto()
    NORMAL = auto()

class CleanGrid(Enum):
    RELATIVE_CLEAN = auto()
    RELATIVE_DIRTY = auto()

class SafeState(Enum):
    SAFE = auto()
    DANGER = auto()

def min_to_real_time(t):
        hours, mins = divmod(t, 60)
        return f"{hours:02d}:{mins:02d}"

class PV:
    def __init__(self, inv_eff, T_daylight, max_power, data):
        self.inv_eff = inv_eff
        self.T_daylight = T_daylight
        self.P_out = 0.0 #cumulative power
        self.P = 0.0 #instant power 
        self.max_power = max_power
        self.data = data
        self.state = auto()
        
        
    
    def update(self, t):
        minute = np.floor((t / 5)).astype(int)
        #sin function simulation
        #self.P = (self.inv_eff)*(self.max_power/2)* (np.sin(np.pi * t/(self.T_daylight))+1)
        #real-world data simulation
        self.P = self.data.at[minute, 'SolArk PV Power (DNI) kW']
        return self.P
        
    def get_current_power_output(self):
        return self.P
    
    def min_to_real_time(self,t):
        hours, mins = divmod(t, 60)
        return f"{hours:02d}:{mins:02d}"

    # Sam could add debug flags as part of the common interface for each element to set the output levels
    def simulate(self): # Sam should be called simulator? -Yes
        #convert to time step of minutes
        t = np.floor(self.T_daylight * 60).astype(int)
        for i in range(t):
            self.update(i)
            print(f"Time: {self.min_to_real_time(i)}, PV Power: {round(self.get_current_power_output(),3)} kW")

    """"example use:
    PV1 = PV(inv_eff=0.96, T_daylight=11.5, max_power=13.2, data=dataframe)
    PV1.simulator()
    """""
        
class EV:
    batt_charge: float
    batt_capacity: float
    connected: bool 
    ev_range: int
    charge_eff = int
    discharge_eff = int
    charger_output_pwr_max = int
    state: Enum
    next_state: Enum
    tot_energy_consumed: float
    charge_pwr_consumed: float
    ev_deliveries = [] # list to hold all the deliveries (tuple with the start (index0), end time (index1), drive_length(index2), drive_distance(index3))
    charging_ctr: int
    drive_drained_percentage: float
    drive_drained_energy: float
    

    

    def str_to_bool(self, input_str):
       # input_str.lower() in ("yes", "true", "t", "1")
        # if (input_str.lower() == "yes"):
            
        #     return True
        # elif (input_str.lower() == "no"):
        #     return False
        # return True
        if (input_str == 1):
            return 1
        elif (input_str == 0):
            return 0
    
    def military_time_to_minutes(self, military_time):
        # Check if the military time is a valid integer
        if not isinstance(military_time, int) or military_time < 0 or military_time > 2359:
            raise ValueError("Time must be an integer between 0 and 2359.\n")
        
        # Extract hours and minutes
        hours = military_time // 100  # Get first one or two digits as hours
        minutes = military_time % 100  # Get last two digits as minutes
        
        # Validate that the minutes are less than 60
        if minutes >= 60:
            raise ValueError("Invalid time provided. Minutes should be less than 60.\n")
        
        # Calculate the total number of minutes
        total_minutes = hours * 60 + minutes
        return total_minutes
    
    def initialize_ev(self, batt_charge, batt_capacity, ev_range, connected, charge_eff, discharge_eff, charger_output_pwr_max):
       
        self.user_input = input("Will there be a delivery Today? Please enter '1' for 'yes' or '0' for 'no': \n")
        # self.delivery_bool = self.str_to_bool(self.user_input)
        # self.delivery_bool = True
        self.delivery_bool = int(self.user_input)
        self.tot_energy_consumed = 0
        self.charge_pwr_consumed = 0
        self.charging_ctr = 0
        self.drive_drained_percentage = 0
        self.drive_drained_energy = 0
        self.charging_ctr = 0
    

        # initialize variables 
        self.batt_charge = batt_charge # %
        self.batt_capacity = batt_capacity # kWh
        self.ev_range = ev_range # mi 
        self.connected = connected
        self.charge_eff = charge_eff
        self.discharge_eff = discharge_eff
        self.charger_output_pwr_max = charger_output_pwr_max # kW
        self.state = EVState.NOT_CHARGED
        self.next_state = EVState.NOT_CHARGED
        #self.drive_distance = 250

        #print(self.state)
        
        # will need to put this into a for loop in the future for multiple deliveries
        print(type(self.delivery_bool))
        if(self.delivery_bool == True):
            drive_time = int(input("When is the delivery scheduled? Please enter a time in military time with no colon. Example: 1330 for 1:30 PM: \n"))
            drive_length = int(input("How long will the drive be in minutes? Please enter a whole number. \n"))
            drive_distance = float(input("How many miles will the drive be? Please enter a whole or decimal number. \n"))
            drive_start = self.military_time_to_minutes(drive_time)
            delivery_tuple = (drive_start, drive_start + drive_length, drive_length, drive_distance)
            self.ev_deliveries.append(delivery_tuple)
            print(f"A drive is scheduled for: {min_to_real_time(drive_start)}.\nThe drive will be {drive_distance} miles long and will take {drive_length} minutes.\n")


        if(self.connected):
            print("The Ford Transit is connected to the charger\n")
            print(f"The current state of charge is {self.batt_charge}.\n")
    
    def update(self,t):
        # state changes
        # print(self.charge_pwr_consumed)
        if(self.state != self.next_state):
            #print(f"EV Battery Percentage: {self.batt_charge}\n")
            if(self.state == EVState.CHARGED):
                print("Stopping EV charging ... Current Battery Level is", self.batt_charge)

                # energy consumed eq                                                             
                #!!!!!!!!! energy_consumed = self.charge_pwr_consumed*(self.charging_ctr/60)
                # TODO: !!!!!!!!!unsure about the equation
               # energy_consumed = self.charge_pwr_consumed / 60
                print("BATT Percentage After")
                energy_consumed = self.charge_pwr_consumed
                print(energy_consumed)
                self.tot_energy_consumed += energy_consumed
                print("self total")
                print(self.tot_energy_consumed)
                #print("pwr_consued",self.charge_pwr_consumed, "ctr",self.charging_ctr)
                print(f"Total energy consumed from EV during charge: {self.tot_energy_consumed} kWh\n")

                self.charge_pwr_consumed = 0
                energy_consumed = 0
                self.charging_ctr = 0
                if(self.next_state == EVState.DRIVING):
                    print("Disconnecting from charger. Starting drive ... Current Battery Percentage:", self.batt_charge,"\n")
                    self.drive_drained_percentage = (self.ev_deliveries[0][3]/self.ev_range)*100
                    self.drive_drained_energy = (self.ev_deliveries[0][3]/self.ev_range)*self.batt_capacity
                    # battery % update
                    # TODO: !!!!!!!!!!Discussion with Nelson
                    #self.batt_capacity = self.batt_capacity - self.drive_drained_percentage
                    self.batt_charge -= self.drive_drained_percentage
            
            elif(self.state == EVState.NOT_CHARGED):
                if(self.next_state == EVState.DRIVING):
                    print("Time:",min_to_real_time(t),"Disconnecting from charger. Starting drive ...\n")
                    self.drive_drained_percentage = (self.ev_deliveries[0][3]/self.ev_range)*100
                    self.drive_drained_energy = (self.ev_deliveries[0][3]/self.ev_range)*self.batt_capacity
                    
                    # battery % update
                    # TODO: changed!
                    self.batt_charge = self.batt_charge - self.drive_drained_percentage

                elif(self.next_state == EVState.CHARGED):
                    print("Time:", min_to_real_time(t), "Starting EV charging ... Current Battery Percentage:", self.batt_charge)
    
            elif(self.state == EVState.DRIVING):
                print("Time", min_to_real_time(t)," Produce delivered! The drive has ended. Reconnecting to charger ... Current Battery Percentage:", self.batt_charge,"\n")
                # greenhouse gas equation
                ghg_saved = 10 # will need to be updated 

                print(f"Greenhouse Gases Saved During Drive: {ghg_saved}\n")
                print(f"Energy drained from battery: {self.drive_drained_energy}\n")
                if(self.next_state == EVState.CHARGED):
                    print("Starting EV charging ... Current Battery Percentage:", self.batt_charge)
        

            
            self.state = self.next_state

        if(self.state == EVState.CHARGED):
            # batt charge eq 
            # charging until battery is full
            if (self.batt_charge < 95):
                p_in = (self.charger_output_pwr_max*(1/60)*self.charge_eff)

                # TODO: Change here !
                e_consumed = self.charger_output_pwr_max*(1/60)
                # print("@@@@@", p_in)
                # print("!!!!",self.charging_ctr)
                #print("BATT Percentage Before")
                self.charge_pwr_consumed += e_consumed
                #print(self.charge_pwr_consumed)
                self.batt_charge = self.batt_charge + (p_in/self.batt_capacity)*100
                self.charging_ctr += 1

                print("CHARGINg COunTER")
                print(self.charging_ctr)
            else:
                self.next_state = EVState.NOT_CHARGED
                print("MADE IT TO THIS")
                
            
        #should we change to CHARGING/IDLE? 
        elif(self.state == EVState.NOT_CHARGED):
            #idle discharge eq (losses 2% every month)
            self.batt_charge = self.batt_charge - (1/20160)  


class Cooler:
    def __init__(self, Ta, setpoint, power):
        self.is_on = False # m
        self.min_temp = setpoint - 2
        self.max_temp = setpoint + 2
        self.p_consume = power # power consumed by the thermal cooling load kw/m
        self.Ta = Ta # Ambient temp
        self.Tk = 48 # current internal temp
        self.h = 0.016 # time
        self.COP = 2 #coefficient of performance
        self.Ri = 10 # thermal resistance of the thermal cooling load
        self.Ci = 0.2 # capacitance of the thermal cooling loadf
        self.state = tempState.NORMAL
        self.safestate = SafeState.SAFE
    
    def temp_cal(self):
        exponent = -self.h / (self.Ci * self.Ri)
        alpha = np.exp(exponent)
        # print(f"exponent: {exponent}")
        # print(f"alpha: {alpha}")
        Tg = self.Ri * self.p_consume * self.COP
        # print(f"alpha*self.Tk: {alpha*self.Tk}, (1 - alpha)*(self.Ta - self.is_on*Tg): {(1 - alpha)*(self.Ta - self.is_on*Tg)}")
        self.Tk = alpha*self.Tk + (1 - alpha)*(self.Ta - self.is_on*Tg)
        

    def set_temp(self):  
        if self.max_temp < self.Tk:
            self.is_on = True
        elif self.min_temp > self.Tk:
            self.is_on = False
        elif self.min_temp < self.Tk < self.max_temp:
            self.is_on = self.is_on
    
    def update(self):
        self.set_temp()
        self.temp_cal()

    def instant_power(self):
        if self.is_on:
            return self.p_consume
        else:
            return 0

    def change_setpoint(self, setpoint):
        self.max_temp = setpoint + 2
        self.min_temp = setpoint - 2

    def print_time(self, minute):
        hour = minute // 60
        minute_of_hour = minute % 60
        print(f"Current time (24-hour format): {hour:02d}:{minute_of_hour:02d}")

def check_clean_period(t):
    
                            
    #                             if t >= clean_time[0][0] and t <=clean_time[0][1]:
    #                             ev.next_state = EVState.CHARGED
    #                         elif t > clean_time[0][1]:
    #                             clean_time.pop(0)
    #                         else:
    #                             ev.next_state = EVState.NOT_CHARGED
    # return None
    return None

if __name__ == "__main__":
    data = pd.read_csv('./PVdata.csv',usecols=['Minute','SolArk PV Power (DNI) kW'])
    #declare PV, EV, main_cooler, basement_cooler
    pv = PV(inv_eff=0.96, T_daylight=24, max_power=13.2, data=data) 
    ev = EV() #TODO 
    ev.initialize_ev(40,131,320,True,.9,.9,19.2)

    power_type = PowerState.INIT
    cooling_type = tempState.NORMAL
    # main_cooler = Cooler(min_temp = 45, max_temp = 50, Ta = 70, Tk = 48)
    # basement_cooler = Cooler(min_temp = 34, max_temp = 38, Ta = 70, Tk = 48)
    main_cooler = Cooler(Ta=70, setpoint=48, power=1.8)
    base_cooler = Cooler(Ta=70, setpoint=45, power=3)
    clean_time = [(24, 200), (500,800)] # a list of relatively clean periods extracted from 72 hrs marginal emissions rate forecast
    #ev_delivery_time = [355,700] #a list of delivery time in form of minutes
    power_consumed_by_cooler = 0
    # ulti_min, ulti_max = 34, 38 # danger zone set by the user
    # ideal_setpoint = 36 # ideal setpoint set by the user
    ulti_min = int(input("What is the minimum danger zone tempertaure? Pleaser enter:\n"))
    ulti_max = int(input("What is the maximum danger zone tempertaure? Pleaser enter:\n"))
    ideal_setpoint = int(input("What is an ideal temperature setpoint? Please enter:\n"))
    current_setpoint = ideal_setpoint
    # pv.simulate()
    danger_time = 0
    danger_time_cool = 0
    danger_calm_time = 0
    calm_enough = True

    #graph
    time_axis = []
    temp_axis = []
    batt_axis = []
    pv_axis = []
    cooler_load = []
    current_temp = []
    healthy_max = []
    healthy_min = []
   
    for t in range(1440):
        pv.update(t)
        ev.update(t) # should take ev state into account
        main_cooler.update()
        base_cooler.update()
        temp_axis.append(current_setpoint)
        batt_axis.append(ev.batt_charge)
        pv_axis.append(pv.get_current_power_output())
        time_axis.append(t)
        cooler_load.append(main_cooler.instant_power())
        current_temp.append(main_cooler.Tk)
        healthy_max.append(ideal_setpoint+2)
        healthy_min.append(ideal_setpoint-2)

    
        if (pv.state != power_type):
            
            if (power_type == PowerState.COMBO):
                print("The system is using both PV power and Grid power Cooler Power Load is ", main_cooler.instant_power())
            elif (power_type == PowerState.OFF_GRID):
                print("The systm is using PV power only! Cooler Power Load is ", main_cooler.instant_power())
            elif (power_type == PowerState.GRID_SUPPORT):
                print("The system is using Grid power only! Cooler Power Load is ", main_cooler.instant_power())
            pv.state = power_type
            print(f"Time: {pv.min_to_real_time(t)}, PV Power: {round(pv.get_current_power_output(),3)} kW")

        if (main_cooler.state != cooling_type):
            if (cooling_type == tempState.COOLTH):
                print("Now the cooler is in the coolth mode!")
                print("The temperature setpoint is:", current_setpoint)
                main_cooler.state = cooling_type
            elif (cooling_type == tempState.ECONOMIC):
                print("Now the cooler is in the economic mode!")
                print("The temperature setpoint is:", current_setpoint)
                main_cooler.state = cooling_type
            elif (cooling_type == tempState.NORMAL):
                print("Now the cooler is in the normal mode!")
                print("The temperature setpoint is:", current_setpoint)
                main_cooler.state = cooling_type

        if (main_cooler.Tk < ideal_setpoint + 2 and main_cooler.Tk > ideal_setpoint - 2):
            danger_time = 0
            danger_calm_time += 1
        else:
            danger_time += 1
            danger_calm_time = 0
        
        #EMS_action
                
        
        # if (cooling_type == tempState.NORMAL):
        #     # danger_calm_time += 1
        #     current_setpoint = ideal_setpoint
        
        # if ((danger_calm_time > 120 and cooling_type == tempState.NORMAL)):
        #     calm_enough = True
        # elif (danger_calm_time <= 120 and cooling_type == tempState.NORMAL and t > 120):
        #     calm_enough = False
      

        if pv.P <= main_cooler.instant_power():
            if (pv.P > 0):
                power_type = PowerState.COMBO
            else:
                power_type = PowerState.GRID_SUPPORT
    
            # pv is not genrating enough power
            # pv+grid to cooler

            # TODO
            if main_cooler.min_temp < ideal_setpoint - 2:
                # if so, the cooler is at risk of coolth, need to back to normal
                current_setpoint = ideal_setpoint
                main_cooler.change_setpoint(current_setpoint)
                cooling_type = tempState.NORMAL
            else:
                # else, the cooler in within healthy zone
                # can play with the set point when applicable
                

                if main_cooler.max_temp < ulti_max:
                    # a temp fluctuation will stay within ideal healthy zone
                    # increase setpoint to reduce power consumption
                    # TODO: economy mode, only last for 60 min for now
                    # if (calm_enough == True):
                    #     # healthy state, avaible for adventure 
                    #     calm_enough = False
                        # danger_time = 0
                        # danger_calm_time = 0
                    # print("!!!")
                    
                    # if (calm_enough == False and danger_time <= 120):
                    if (main_cooler.safestate == SafeState.SAFE):
                        
                        #undergo danger zone
                        # danger_time += 1
                        if (danger_calm_time < 30):
                            current_setpoint = ideal_setpoint
                        else:
                            current_setpoint += 1
                        # current_setpoint += 1
                        # current_setpoint += 1 if current_setpoint < ulti_max - 2 else current_setpoint
                        main_cooler.change_setpoint(current_setpoint)
                        cooling_type = tempState.ECONOMIC
                        # print(danger_time)
                        #print("@@@")

                    # if (calm_enough == False and danger_time > 120):
                    if (main_cooler.safestate == SafeState.DANGER):
                        # finished adventure, but not ready for new adventure
                        
                        cooling_type = tempState.NORMAL
                        current_setpoint = ideal_setpoint
                        main_cooler.change_setpoint(current_setpoint)
                        # danger_calm_time = 0 
                    
                else:
                    # the current tempeture is high, need to back to normal
                    if (main_cooler.Tk + 2 > ulti_max):
                        cooling_type = tempState.NORMAL
                        # current_setpoint -= 1 if current_setpoint > ideal_setpoint else ideal_setpoint
                        current_setpoint = ideal_setpoint
                        main_cooler.change_setpoint(current_setpoint)
                        # danger_calm_time = 0 
                    if (main_cooler.safestate == SafeState.DANGER):
                        cooling_type = tempState.NORMAL
                        # current_setpoint -= 1 if current_setpoint > ideal_setpoint else ideal_setpoint
                        current_setpoint = ideal_setpoint
                        main_cooler.change_setpoint(current_setpoint)

                   
                    #print("&&&")
                    
            # check ev delivery schedule, when is the nearest delivery task
                # charge EV when necessary using grid power
            if not ev.ev_deliveries:
                # no delivery task
                ev.next_state = EVState.NOT_CHARGED
        
            else:
                if ev.ev_deliveries[0][0] - t < 120 and ev.ev_deliveries[0][0] - t > 0:
                    # delivery task soon
                    if ev.batt_charge < 50:
                        # chraging is urgent
                        ev.next_state = EVState.CHARGED
                    else:
                        # charging ev is not urgent
                        # wait for clean period - consecutive charging 
                        if not clean_time:
                            ev.next_state = EVState.NOT_CHARGED
                         
                        else:
                            if t >= clean_time[0][0] and t <=clean_time[0][1]:
                                ev.next_state = EVState.CHARGED
                            elif t > clean_time[0][1]:
                                clean_time.pop(0)
                            else:
                                ev.next_state = EVState.NOT_CHARGED
                                
      
                # if ev.ev_deliveries[0][0] <= t and ev.ev_deliveries[0][1] >= t:
                #     # pop the past delivery task, so that the first element in the delivery task list is always the upcoming?
                #     #ev.ev_deliveries.pop(0)
                #     ev.next_state = EVState.DRIVING
                
                # if ev.ev_deliveries[0][1] < t:
                #     ev.ev_deliveries.pop(0)

        elif pv.P > main_cooler.instant_power() and pv.P > 0:
            power_type = PowerState.OFF_GRID

        
        # pv is generating excessive power
        # charge ev using solar power if ev is not fully charged
            #!!!!!!!!!!!Reivse: charge ev using solar power if ev battery percentage is not above 80

            if main_cooler.max_temp > ideal_setpoint + 2:

                current_setpoint = ideal_setpoint
                main_cooler.change_setpoint(current_setpoint)
                cooling_type = tempState.NORMAL
            else:
                # no need to charge ev, will coolth cooler with solar power
                if main_cooler.min_temp > ulti_min:
                    # coolth, no longer than 60 min
                    # TODO: no longer than 60 min
                  #  print('????')
                    # if (calm_enough == True):
                    # # healthy state, avaible for adventure 
                    #     calm_enough = False
                    #     danger_time_cool = 0
                    #     danger_calm_time = 0
                     #   print("111")
                    
                    # if (calm_enough == False and danger_time_cool <= 120):
                    if (main_cooler.safestate == SafeState.SAFE):
                        #undergo danger zone
                        # danger_time_cool += 1
                        if (danger_calm_time < 30):
                            current_setpoint = ideal_setpoint
                        else:
                            current_setpoint -= 1
                        # current_setpoint -= 1 
                        main_cooler.change_setpoint(current_setpoint)
                        cooling_type = tempState.COOLTH
                     #   print("222")

                    # if(calm_enough == False and danger_time_cool > 120):
                    if (main_cooler.safestate == SafeState.DANGER):
                        # finished adventure, but not ready for new adventure
                        cooling_type = tempState.NORMAL
                        current_setpoint = ideal_setpoint
                        main_cooler.change_setpoint(current_setpoint)
                        # danger_calm_time = 0
                     #   print("333")
                else:
                    if (main_cooler.Tk - 2 < ulti_min):

                        cooling_type = tempState.NORMAL
                        if (main_cooler.safestate == SafeState.DANGER):
                            current_setpoint = ideal_setpoint
                        elif (main_cooler.safestate == SafeState.SAFE):
                            current_setpoint += 1 if current_setpoint <  ideal_setpoint else ideal_setpoint
                        main_cooler.change_setpoint(current_setpoint)
                    # danger_calm_time = 0
                        
            
            if ev.batt_charge < 80:
                ev.next_state = EVState.CHARGED
        
        if (len(ev.ev_deliveries) > 0):
            
            if ev.ev_deliveries[0][0] <= t and ev.ev_deliveries[0][1] >= t:
                    # pop the past delivery task, so that the first element in the delivery task list is always the upcoming?
                    #ev.ev_deliveries.pop(0)
                    ev.next_state = EVState.DRIVING
                
            if ev.ev_deliveries[0][1] < t:
                    ev.ev_deliveries.pop(0)
                    ev.next_state = EVState.NOT_CHARGED
                  

        if (cooling_type == tempState.NORMAL):
            current_setpoint = ideal_setpoint

        # checking clean periods every timestep
        if clean_time:
            if t > clean_time[0][1]:
                clean_time.pop(0)

    print("Total energy consumed by EV: ", ev.tot_energy_consumed)

    plt.subplot(5,1,1)
    plt.plot(time_axis, temp_axis)  
    plt.xlabel('Time/min')  
    plt.ylabel('Temp Setpoint') 
    plt.title('Temperature Setpoint')  

    plt.subplot(5,1,2)
    plt.plot(time_axis, batt_axis) 
    plt.xlabel('Time/min')  
    plt.ylabel('Battery Charge Percentage') 
    plt.title('Battery Charge Percentage')

    plt.subplot(5,1,3)
    plt.plot(time_axis, pv_axis)  
    plt.xlabel('Time/min') 
    plt.ylabel('PV output')
    plt.title('PV output')  

    plt.subplot(5,1,4)
    plt.plot(time_axis, cooler_load)  
    plt.xlabel('Time/min')  
    plt.ylabel('cooler load') 
    plt.title('cooler load') 
    # plt.show()

    plt.subplot(5,1,5)
    plt.plot(time_axis, current_temp)  
    plt.plot(time_axis, healthy_max)
    plt.plot(time_axis,healthy_min)
    min_hour = min(time_axis) // 60
    max_hour = max(time_axis) // 60
    hour_ticks =  list(range(min_hour, max_hour + 1))
    hour_ticks_in_min = [h*60 for h in hour_ticks]
    plt.xticks(hour_ticks_in_min, [f"{int(h)}" for h in hour_ticks])

    # plt.xlabel('Time/hour1')  
    plt.ylabel('current cooler temperature') 
    plt.title('current cooler temprature') 
    plt.show()
    print("The Day has ended")
    print(f"The final state of charge is {ev.batt_charge}.\n")
    print("Happy Farming!")