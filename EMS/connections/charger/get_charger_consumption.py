import http.client
import json
from datetime import datetime
import os
from from_root import from_root
from dotenv import load_dotenv

load_dotenv(from_root(".env"))

# Function to read the stored refresh token from a file
def read_refresh_token():
    try:
        with open("refresh_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("No refresh token file found.")
        return None

# Function to save the new refresh token to a file
def save_refresh_token(token):
    with open("refresh_token.txt", "w") as file:
        file.write(token)

def generate_access_token():
    try:
        # Read the refresh token from file (or replace this with your initial token if running for the first time)
        refresh_token = read_refresh_token()
        if not refresh_token:
            # Use the initial token here if no file exists
            refresh_token = os.environ.get('EMPHASE_INITIAL_TOKEN')
        # Set up the connection and headers
        conn = http.client.HTTPSConnection("api.enphaseenergy.com")
        payload = ''
        headers = {
            'Authorization': 'Basic '+os.environ.get('ENPHASE_AUTHORIZATION_HEADER')
        }

        # Make the request with the current refresh token
        conn.request("POST", f"/oauth/token?grant_type=refresh_token&refresh_token={refresh_token}", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # Decode and parse the JSON response
        response = json.loads(data.decode("utf-8"))

        # Check if the request was successful and save the new refresh token
        if 'refresh_token' in response:
            new_refresh_token = response['refresh_token']
            save_refresh_token(new_refresh_token)
            print("New refresh token saved.")
        else:
            print("Failed to obtain refresh token:", response)

        # Print the access token or other relevant information
        if 'access_token' in response:
            return response['access_token']
            #print("Access token:", response['access_token'])
        else:
            print("Failed to obtain access token:", response)
    except Exception as e:
        print(f"Error connecting to Enphase API in connections/charger/get_charger_consumption:\n", e)


try:
    auth = generate_access_token()
    conn = http.client.HTTPSConnection("api.enphaseenergy.com")
    payload = ''
    headers = {
        'Authorization': f"bearer {auth}",
        'key': os.environ.get('ENPHASE_AUTHORIZATION_KEY')
    }
    system_id = os.environ.get('ENPHASE_SYSTEM_ID')
    serial_no = os.environ.get('ENPHASE_SERIAL_NO')
    conn.request("GET", f"/api/v4/systems/{system_id}/ev_charger/{serial_no}/sessions", payload, headers)
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
except Exception as e:
    print(f"Error occurred in connections/charger/get_charger_consumption:\n", e)

def get_miles_added():
    return sessions[0]['miles_added']
