#!/usr/bin/env python3
import requests
import json

# import one single custom format to radarr/sonarr(v4)
# example of custom format: https://github.com/PierreDurrr/arr-french-CF
# or here: https://github.com/santiagosayshey/Profilarr/ (attention, get rid of square brackets at begining of json file)

base_url = "http://<ip>:<radarr/sonarr_port>"
api_key = "yOuRaPiKeY"
json_file_path  = "./10bits.json"

def get_current_cf(base_url,api_key):
    return requests.get(f"{base_url}/api/v3/customformat", headers={'X-Api-Key': api_key}).json()

def make_request():
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    url = f"{base_url}/api/v3/customformat"

    headers = {"X-Api-Key": api_key}

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code in [200,201,202]:
            print("request successfully sent!")
        else:
            print(f"requests failed with status code: {response.status_code}")
            print("server response:", response.text)

    except requests.exceptions.RequestException as e:
        print("error while sending request:", e)

#print(get_current_cf(base_url,api_key))
make_request()

print("\nDon't forget to change the score of this custom format.")

