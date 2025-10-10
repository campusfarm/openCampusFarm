from tomllib import load
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, timezone
import matplotlib.dates as mdates
from .closestDelivery import get_next_delivery, read_schedule_from_csv
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))

# from real_time_ems import get_amount_of_clean_periods
# import test as test
import csv
import pytz
import json
import math

TIMEZONE = pytz.UTC
DETROIT_TIMEZONE = pytz.timezone("America/Detroit")
filepath = "weeklySchedule.csv"
min_time_difference = None
hours_difference = 0

real_time = datetime.now()


def perform_action_based_on_next_delivery():
    global min_time_difference
    global hours_difference

    schedule = read_schedule_from_csv(filepath)
    current_time = datetime.now(DETROIT_TIMEZONE)
    # Find the next delivery
    next_delivery, next_delivery_time, min_time_difference = get_next_delivery(
        schedule, current_time
    )
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

    register_url = "https://api.watttime.org/register"
    params = {
        "username": os.environ.get("WT_USERNAME"),
        "password": os.environ.get("WT_PASSWORD"),
        "email": os.environ.get("WT_EMAIL"),
        "org": os.environ.get("WT_ORG"),
    }
    rsp = requests.post(register_url, json=params)
    # print(rsp.text)


def get_login_token():
    # To login and obtain an access token, use this code:
    import requests
    from requests.auth import HTTPBasicAuth

    login_url = "https://api.watttime.org/login"
    rsp = requests.get(login_url, auth=HTTPBasicAuth(os.environ.get("WT_USERNAME"), os.environ.get("WT_PASSWORD")))
    TOKEN = rsp.json()["token"]
    print(rsp.json())
    return TOKEN


def get_moer(token, time_interval=15):
    url = "https://api.watttime.org/v3/historical"
    headers = {"Authorization": f"Bearer {token}"}
    # Get the current time in Detroit timezone
    current_time_detroit = datetime.now(DETROIT_TIMEZONE)

    time_difference = time_interval - 5

    # Round down to the nearest 5-minute interval
    rounded_end_time = current_time_detroit - timedelta(
        minutes=current_time_detroit.minute % 5,
        seconds=current_time_detroit.second,
        microseconds=current_time_detroit.microsecond,
    )
    # Calculate the start time (15 minutes before the end time)
    rounded_start_time = rounded_end_time - timedelta(minutes=time_difference)

    params = {
        "region": "MISO_DETROIT",
        "start": rounded_start_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "end": rounded_end_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "signal_type": "co2_moer",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    # print(response.json())
    return response.json()


token = get_login_token()
data = get_moer(token)
formatted_data = [(entry["point_time"], entry["value"]) for entry in data["data"]]
total_value = sum(value for _, value in formatted_data)
average_value = total_value / len(formatted_data)
# print(formatted_data)
# print(total_value)


def get_wt(mode, type):
    global token
    if mode == "optimization":
        get_moer(token, time_interval=30)
        data = get_moer(token)
        formatted_data = [
            (entry["point_time"], entry["value"]) for entry in data["data"]
        ]
        if type == "aoer":
            return sum(value for _, value in formatted_data)
        elif type == "moer":
            return sum(value for _, value in formatted_data) / len(formatted_data)

    if mode == "ruleBased":
        get_moer(token, time_interval=5)
        data = get_moer(token)
        formatted_data = [
            (entry["point_time"], entry["value"]) for entry in data["data"]
        ]
        if type == "aoer":
            return sum(value for _, value in formatted_data)
        elif type == "moer":
            return sum(value for _, value in formatted_data) / len(formatted_data)


print(get_wt("optimization", "aoer"))
