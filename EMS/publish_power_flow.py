"""
Campus Farm power-flow publisher.

Reads live PV / grid / load power from the SolArk inverter API and POSTs it
to the Drupal site's ems_api module (`/api/data`), so graph_display's power
flow arrow diagram can render it in near real time.

Runs independently of real_time_ems.py — it only publishes readings, it
does not make any EMS control decisions.
"""

import logging
import os
import time

import requests
from dotenv import load_dotenv
from from_root import from_root

from solArk_inverter import fetch_plant_data

load_dotenv(from_root(".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DRUPAL_BASE_URL = os.getenv("DRUPAL_BASE_URL", "http://mbgna.lndo.site")
DRUPAL_DATA_ENDPOINT = f"{DRUPAL_BASE_URL}/api/data"
PUBLISH_INTERVAL = int(os.getenv("POWER_PUBLISH_INTERVAL", "5"))  # seconds


def publish_power_flow() -> bool:
    """Fetch current PV/grid/load power from SolArk and POST it to Drupal."""
    flow = fetch_plant_data()
    if flow is None:
        log.warning("[SolArk] No flow data available — skipping publish")
        return False

    payload = {
        "netSolartoInverter": flow["pv"],
        "netInvertertoGrid": flow["grid"],
        "netInvertertoComps": flow["load"],
    }

    try:
        response = requests.post(
            DRUPAL_DATA_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=15,
        )
        if response.status_code == 201:
            log.info(
                "[Publish] solar=%.0fW grid=%.0fW load=%.0fW -> %s",
                flow["pv"], flow["grid"], flow["load"], DRUPAL_DATA_ENDPOINT,
            )
            return True
        log.error("[Publish] Drupal returned %s: %s", response.status_code, response.text)
    except Exception as exc:
        log.error("[Publish] Failed to reach Drupal: %s", exc)
    return False


def main() -> None:
    log.info(
        "Power-flow publisher starting — publishing every %ds to %s",
        PUBLISH_INTERVAL, DRUPAL_DATA_ENDPOINT,
    )
    while True:
        try:
            publish_power_flow()
        except KeyboardInterrupt:
            log.info("Publisher stopped by user.")
            break
        except Exception as exc:
            log.error("Unexpected error: %s", exc, exc_info=True)
        time.sleep(PUBLISH_INTERVAL)


if __name__ == "__main__":
    main()
