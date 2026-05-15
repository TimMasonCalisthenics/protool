import requests
import time
from device_controller import IMBController
from models import MeasurementModel

def main():
    device = IMBController()
    if device.init_device():
        # สมมติโหลดค่าจาก JSON มาแล้ว
        config_data = [...] # ข้อมูล JSON ที่คุณส่งมา
        models = [MeasurementModel(c) for c in config_data]

        try:
            while True:
                current_values = []
                for i in range(len(models)):
                    raw_x = device.get_value(i + 1)
                    if raw_x is not None:
                        y = models[i].calculate_y(raw_x)
                        current_values.append(y)

                # เปลี่ยนจาก Save CSV เป็นยิง Service
                send_to_service(current_values)

                time.sleep(0.5) # อ่านทุก 500ms
        except KeyboardInterrupt:
            device.close_device()

def send_to_service(values):
    url = "https://your-api.com/v1/log"
    payload = {"data": values}
    try:
        requests.post(url, json=payload, timeout=1)
    except:
        print("Network Error")

if __name__ == "__main__":
    main()