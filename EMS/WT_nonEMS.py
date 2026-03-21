import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from closestDelivery import get_next_delivery, read_schedule_from_csv
# from real_time_ems import get_amount_of_clean_periods
# import test as test
import csv
import pytz
import json 
import math

from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))

TIMEZONE = pytz.UTC
DETROIT_TIMEZONE = pytz.timezone("America/Detroit")
filepath = 'weeklySchedule.csv'
min_time_difference = None
hours_difference = 0
clean_periods = []
normal_periods = []

real_time = datetime.now()

# def perform_action_based_on_next_delivery():
#     try:
#         global min_time_difference
#         global hours_difference

#         schedule = read_schedule_from_csv(filepath)
#         current_time = datetime.now(DETROIT_TIMEZONE)
#         # Find the next delivery
#         next_delivery, next_delivery_time, min_time_difference = get_next_delivery(schedule, current_time)
#         hours_difference = min_time_difference.total_seconds() / 3600  # Convert to hours
#         hours_difference = math.floor(hours_difference)  # Get the floored value
#         return hours_difference
#     except Exception as e:
#         print(f"An error occurred with perform_action_based_on_next_delivery: {e}")

# perform_action_based_on_next_delivery()

def get_current_time():
    print(real_time)
    return real_time

# def make_account():
    
#     # To register, use the code below. Please note that for these code examples we are using filler values for username
#     # (freddo), password (the_frog), email (freddo@frog.org), org (freds world) and you should replace each if you are
#     # copying and pasting this code.

