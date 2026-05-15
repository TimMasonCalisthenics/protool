import time

class HardwareService:

    def __init__(self, config):
        self.config = config

    def read_device(self):

        retry = self.config.get("retry_count")
        delay = self.config.get("retry_delay")

        for i in range(retry):
            try:
                # ตัวอย่าง hardware call
                print("Reading hardware...")
                return {"value": 123}

            except Exception:
                print("retry", i)
                time.sleep(delay)

        raise Exception("Hardware failed")