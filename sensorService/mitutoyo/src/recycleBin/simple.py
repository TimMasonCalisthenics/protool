import json
import re
import requests


# ---------- Load config ----------
with open("config.json", "r") as f:
    config = json.load(f)

machine_id = config["machine_id"]
post_url = config["post_url"]
mapping = config["mapping"]


# ---------- Parse raw string ----------
def parse_raw(data: str):
    pattern = r'^([A-Z]+\d+)([+-]\d+(\.\d+)?)$'
    match = re.match(pattern, data.strip())

    if not match:
        raise ValueError("Invalid format")

    key = match.group(1)
    value = float(match.group(2))

    return key, value


# ---------- Build JSON payload ----------
def build_payload(raw_list):
    payload_data = []

    for raw in raw_list:
        key, value = parse_raw(raw)

        if key not in mapping:
            continue  # หรือ raise error ตาม design

        payload_data.append({
            "key_value": mapping[key],
            "value": value
        })

    return {
        "device_id": machine_id,
        "data": payload_data
    }


# ---------- Example usage ----------
raw_input = [
    "AB123+50.0",
    "AB124-10.5"
]

payload = build_payload(raw_input)

print(json.dumps(payload, indent=2))


# ---------- POST ----------
response = requests.post(post_url, json=payload)

print(response.status_code, response.text)