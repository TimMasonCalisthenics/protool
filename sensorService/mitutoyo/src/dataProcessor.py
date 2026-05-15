import re

class DataProcessor:
    def __init__(self, machine_id, mapping):
        self.machine_id = machine_id
        self.mapping = mapping

    def parse_raw(self, data: str):
        pattern = r'^([A-Z]+\d+)([+-]\d+(\.\d+)?)M$'
        match = re.match(pattern, data.strip())
        print( "data" , data)
        if not match:
            raise ValueError("Invalid format")

        key = match.group(1)
        value = float(match.group(2))

        return key, value

    def build_payload(self, raw_list):
        payload_data = []

        for raw in raw_list:
            try:
                key, value = self.parse_raw(raw)

                if key not in self.mapping:
                    continue

                payload_data.append({
                    "key_value": self.mapping[key],
                    "value": value
                })

            except Exception as e:
                print("Parse error:", e)

        return {
            "device_id": self.machine_id,
            "measurements": payload_data
        }