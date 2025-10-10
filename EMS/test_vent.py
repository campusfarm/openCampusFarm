import requests
import re

cooler_indoor_temp = 0

def toggle_vent():
    url = "http://192.168.0.160:5000/toggle_vent"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print("Vent toggled successfully!")
        else:
            print(f"Failed to toggle vent. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

def get_cooler_temp():
    url="http://192.168.0.160:5000/temperatures"
    global cooler_indoor_temp
    try:
        print("temp sensor worked!")
        response = requests.get(url)
        response.raise_for_status() 

        temps = response.text

        # Use regex to extract the numbers
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", temps)

        # Convert the extracted strings to floats
        parsed_numbers = [float(num) for num in numbers]

        # Separate and print them
        indoor_temp = parsed_numbers[0]
        outdoor_temp = parsed_numbers[1] 

        print(indoor_temp)
        print(outdoor_temp)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"An error occurred with the temp sensor trying automation: {e}")

# Call the function
toggle_vent()

