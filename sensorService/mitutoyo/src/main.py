import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import sys
import json
import requests
import time

# นำเข้า class จากไฟล์ของคุณ
from serialManager import SerialManager
from dataProcessor import DataProcessor

# ตั้งค่า Path ให้ถูกต้องแม่นยำ
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class SerialApp:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.serial_manager = None
        self.processor = None
        self.post_url = None
        self.buffer = []

    def setup(self):
        """โหลดค่า Config และเชื่อมต่อ Serial"""
        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.serial_manager = SerialManager(config["serial"])
        self.processor = DataProcessor(config["machine_id"], config["mapping"])
        self.post_url = config["post_url"]
        self.serial_manager.connect()

    def process_once(self):
        """ทำงาน 1 รอบ (อ่าน data -> ส่ง API)"""
        try:
            line = self.serial_manager.read_line()
            if line:
                print(f"[{time.strftime('%H:%M:%S')}] Received: {line}")
                self.buffer.append(line)

            # if len(self.buffer) >= 5:
            if True:
                payload = self.processor.build_payload(self.buffer)
                if payload.get("measurements"):                    
                    requests.post(self.post_url, json=payload, timeout=5)
                self.buffer.clear()

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2) # พักแป๊บเดียวเผื่อ Error รัวๆ
            self.serial_manager.reconnect()


if __name__ == "__main__":
    # ---- DEBUG MODE (รันปกติด้วย python script.py) ----
    print("DEBUG MODE: Press Ctrl+C to stop")
    app = SerialApp()
    try:
        app.setup()
        while True:
            app.process_once()
            time.sleep(0.1) # ในโหมด Debug ใช้ sleep ปกติได้
    except KeyboardInterrupt:
        print("\nStopped by user.")
