import subprocess
import time
from datetime import datetime
import csv
import os

def check_wifi_status_ifconfig():
    try:
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
        if 'State' in result.stdout and "connected" in result.stdout.lower():
            return True 
        else:
            return False 
    except Exception as e:
        print(f"Error checking Wi-Fi status: {e}")

def monitor_wifi_status(interval=5, csv_filename='wifi_status.csv'):
    # Check if CSV file exists to determine if we need to write the header
    file_exists = os.path.isfile(csv_filename)
    try:
        with open(csv_filename, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Wi-Fi Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write header only if file does not exist
            if not file_exists:
                writer.writeheader()

            while True:
                status = check_wifi_status_ifconfig()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Write the status and timestamp to CSV
                writer.writerow({'Timestamp': timestamp, 'Wi-Fi Status': status})
                # Optionally print the status to the console
                # print(f"{timestamp} - {status}")
                time.sleep(interval)  # Wait for the specified interval before checking again
    except KeyboardInterrupt:
        print("Monitoring stopped.")
