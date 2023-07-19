import subprocess
import sys


def install(package):
    try:
        import importlib
        importlib.import_module(package)
        print(f"{package} module is already installed.")
    except ImportError:
        print(f"{package} module is not installed. Attempting to install...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} module has been installed.")


# Use the function to check and install requests
install('requests')

import requests
import os
import json
import datetime
import sys
import time
import hmac
import hashlib
import base64


def hex_to_base32(hex_secret):
    # Convert the hexadecimal secret to bytes
    secret_bytes = bytes.fromhex(hex_secret)

    # Base32 encode the bytes and decode to a string
    base32_secret = base64.b32encode(secret_bytes).decode()

    return base32_secret


# Function to generate the TOTP code
def generate_totp(secret):
    interval = int(time.time()) // 120
    key = base64.b32decode(secret, casefold=True)
    msg = int.to_bytes(interval, length=8, byteorder='big')
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    truncated_hash = h[offset:offset + 4]
    code = int.from_bytes(truncated_hash, byteorder='big') & 0x7FFFFFFF
    return '{:06d}'.format(code % 10 ** 6)  # Ensure 6-digit code by using modulo 10^6


# Load the client secret from the JSON file
with open('client_secret.json') as f:
    data = json.load(f)
    client_secret = data['secret']

# Generate the TOTP code
totp_code = generate_totp(hex_to_base32(client_secret))

api_base_url = 'http://localhost:5600/api'  # replace with your actual base API URL
upload_url = 'https://activity-watcher.2btechprojects.com/api/upload'  # replace with your actual upload API URL
timestamp_file = 'timestamps.json'
default_date = datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                               microsecond=0).isoformat()  # start with current day for first run

# Initialize or load timestamps
if os.path.exists(timestamp_file):
    with open(timestamp_file, 'r') as file:
        timestamps = json.load(file)
else:
    timestamps = {}

# Get list of buckets
try:
    response = requests.get(f'{api_base_url}/0/buckets')
    buckets = response.json()
except Exception as e:
    print(f"Failed to get the list of buckets due to {str(e)}")
    sys.exit(1)

for bucket in buckets.values():
    bucket_id = bucket['id']
    bucket_type = bucket['type']
    hostname = bucket['hostname']

    # Only process buckets of type afkstatus or currentwindow
    if bucket_type not in ['afkstatus', 'currentwindow']:
        continue

    # Get last upload time for bucket or default to current day
    last_upload_time = timestamps.get(bucket_id, default_date)

    # Get events since last upload
    params = {
        'start': last_upload_time
    }

    url = f'{api_base_url}/0/buckets/{bucket_id}/events'

    try:
        response = requests.get(url, params=params)
        events = response.json()
    except Exception as e:
        print(f"Failed to get events due to {str(e)}")
        sys.exit(1)

    # Upload events to server
    data = {
        'bucket': bucket,
        'events': events
    }
    headers = {
        'Content-Type': 'application/json',
        'AppId': 'MyApp',
        'X-TOTP-Code': totp_code,
        'Host-Name': hostname,
    }

    try:
        response = requests.post(upload_url, headers=headers, data=json.dumps(data))
    except Exception as e:
        print(f"Failed to upload events due to {str(e)}")
        sys.exit(1)

    # If upload was successful, update timestamp
    if response.status_code == 200:
        # print('uploaded.....')
        timestamps[bucket_id] = datetime.datetime.now().isoformat()

    # print(response)

# Save timestamps
with open(timestamp_file, 'w') as file:
    json.dump(timestamps, file)
