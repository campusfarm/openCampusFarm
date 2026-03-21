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

UTC = pytz.UTC
DETROIT_TZ = pytz.timezone("America/Detroit")
filepath = 'weeklySchedule.csv'
min_time_difference = None
hours_difference = 0
clean_periods = []
normal_periods = []

real_time = datetime.now()
def get_login_token():
    
    # To login and obtain an access token, use this code:
    import requests
    from requests.auth import HTTPBasicAuth
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth(os.environ.get("WT_USERNAME"), os.environ.get("WT_PASSWORD")))
    TOKEN = rsp.json()['token']
    print(rsp.json())
    return TOKEN
# -------------------------
# Helpers
# -------------------------
def _parse_watttime_iso(s: str) -> datetime:
    """
    Handles both:
      - 2026-02-07T23:10:00Z
      - 2026-02-07T23:10:00+00:00
    Returns tz-aware UTC datetime.
    """
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    return dt.astimezone(UTC)


# -------------------------
# 1) get_moer(token)
# -------------------------
def get_moer(token, region="MISO_DETROIT", signal_type="co2_moer", horizon_hours=None):
    """
    Fetch WattTime forecast and populate global `data` as Detroit-local tz-aware datetimes.
    """
    global data

    url = "https://api.watttime.org/v3/forecast"
    headers = {"Authorization": f"Bearer {token}"}

    params = {"region": region, "signal_type": signal_type}
    if horizon_hours is not None:
        # WattTime expects integer hours; keep it safe.
        hh = int(max(1, min(72, math.floor(float(horizon_hours)))))
        params["horizon_hours"] = hh

    rsp = requests.get(url, headers=headers, params=params)
    rsp.raise_for_status()
    pre_data = rsp.json()

    # Convert API points -> Detroit-local time, no manual "-5 hours"
    parsed = []
    for entry in pre_data.get("data", []):
        pt_utc = _parse_watttime_iso(entry["point_time"])
        pt_detroit = pt_utc.astimezone(DETROIT_TZ)
        parsed.append({"point_time": pt_detroit, "value": float(entry["value"])})

    # Ensure chronological order
    parsed.sort(key=lambda x: x["point_time"])
    data = parsed

    return pre_data


# -------------------------
# 2) generate_clean_periods(num_time_slots_wanted)
# -------------------------
def generate_clean_periods(num_time_slots_wanted):
    """
    Selects:
      - clean_periods: the lowest-MOER N individual 5-min slots (scattered)
      - normal_periods: the first N chronological 5-min slots
    Saves to global lists.
    """
    global data, clean_periods, normal_periods

    if not data:
        raise RuntimeError("Global `data` is empty. Call get_moer(token) first.")

    N = int(num_time_slots_wanted)
    N = max(0, min(N, len(data)))

    # Build chronological slots
    chronological_slots = [(d["value"], d["point_time"]) for d in data]  # (value, dt_detroit)

    # Normal = first N chronological
    normal_slots = chronological_slots[:N]

    # Clean = lowest N by value
    clean_slots = sorted(chronological_slots, key=lambda x: x[0])[:N]

    # Convert to (start_iso, end_iso) intervals (5 minutes each)
    def to_interval(dt_detroit: datetime):
        start = dt_detroit.isoformat()
        end = (dt_detroit + timedelta(minutes=5)).isoformat()
        return (start, end)

    clean_periods = [to_interval(dt) for _, dt in clean_slots]
    normal_periods = [to_interval(dt) for _, dt in normal_slots]

    return clean_periods, normal_periods


# -------------------------
# 3) plot_clean_periods(clean_periods, values, times)
# -------------------------
def plot_clean_periods(clean_periods, values, times, filename="clean_periods.png"):
    """
    `values`: list/array of MOER values (chronological)
    `times`:  list of datetime objects (chronological, ideally Detroit tz-aware)
    `clean_periods`: list of (start_iso, end_iso) to highlight
    """
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, label="MOER Values")

    # Highlight selected clean windows
    for start_iso, end_iso in clean_periods:
        start_dt = datetime.fromisoformat(start_iso)
        end_dt = datetime.fromisoformat(end_iso)
        mask = (np.array(times) >= start_dt) & (np.array(times) <= end_dt)
        plt.plot(np.array(times)[mask], np.array(values)[mask], color="green")

    plt.xlabel("Time (Detroit)")
    plt.ylabel("MOER (lbs CO₂/MWh)")
    plt.title("Clean Time Periods - Detroit (MISO_DETROIT)")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(filename)
    # plt.show()


# -------------------------
# 4) save_clean_periods(filename="ev_clean_periods.json")
# -------------------------
def save_clean_periods(filename="ev_clean_periods.json"):
    global clean_periods
    with open(filename, "w") as f:
        json.dump(clean_periods, f, indent=2)
    print(f"EV clean periods saved to {filename}")


# -------------------------
# 5) save_nonEMS_charging_periods(filename="ev_nonEMS_charging_periods.json")
# -------------------------
def save_nonEMS_charging_periods(filename="ev_nonEMS_charging_periods.json"):
    global normal_periods
    with open(filename, "w") as f:
        json.dump(normal_periods, f, indent=2)
    print(f"EV non-EMS charging periods saved to {filename}")


# -------------------------
# Convenience: build values/times from global data
# -------------------------
def _values_times_from_global_data():
    if not data:
        return [], []
    times = [d["point_time"] for d in data]
    values = [d["value"] for d in data]
    return values, times


token = get_login_token()
get_moer(token, horizon_hours=24)  # or omit horizon_hours
generate_clean_periods(29)

values, times = _values_times_from_global_data()
plot_clean_periods(clean_periods, values, times)

save_clean_periods()
save_nonEMS_charging_periods()
