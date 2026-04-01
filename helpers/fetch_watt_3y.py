"""
Fetch 3 years of MOER data (2023-01-01 to 2025-12-31) from WattTime
and dump to watt-3y.csv with columns: point_time, moer_lbs_co2_per_mwh
"""

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone
import csv
import time
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

START = datetime(2023, 1, 1, tzinfo=timezone.utc)
END   = datetime(2026, 1, 1, tzinfo=timezone.utc)  # exclusive
CHUNK_DAYS = 30
REGION = "MISO_DETROIT"
OUT_CSV = Path(__file__).parent / "watt-3y.csv"


def login():
    rsp = requests.get(
        "https://api.watttime.org/login",
        auth=HTTPBasicAuth(os.environ["WT_USERNAME"], os.environ["WT_PASSWORD"]),
        timeout=30,
    )
    rsp.raise_for_status()
    return rsp.json()["token"]


def fetch_chunk(token, start: datetime, end: datetime) -> list[dict]:
    url = "https://api.watttime.org/v3/historical"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "region": REGION,
        "start": start.strftime("%Y-%m-%dT%H:%MZ"),
        "end":   end.strftime("%Y-%m-%dT%H:%MZ"),
        "signal_type": "co2_moer",
    }
    rsp = requests.get(url, headers=headers, params=params, timeout=60)
    rsp.raise_for_status()
    return rsp.json().get("data", [])


def main():
    print("Logging in to WattTime...")
    token = login()

    chunks = []
    cursor = START
    while cursor < END:
        chunk_end = min(cursor + timedelta(days=CHUNK_DAYS), END)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end

    print(f"Fetching {len(chunks)} chunks ({CHUNK_DAYS}-day windows)...")

    rows_written = 0
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["point_time", "moer_lbs_co2_per_mwh"])

        for i, (start, end) in enumerate(chunks):
            print(f"  [{i+1}/{len(chunks)}] {start.date()} → {end.date()}", end=" ... ", flush=True)
            try:
                data = fetch_chunk(token, start, end)
                for entry in data:
                    writer.writerow([entry["point_time"], entry["value"]])
                rows_written += len(data)
                print(f"{len(data)} rows")
            except requests.HTTPError as e:
                if e.response.status_code == 401:
                    print("token expired, re-logging in...")
                    token = login()
                    data = fetch_chunk(token, start, end)
                    for entry in data:
                        writer.writerow([entry["point_time"], entry["value"]])
                    rows_written += len(data)
                    print(f"{len(data)} rows (after re-auth)")
                else:
                    print(f"ERROR: {e}")
                    raise
            time.sleep(0.5)  # be polite to the API

    print(f"\nDone. {rows_written} rows written to {OUT_CSV}")


if __name__ == "__main__":
    main()
