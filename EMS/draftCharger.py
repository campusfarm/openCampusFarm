import time 
import json
import os

global simulator 
simulator = True

def update_charge():
    charge = 0

    while simulator is True:
        if simulator:
            if charge < 100:
                charge += 2

                # Check if the file exists, and only update if it does
                # if os.path.exists('charge_data.json'):
                with open('charge_data.json', 'w') as file:
                    json.dump({'charge': charge}, file)
                # else:
                #     print("step_data.json doesn't exist. Skipping update.")

                time.sleep(3)
            

        else:
            break  # Stop the loop if the simulator is no longer running

if __name__ == "__main__":
    update_charge()
