import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))

def make_account():
    
    # To register, use the code below. Please note that for these code examples we are using filler values for username
    # (freddo), password (the_frog), email (freddo@frog.org), org (freds world) and you should replace each if you are
    # copying and pasting this code.

    import requests
    register_url = 'https://api.watttime.org/register'
    params = {'username': os.environ.get("WT_USERNAME"),
            'password': os.environ.get("WT_PASSWORD"),
            'email': os.environ.get("WT_EMAIL"),
            'org': os.environ.get("WT_ORG")}
    rsp = requests.post(register_url, json=params)
    print(rsp.text)

def get_login_token():
    
    # To login and obtain an access token, use this code:
    import requests
    from requests.auth import HTTPBasicAuth
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth(os.environ.get("WT_USERNAME"), os.environ.get("WT_PASSWORD")))
    TOKEN = rsp.json()['token']
    print(rsp.json())
    return TOKEN


def get_moer(token):
    url = "https://api.watttime.org/v3/forecast"

    # Provide your TOKEN here, see https://docs.watttime.org/#tag/Authentication/operation/get_token_login_get for more information
    TOKEN = ""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "region": "MISO_DETROIT",
        "signal_type": "co2_moer",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

token = get_login_token()
#print(token)
data = get_moer(token)
#print(data)
time = []
value = []
t = 0
generated_time = data['meta']['generated_at']
print(generated_time)
generated_date = generated_time.split('T')[0]
start_clock = ((generated_time.split('T')[1].split('+')[0]).strip())[:5]
print((start_clock))
start_time = datetime.strptime(start_clock, '%H:%M')
with open("watttime_output.txt", "w") as file:
    for entry in data['data']:
        time.append(5*t)
    # print(f"Point Time: {data['point_time']}, Value: {data['value']}")
        file.write(f"Point Time: {entry['point_time']}, Value: {entry['value']} \n")
        military_time = entry['point_time'].split('T')[1].split('+')[0]
        hours = int(military_time[0:2])
        mins = int(military_time[3:5])
        value.append(entry['value'])
        t+=1

value_array = np.array(value)
time_block_list = []
# print(value)
# 30 min blocks, 48 blocks, pick 16 blocks
for i in range(48):
    temp = value_array[6*i:6*(i+1)]
    ave = np.mean(temp)
    time_block_list.append(ave)

print((time_block_list))
result = np.argpartition(time_block_list, 16)[:16]
result = np.sort(result)
print(result)

extracted_time = []
for el in result:
    time_block = (el * 30, (el+1) * 30)
    extracted_time.append(time_block)
print("Extracted clean periods are:", extracted_time)

plt.figure()

# Convert time to datetime labels
time_labels = [start_time + timedelta(minutes=int(x)) for x in time]

# # Plot the data
plt.plot(time_labels, value)

# Fill between specified times
for start, end in extracted_time:
   # plt.fill_between(time, value, where=(time >= start) & (time <= end), color='green', alpha=0.5)
    s = start_time + timedelta(minutes=int(start))
    e = start_time + timedelta(minutes=int(end))

    mask = (np.array(time_labels) >= s) & (np.array(time_labels) <= e)
    plt.plot(np.array(time_labels)[mask], np.array(value)[mask], color='green')

# Set labels and title
plt.xlabel('Time')  # Updated xlabel to 'Time' since it's now in HH:MM:SS format
plt.ylabel('MOER (lbs CO_2/MWh)')
plt.title(f"Marginal Operating Emission Rate - Region MISO_DETROIT - {generated_date}")

# Set x-axis formatter using gca() to get current Axes
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Save the figure
plt.savefig("watttime.png")

# Optionally show the plot
#plt.show()

def get_clean_periods():
    return extracted_time