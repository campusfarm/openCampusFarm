import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from from_root import from_root

load_dotenv(from_root(".env"))

# Global token cache
cached_token: Optional[str] = None
token_expiry: float = 0

# Configuration from environment variables
API_USERNAME = os.getenv("SOLARK_USERNAME")
API_PASSWORD = os.getenv("SOLARK_PASSWORD")
PLANT_ID = os.getenv("SOLARK_PLANT_ID", "139155")
BASE_URL = "https://ecsprod-api-new.solarkcloud.com"


def get_access_token() -> Optional[str]:
    global cached_token, token_expiry

    if cached_token and time.time() < token_expiry:
        return cached_token

    url = f"{BASE_URL}/oauth/token"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "origin": BASE_URL,
        "referer": BASE_URL,
    }
    data = {
        "client_id": "csp-web",
        "grant_type": "password",
        "password": API_PASSWORD,
        "username": API_USERNAME,
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()["data"]
        cached_token = result["access_token"]
        token_expiry = time.time() + (23 * 3600)
        print(f"[AUTH] New access token obtained, expires in 23 hours")
        return cached_token
    except Exception as e:
        print(f"[ERROR] Failed to get access token: {e}")
        return None


def parse_flow_data(flow_response: Dict[str, Any]) -> Dict[str, float]:
    try:
        data = flow_response.get("data", {})
        return {
            "pv": float(data.get("pvPower", 0)),
            "battery": float(data.get("battPower", 0)),
            "grid": float(data.get("gridOrMeterPower", 0)),
            "load": float(data.get("loadOrEpsPower", 0)),
            "soc": float(data.get("soc", 0)),
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse flow data: {e}")
        return {"pv": 0, "battery": 0, "grid": 0, "load": 0, "soc": 0}


def fetch_plant_data() -> Optional[Dict[str, float]]:
    global cached_token, token_expiry

    token = get_access_token()
    if not token:
        return None

    current_date = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/api/v1/plant/energy/{PLANT_ID}/flow"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    params = {"date": current_date}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 401:
            print("[AUTH] Token expired, refreshing...")
            cached_token = None
            token_expiry = 0
            token = get_access_token()
            if not token:
                return None
            headers["Authorization"] = f"Bearer {token}"
            response = requests.get(url, headers=headers, params=params, timeout=30)

        response.raise_for_status()
        raw_data = response.json()

        if raw_data.get("code") != 0:
            print(f"[ERROR] API returned error code: {raw_data.get('code')}, msg: {raw_data.get('msg')}")
            return None

        parsed_data = parse_flow_data(raw_data)
        print(
            f"[DATA] Flow data updated: PV={parsed_data['pv']}W, "
            f"Battery={parsed_data['battery']}W, Grid={parsed_data['grid']}W, "
            f"Load={parsed_data['load']}W, SOC={parsed_data['soc']}%"
        )
        return parsed_data
    except Exception as e:
        print(f"[ERROR] Failed to fetch flow data: {e}")
        return None


def get_inverter_data() -> Dict[str, str]:
    data = fetch_plant_data() or {}
    return {
        "Solar W": str(data.get("pv", 0)),
        "Battery W": str(data.get("battery", 0)),
        "Grid W": str(data.get("grid", 0)),
        "Consumed W": str(data.get("load", 0)),
        "soc": str(data.get("soc", 0)),
    }
