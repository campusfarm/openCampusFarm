# from real_time_ems import get_amount_of_clean_periods
# import test as test
import json
import os
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pytz
import requests
from dotenv import load_dotenv
from from_root import from_root

load_dotenv(from_root(".env"))

TIMEZONE = pytz.UTC
DETROIT_TIMEZONE = pytz.timezone("America/Detroit")
filepath = "weeklySchedule.csv"
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

    login_url = "https://api.watttime.org/login"
    rsp = requests.get(
        login_url,
        auth=HTTPBasicAuth(
            os.environ.get("WT_USERNAME"), os.environ.get("WT_PASSWORD")
        ),
    )
    TOKEN = rsp.json()["token"]
    print(rsp.json())
    return TOKEN


def get_moer(token, horizon_hours=24):
    url = "https://api.watttime.org/v3/forecast"
    headers = {"Authorization": f"Bearer {token}"}

    horizon_hours = int(max(1, min(72, horizon_hours)))  # WT limit protection

    params = {
        "region": "MISO_DETROIT",
        "signal_type": "co2_moer",
        "horizon_hours": horizon_hours,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


# def generate_clean_periods(clean_bar, merge_adjacent=True):
#     try:
#         global data, TIMEZONE, clean_periods, normal_periods

#         slots = []
#         for entry in data:
#             v = entry["value"]
#             t0 = datetime.fromisoformat(entry["point_time"]).astimezone(TIMEZONE)
#             t1 = t0 + timedelta(minutes=5)
#             slots.append((v, t0, t1))

#         normal_periods = [(t0.isoformat(), t1.isoformat()) for (v, t0, t1) in slots]

#         clean_raw = [(t0, t1) for (v, t0, t1) in slots if v <= clean_bar]

#         if merge_adjacent:
#             merged = []
#             if clean_raw:
#                 cur_s, cur_e = clean_raw[0]
#                 for s, e in clean_raw[1:]:
#                     if s == cur_e:
#                         cur_e = e
#                     else:
#                         merged.append((cur_s, cur_e))
#                         cur_s, cur_e = s, e
#                 merged.append((cur_s, cur_e))
#             clean_periods = [(s.isoformat(), e.isoformat()) for s, e in merged]
#         else:
#             clean_periods = [(s.isoformat(), e.isoformat()) for s, e in clean_raw]

#         print(f"Clean bar = {clean_bar}. Clean intervals = {len(clean_periods)}")

#     except Exception as e:
#         print(f"An error occurred with generate_clean_periods: {e}")


def generate_clean_periods(clean_bar, merge_adjacent=True):
    try:
        global data, TIMEZONE, clean_periods, normal_periods

        slots = []
        for entry in data:
            v = entry["value"]
            t0 = datetime.fromisoformat(entry["point_time"]).astimezone(TIMEZONE)
            t1 = t0 + timedelta(minutes=5)
            slots.append((v, t0, t1))

        # all 5-min periods (24h -> ~288)
        normal_periods = [(t0.isoformat(), t1.isoformat()) for (v, t0, t1) in slots]

        # clean 5-min slots (no merge yet)
        clean_raw = [(t0, t1) for (v, t0, t1) in slots if v <= clean_bar]
        clean_slots_5min = len(clean_raw)  # <-- this is what you want

        if merge_adjacent:
            merged = []
            if clean_raw:
                cur_s, cur_e = clean_raw[0]
                for s, e in clean_raw[1:]:
                    if s == cur_e:
                        cur_e = e
                    else:
                        merged.append((cur_s, cur_e))
                        cur_s, cur_e = s, e
                merged.append((cur_s, cur_e))
            clean_periods = [(s.isoformat(), e.isoformat()) for s, e in merged]
        else:
            clean_periods = [(s.isoformat(), e.isoformat()) for (s, e) in clean_raw]

        print(
            f"Clean bar = {clean_bar}. "
            f"Clean intervals = {len(clean_periods)}. "
            f"Clean 5-min slots = {clean_slots_5min} / {len(slots)}"
        )

    except Exception as e:
        print(f"An error occurred with generate_clean_periods: {e}")


def plot_clean_periods(clean_periods, values, times):
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, color="blue", label="MOER Values")

    for start, end in clean_periods:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        plt.axvspan(start_dt, end_dt, alpha=0.3, color="green")

    plt.xlabel("Time")
    plt.ylabel("MOER (lbs CO₂/MWh)")
    plt.title("Clean Periods - MISO Detroit MOER (24h)")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig("clean_periods1.png")
    plt.close()


def save_clean_periods(filename="ev_clean_periods1.json"):
    try:
        global clean_periods
        with open(filename, "w") as file:
            json.dump(clean_periods, file)
        print(f"EV clean periods saved to {filename}")
    except Exception as e:
        print(f"An error occurred with save_clean_periods: {e}")


def save_nonEMS_charging_periods(filename="ev_nonEMS_charging_periods1.json"):
    try:
        global normal_periods
        with open(filename, "w") as file:
            json.dump(normal_periods, file)
        print(f"EV clean periods saved to {filename}")
    except Exception as e:
        print(f"An error occurred with save_nonEMS_charging_periods: {e}")


# ===== MAIN =====
token = get_login_token()
horizon = 24
pre_data = get_moer(token, horizon_hours=horizon)

data = [{"point_time": e["point_time"], "value": e["value"]} for e in pre_data["data"]]

values = [e["value"] for e in data]
times = [datetime.fromisoformat(e["point_time"]).astimezone(TIMEZONE) for e in data]

# clean-bar judgement: pick one
# Option A: percentile-based (recommended)
clean_bar = np.percentile(values, 50)  # cleanest 20% of next 24h
# Option B: fixed threshold (example)
# clean_bar = 250

generate_clean_periods(clean_bar, merge_adjacent=True)

plot_clean_periods(clean_periods, values, times)
print("clean_periods:", len(clean_periods), clean_periods[:5])
print("normal_periods:", len(normal_periods), normal_periods[:5])

print("Saving clean periods...")
save_clean_periods()
print("Saving normal periods...")
save_nonEMS_charging_periods()
print("Done.")
