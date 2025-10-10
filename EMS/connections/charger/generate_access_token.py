import http.client
import json
import time
import os
from from_root import from_root
from dotenv import load_dotenv

load_dotenv(from_root(".env"))

def read_refresh_token():
    try:
        with open("refresh_token.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("No refresh token file found.")
        return None

def save_refresh_token(token):
    with open("refresh_token.txt", "w") as file:
        file.write(token)

def get_access_token():
    refresh_token = read_refresh_token()
    if not refresh_token:
        refresh_token = os.environ.get('EMPHASE_REFRESH_TOKEN')
    payload = ''
    headers = {
        'Authorization': 'Basic '+os.environ.get("EMPHASE_REFRESH_TOKEN")
    }
    
    for attempt in range(5):  # Retry up to 5 times
        conn = http.client.HTTPSConnection("api.enphaseenergy.com")  # New connection each attempt
        conn.request("POST", f"/oauth/token?grant_type=refresh_token&refresh_token={refresh_token}", payload, headers)
        
        try:
            res = conn.getresponse()
            
            if res.status == 200:
                data = res.read()
                try:
                    response = json.loads(data.decode("utf-8"))
                    
                    if 'refresh_token' in response:
                        save_refresh_token(response['refresh_token'])
                        print("New refresh token saved.")

                    if 'access_token' in response:
                        print("Access token:", response['access_token'])
                    else:
                        print("Failed to obtain access token:", response)
                    return  # Exit after successful request
                except json.JSONDecodeError:
                    print("Error: Unable to parse JSON response. Response was:", data.decode("utf-8"))
                    return
            else:
                print(f"Attempt {attempt + 1}: Error {res.status} - {res.reason}")
                time.sleep(2 ** attempt)  # Exponential backoff: 1, 2, 4, 8, 16 seconds

        except http.client.ResponseNotReady:
            print("ResponseNotReady error encountered. Retrying...")
            time.sleep(2 ** attempt)

        finally:
            conn.close()  # Ensure connection is closed after each attempt

    print("All retry attempts failed. Please try again later.")

get_access_token()
