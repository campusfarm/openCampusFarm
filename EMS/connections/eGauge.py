import requests
import requests
import hashlib
from secrets import token_hex
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))
# meter and credential information
meter = os.environ["EGAUGE_METER_NAME"]
URI = f"https://{meter}.d.egauge.net"
USER = os.environ["EGAUGE_USER"]
PASS = os.environ["EGAUGE_PASSWORD"]


# get realm (rlm) and server nonce (nnc):
auth_req = requests.get(f"{URI}/api/auth/unauthorized").json()
realm = auth_req["rlm"]
nnc = auth_req["nnc"]

cnnc = str(token_hex(64)) # generate a client nonce (cnnc)

# generate our hash
# ha1 = MD5(usr:rlm:pwd)
# hash = MD5(ha1:nnc:cnnc)
ha1_content = f"{USER}:{realm}:{PASS}"
ha1 = hashlib.md5(ha1_content.encode("utf-8")).hexdigest()

hash_content = f"{ha1}:{nnc}:{cnnc}"
hash = hashlib.md5(hash_content.encode("utf-8")).hexdigest()

# Generate our payload
payload = {
    "rlm": realm,
    "usr": USER,
    "nnc": nnc,
    "cnnc": cnnc,
    "hash": hash
}

# POST to /auth/login to get a JWT
auth_login = requests.post(f"{URI}/api/auth/login", json=payload).json()

rights = auth_login["rights"] # rights this token has (save, control, etc)
jwt = auth_login["jwt"] # the actual bearer token

print(f"Got token with rights {rights}.")

# We can verify this token works.
# Add an authorization header with our token and make a request
headers = {"Authorization": f"Bearer {jwt}"}

api_request = requests.get(
    f"{URI}/api/config/net/hostname",
    headers=headers,
)

print("JWT")
print(jwt)



url = "https://webapi.egauge.net/_mock/webapi/4.6/openapi/config/local"

query = {
  "max-depth": "1",
  "filter": "string"
}

headers = {"Authorization": f"Bearer {jwt}"}

response = requests.get(url, headers=headers, params=query)

data = response.json()
print("LOCAL\n")
print(data)


url = "https://webapi.egauge.net/_mock/webapi/4.6/openapi/capture"

query = {
  "C": "0",
  "M": "any",
  "L": "0",
  "R": "true",
  "T": "0",
  "c": "0",
  "d": "0",
  "i": "true",
  "n": "0",
  "p": "0",
  "r": "true",
  "t": "true"
}

headers = {"Authorization": f"Bearer {jwt}"}

response = requests.get(url, headers=headers, params=query)

print("CAPTURE\n")
data = response.json()
print(data)