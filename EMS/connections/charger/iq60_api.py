from errno import ENOPKG
import http.client
import json
from datetime import datetime
import os
from from_root import from_root
from dotenv import load_dotenv

load_dotenv(from_root(".env"))

conn = http.client.HTTPSConnection("api.enphaseenergy.com")
payload = ''
headers = {
    'Authorization': 'bearer '+os.environ.get('ENPHASE_AUTHORIZATION_TOKEN'),
    'key': os.environ.get("ENPHASE_AUTHORIZATION_KEY")
}
ENPHASE_SYSTEM_ID=os.environ.get("ENPHASE_SYSTEM_ID")
ENPHASE_SERIAL_NO=os.environ.get("ENPHASE_SERIAL_NO")
conn.request("GET", f"/api/v4/systems/{ENPHASE_SYSTEM_ID}/ev_charger/{ENPHASE_SERIAL_NO}/sessions", payload, headers)
res = conn.getresponse()
data = res.read()

# Parse the JSON response
response_data = json.loads(data.decode("utf-8"))

# Access the sessions
sessions = response_data.get("sessions", [])

# Iterate through each session and print details with human-readable times
for i, session in enumerate(sessions, start=1):
    start_time_human = datetime.fromtimestamp(session['start_time']).strftime('%Y-%m-%d %H:%M:%S')
    end_time_human = datetime.fromtimestamp(session['end_time']).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Session {i}:")
    print(f"  Start Time: {start_time_human}")
    print(f"  End Time: {end_time_human}")
    print(f"  Duration: {session['duration']} seconds")
    print(f"  Energy Added: {session['energy_added']} kWh")
    print(f"  Charge Time: {session['charge_time']} seconds")
    print(f"  Miles Added: {session['miles_added']}")
    print(f"  Cost: {session['cost']}")
    print()
