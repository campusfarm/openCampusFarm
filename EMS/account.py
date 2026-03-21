import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))
print(os.environ.get("WT_USERNAME"))
print(os.environ.get("WT_PASSWORD"))
print(os.environ.get("WT_EMAIL"))
print(os.environ.get("WT_ORG"))
def make_account():

    # To register, use the code below. Please note that for these code examples we are using filler values for username
    # (freddo), password (the_frog), email (freddo@frog.org), org (freds world) and you should replace each if you are
    # copying and pasting this code.

    import requests
    register_url = 'https://api.watttime.org/register'
    params = {'username': os.environ.get("WT_USERNAME"),
            'password': os.environ.get("WT_PASSWORD"),
            'email': os.environ.get("WT_EMAIL"),
            'org': os.environ.get("WT_ORG")}
    rsp = requests.post(register_url, json=params)
    print(rsp.text)

if __name__ == "__main__":
   make_account()