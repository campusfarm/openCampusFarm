# egauge_client.py
import hashlib
import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
from secrets import token_hex

import requests
from dotenv import load_dotenv

load_dotenv()


class EGaugeClient:
    def __init__(self):
        self.meter = os.environ["EGAUGE_METER_NAME"]
        self.uri = f"https://{self.meter}.d.egauge.net"
        self.user = os.environ["EGAUGE_USER"]
        self.password = os.environ["EGAUGE_PASSWORD"]
        self.jwt = None
        self.last_token_time = None

    def _get_jwt(self):  # Authentication
        # Get realm and nonce
        auth_req = requests.get(f"{self.uri}/api/auth/unauthorized").json()
        realm = auth_req["rlm"]
        nnc = auth_req["nnc"]

        # Generate client nonce
        cnnc = str(token_hex(64))

        # Generate hash
        ha1_content = f"{self.user}:{realm}:{self.password}"
        ha1 = hashlib.md5(ha1_content.encode("utf-8")).hexdigest()
        hash_content = f"{ha1}:{nnc}:{cnnc}"
        hash = hashlib.md5(hash_content.encode("utf-8")).hexdigest()

        # Login
        payload = {
            "rlm": realm,
            "usr": self.user,
            "nnc": nnc,
            "cnnc": cnnc,
            "hash": hash,
        }

        auth_login = requests.post(f"{self.uri}/api/auth/login", json=payload).json()
        self.jwt = auth_login["jwt"]
        self.last_token_time = datetime.now()
        return self.jwt

    def _get_headers(self):
        # Refresh token if older than 5 minutes
        if not self.jwt or (datetime.now() - self.last_token_time) > timedelta(
            minutes=5
        ):
            self._get_jwt()
        return {"Authorization": f"Bearer {self.jwt}"}

    def get_live_data(self):  # this returns full local endpoint result
        url = f"{self.uri}/api/local"
        query_string = "env=all&l=all&s=all&values&energy&apparent&rate&cumul&type&normal&mean&freq"

        response = requests.get(url, headers=self._get_headers(), params=query_string)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get data: {response.status_code}")

    def get_l1(self):
        data = self.get_live_data()
        return data["values"]["L1"]["rate"]["n"]

    def get_l2(self):
        data = self.get_live_data()
        return data["values"]["L2"]["rate"]["n"]

    def get_s1(self):
        data = self.get_live_data()
        return data["values"]["S1"]["rate"]["n"]

    def get_s2(self):
        data = self.get_live_data()
        return data["values"]["S2"]["rate"]["n"]

    def get_evcharger_current(self):
        data = self.get_live_data()
        return data["values"]["S5"]["rate"]["n"]

    def get_cooler_current(self):
        data = self.get_live_data()
        return data["values"]["S8"]["rate"]["n"]

    def get_grid_power(self):
        data = self.get_live_data()
        return data["energy"]["S1*L1"]["rate"] + data["energy"]["S2*L2"]["rate"]

    def get_cooler_power(self):
        data = self.get_live_data()
        return (
            data["energy"]["S8*L1"]["rate"] + data["energy"]["-S8*L2"]["rate"]
        )  # config is S8*L1 and -S8*L2, negative means consume

    def get_evcharger_power(self):
        data = self.get_live_data()
        return (
            data["energy"]["S5*L2"]["rate"] + data["energy"]["-S5*L1"]["rate"]
        )  # config is S5*L2 and -S5*L1, negative means consume?

    def get_all_values(self):
        data = self.get_live_data()
        return {
            "l1_voltage": data["values"]["L1"]["rate"]["n"],
            "l2_voltage": data["values"]["L2"]["rate"]["n"],
            "s1_current": data["values"]["S1"]["rate"]["n"],
            "s2_current": data["values"]["S2"]["rate"]["n"],
            "evcharger_current": data["values"]["S5"]["rate"]["n"],
            "cooler_current": data["values"]["S8"]["rate"]["n"],
            "grid_power": data["energy"]["S1*L1"]["rate"]
            + data["energy"]["S2*L2"]["rate"],
            "cooler_power": data["energy"]["S8*L1"]["rate"]
            + data["energy"]["-S8*L2"]["rate"],
            "evcharger_power": data["energy"]["S5*L2"]["rate"]
            + data["energy"]["-S5*L1"]["rate"],
            "timestamp": data["ts"],
        }