#     import requests
#     register_url = 'https://api.watttime.org/register'
#     params = {'username': os.environ.get("WT_USERNAME"),
#             'password': os.environ.get("WT_PASSWORD"),
#             'email': os.environ.get("WT_EMAIL"),
#             'org': os.environ.get("WT_ORG")}
#     rsp = requests.post(register_url, json=params)
    # print(rsp.text)

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
    # Get the current time in Detroit's timezone
    current_time_detroit = datetime.now(DETROIT_TIMEZONE)
    # Convert Detroit time to UTC for the WattTime API
    # Forecast should start now (in Detroit time) and extend 24 hours
    start_time = current_time_detroit.isoformat()  # Detroit local time (ISO format)
    # end_time = (current_time_detroit + timedelta(hours=24)).isoformat()
    
    
    # Convert to UTC for WattTime API
    start_time_utc = current_time_detroit.astimezone(pytz.timezone("America/New_York")).isoformat()
    global min_time_difference
    global hours_difference
    print(hours_difference)
    print(min_time_difference)
    if hours_difference > 72:
        hours_difference = 72

    params = {
        "region": "MISO_DETROIT",
        "signal_type": "co2_moer",
        "horizon_hours": hours_difference
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()



def generate_clean_periods(num_time_slots_wanted):
    try:
        global data
        global TIMEZONE
        global clean_periods
        global normal_periods
            
        # Extract values and times
        values = [entry['value'] for entry in data]
        times = [datetime.fromisoformat(entry['point_time']).astimezone(TIMEZONE) for entry in data]

        # Extract and sort 5-minute periods
        time_slots = [(value, times[i]) for i, value in enumerate(values)]  # Pair values with their timestamps
        normal_s = time_slots
        # Sort by MOER value (ascending)
        time_slots.sort(key=lambda x: x[0])  # Sort by the MOER value (lowest first)

        # Select up to X hours worth of 5-minute periods (X*12 periods)
    # num_time_slots_wanted = get_amount_of_clean_periods()
        print(num_time_slots_wanted)
        selected_slots = time_slots[:num_time_slots_wanted]  # Take the first 84 slots (X hours)
        normal_slots = normal_s[:num_time_slots_wanted]
        # Extract clean periods with full ISO 8601 timestamps
        clean_periods = [(slot[1].isoformat(), (slot[1] + timedelta(minutes=5)).isoformat()) for slot in selected_slots]
        normal_periods = [(slot[1].isoformat(), (slot[1] + timedelta(minutes=5)).isoformat()) for slot in normal_slots]
        print(len(selected_slots))
    except Exception as e:
        print(f"An error occurred with generate_clean_periods: {e}")

# def generate_clean_periods(clean_bar, merge_adjacent=True):
#     """
#     Build clean_periods based on MOER threshold (clean_bar).
#     Any 5-min slot with value <= clean_bar is considered clean.

#     Args:
#         clean_bar (float): MOER threshold. Example: 250 (lbs/MWh) or whatever unit your WT returns.
#         merge_adjacent (bool): If True, merge consecutive clean 5-min slots into longer intervals.
#     """
#     try:
#         global data
#         global TIMEZONE
#         global clean_periods
#         global normal_periods

#         # Parse times + values (keep original order)
#         slots = []
#         for entry in data:
#             v = entry["value"]
#             t0 = datetime.fromisoformat(entry["point_time"]).astimezone(TIMEZONE)
#             t1 = t0 + timedelta(minutes=5)
#             slots.append((v, t0, t1))

#         # All periods (normal) in original order
#         normal_periods = [(t0.isoformat(), t1.isoformat()) for (v, t0, t1) in slots]

#         # Threshold filter (no sorting)
#         clean_raw = [(t0, t1) for (v, t0, t1) in slots if v <= clean_bar]

#         # Optionally merge adjacent clean slots into continuous intervals
#         if merge_adjacent:
#             clean_periods_dt = []
#             if clean_raw:
#                 cur_start, cur_end = clean_raw[0]
#                 for (s, e) in clean_raw[1:]:
#                     # adjacent if next starts exactly when current ends
#                     if s == cur_end:
#                         cur_end = e
#                     else:
#                         clean_periods_dt.append((cur_start, cur_end))
#                         cur_start, cur_end = s, e
#                 clean_periods_dt.append((cur_start, cur_end))

#             clean_periods = [(s.isoformat(), e.isoformat()) for (s, e) in clean_periods_dt]
#         else:
#             clean_periods = [(s.isoformat(), e.isoformat()) for (s, e) in clean_raw]

#         print(f"Clean bar = {clean_bar}. Clean intervals = {len(clean_periods)}")

#     except Exception as e:
#         print(f"An error occurred with generate_clean_periods: {e}")

def plot_clean_periods(clean_periods, values, times):
    """
    Visualize clean periods on a time-value plot.
    - Clean periods: Green
    - Other periods: Black
    """
    plt.figure(figsize=(12, 6))

    # Plot the entire dataset in blue
    plt.plot(times, values, color="blue", label="MOER Values")

    # Highlight clean periods in green
    for start, end in clean_periods:
        # Convert clean period times (HH:MM) into datetime objects
# Parse full ISO 8601 timestamps for start and end
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

    # Customize plot
    plt.xlabel("Time")
    plt.ylabel("MOER (lbs CO₂/MWh)")
    plt.title(f"Clean Time Periods - Region: Detroit")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")

    # Save and show the plot
    plt.savefig("clean_periods.png")
    plt.show()


# plot_clean_periods(clean_periods,values,times)
# Save clean periods to a JSON file
def save_clean_periods(filename="ev_clean_periods.json"):
    try:
        global clean_periods
        with open(filename, "w") as file:
            json.dump(clean_periods, file)
        print(f"EV clean periods saved to {filename}")
    except Exception as e:
        print(f"An error occurred with save_clean_periods: {e}")

def save_nonEMS_charging_periods(filename="ev_nonEMS_charging_periods.json"):
    try:
        global normal_periods
        with open(filename, "w") as file:
            json.dump(normal_periods, file)
        print(f"EV clean periods saved to {filename}")
    except Exception as e:
        print(f"An error occurred with save_nonEMS_charging_periods: {e}")

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6Ik5PTkUiLCJpYXQiOjE3NzEyMjI5NjYsImV4cCI6MTc3MTIyNDc2NiwiaXNzIjoiV2F0dFRpbWUiLCJzdWIiOiJDRi1FTVMtYWRtaW5AdW1pY2guZWR1In0.QhEyfb-Q7hQmgNRJb0mTRV0QuCgF5bqLhFqiptPuU7i98hgz-NLkZ3zyH9w9ftC_xmwOVFdX37E4mxusAQD0gFzQLGwnyY2rIfWwjtTg4kG1dgsWS2suhw3bq1TDnhC6sYI8LF1XEBPlf9rjfiPl_GauxJX1A6EiQF1g_Q713qyv6U4N3paCSid_wMCk3dE2ia2idfBSi8DgaWgQvq4ToC9Gsko5YqOCw8Ma45_l_hXA8HPI77kxxy9JFZP7xuvRv3bCF0bpL5rY7CUDDP4frjwG73mPRXAOdvENuAPs9JLn6tPZLU0HB6iZG6de4QEsnsmr_v_vO43Ep9-kyQZsLA'

# choose a horizon (hours). If you don’t have delivery logic yet, just use 24.
horizon = 24

pre_data = get_moer(token)

# build data list in UTC (keep UTC consistent everywhere)
data = [{"point_time": e["point_time"], "value": e["value"]} for e in pre_data["data"]]
print(data)
# extract series for plotting
values = [e["value"] for e in data]
times = [datetime.fromisoformat(e["point_time"]).astimezone(TIMEZONE) for e in data]

# pick threshold (example: median = 50th percentile; you can change to 20 for “cleanest 20%”)
clean_bar = np.percentile(values, 50)

generate_clean_periods(29)

# plot + save
plot_clean_periods(clean_periods, values, times)

save_clean_periods()
save_nonEMS_charging_periods()

