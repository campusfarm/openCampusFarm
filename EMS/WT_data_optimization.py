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

real_time = datetime.now()

def perform_action_based_on_next_delivery():
    global min_time_difference
    global hours_difference

    schedule = read_schedule_from_csv(filepath)
    current_time = datetime.now(DETROIT_TIMEZONE)
    # Find the next delivery
    next_delivery, next_delivery_time, min_time_difference = get_next_delivery(schedule, current_time)
    hours_difference = min_time_difference.total_seconds() / 3600  # Convert to hours
    hours_difference = math.floor(hours_difference)  # Get the floored value

perform_action_based_on_next_delivery()

def get_current_time():
    print(real_time)
    return real_time

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

    params = {
        "region": "MISO_DETROIT",
        "signal_type": "co2_moer",
        "horizon_hours": 48
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

token = get_login_token()
# print(token)
pre_data = get_moer(token)

data = []
for entry in pre_data['data']:
    original_time = datetime.fromisoformat(entry['point_time'])  # Parse the point_time
    adjusted_time = original_time - timedelta(hours=5)  # Subtract 5 hours
    data.append({
        "point_time": adjusted_time.isoformat(),
        "value": entry['value']
    })

# print(len(data))
downsampled_data = data[::6]
print(type(downsampled_data))

def get_48h_wt():
    global downsampled_data
    return downsampled_data

print(get_48h_wt())



