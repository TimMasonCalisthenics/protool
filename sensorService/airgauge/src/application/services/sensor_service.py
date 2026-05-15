import threading
import time
import requests


class SensorService:    
    def __init__(self, controller, config):
        self.controller = controller
        self.config = config

        self.cache = {}
        self.lock = threading.Lock()

        self.poll_running = False # เริ่มต้นเป็น False เสมอ
        self.send_running = False

        self.poll_thread = None
        self.send_thread = None

        self.main_service_url = "http://localhost:5000/api/v1/airgauge"
        
        # ลบ self.start() ออกจากที่นี่ เพื่อไปเรียกจากภายนอกแทน (Safe Start)

    def start(self):
        """เริ่ม Polling อย่างปลอดภัย เช็คสถานะก่อนรัน"""
        with self.lock:
            if self.poll_running:
                print("SensorService is already running.")
                return
            self.poll_running = True

        self.poll_thread = threading.Thread(
            target=self._poll_loop,
            daemon=True
        )
        self.poll_thread.start()

    def stop(self):
        self.poll_running = False
        self.send_running = False
        
        # ป้องกัน RuntimeError: cannot join current thread
        current_t = threading.current_thread()
        if self.poll_thread and self.poll_thread.is_alive() and self.poll_thread != current_t:
            try:
                self.poll_thread.join(timeout=1.0)
            except RuntimeError:
                pass        
        
        # ปิด Device
        try:
            if hasattr(self.controller, 'close_device'):
                self.controller.close_device()
                print("Hardware Device Closed Successfully.")
        except Exception as e:
            print(f"Error during device shutdown: {e}")

    def _poll_loop(self):
        attempt = 0
        retry_cfg = self.config.get("retry", {})
        max_attempts = retry_cfg.get("max_attempts", 5)
        base_delay = retry_cfg.get("delay_ms", 500) / 1000.0  # แปลงเป็นวินาที
        backoff_factor = retry_cfg.get("backoff", 1.5)

        try:
            while self.poll_running:
                if not self.controller.is_connected:                                 
                    success = self.controller.init_device()
                    if not success:
                        attempt += 1                        
                        wait_time = base_delay * (backoff_factor ** (attempt - 1))                        
                        wait_time = min(30, wait_time)                        
                        print(f"HW Connection failed. Attempt {attempt}/{max_attempts}. Retrying in {wait_time:.2f}s...")                                                
                        if attempt >= max_attempts:
                            print("Warning: Reached max attempts. Still trying but at max delay.")
                        time.sleep(wait_time)
                        continue
                    attempt = 0
                    
                airgauge_config = self.config.get("airgauge", {})                
                try:
                    number_module = self.config.get("settings-airgauge", {}).get("number_module")
                    number_device = self.config.get("settings-airgauge", {}).get("number_device")

                    hardware_results = {}
                    global_device_index = 1
                    for module in range(1 , number_module + 1):
                        for device in range(1 , number_device + 1):
                            hw_val = self.controller.get_value_by_moduleChannel(module , device)
                            hardware_results[str(global_device_index)] = hw_val
                            global_device_index += 1
                            # print(f"Raw Hardware Value: {hw_val}")
                except Exception as e:
                    hw_val = f"Error: {e}"                
                for sensor_id , val in hardware_results.items():                    
                    sensor_data = airgauge_config.get(str(sensor_id))
                    key = sensor_data.get("key")
                    if not sensor_data:
                        continue

                    try:                        
                        current_raw = float(val)

                        x0 = float(sensor_data.get("x0", 0.0))
                        x1 = float(sensor_data.get("x1", 0.0))
                        y0 = float(sensor_data.get("y0", 0.0))
                        y1 = float(sensor_data.get("y1", 0.0))

                        denominator = x1 - x0                        
                        if denominator == 0:
                            cal_val = current_raw                            
                        else:                            
                            slope = (y1 - y0) / denominator
                            cal_val = y0 + (current_raw - x0) * slope
                        with self.lock:
                            self.cache[key] = current_raw , cal_val
                    except (ValueError, TypeError) as e:
                        with self.lock:
                            self.cache[key] = val , val                                         
                        print(f"ID {sensor_id}: Hardware/Config Error - Cannot calculate. (Value: {hw_val})")
                        
                
                    
                
                time.sleep(0.8)
        except Exception as e:
            print(f"Poll loop fatal error: {e}")
        finally:
            # สำคัญ: อย่าเรียก self.stop() ที่นี่ถ้าไม่อยากให้มันวนลูป Join ตัวเอง
            # ให้แค่เคลียร์ Flag ตัวเองพอ
            self.poll_running = False

    def start_sending(self):
        if self.send_running:
            return
        self.send_running = True
        self.send_thread = threading.Thread(
            target=self._send_loop,
            daemon=True
        )
        self.send_thread.start()

    def _send_loop(self):
        url = self.config.get("main_service_url", self.main_service_url)
        device_id = self.config.get("settings-airgauge", {}).get("Sensor-ID", "unknown-device")
        interval = self.config.get("settings-airgauge", {}).get("interval", 0.5)
        while self.send_running:
            with self.lock:
                data = dict(self.cache)

            try:
                payload = {
                    "device_id": device_id,
                    "measurements": [
                        {"key_value": str(k), "value": v[1]} 
                        for k, v in data.items()
                    ]
                }
                requests.post(url, json=payload, timeout=2)
            except Exception as e:
                print("send error", e)
            time.sleep(interval)

    def stop_sending(self):        
        self.send_running = False


    def get_sensorValue(self):        
        with self.lock:
            data_dict = dict(self.cache)
        return data_dict
    def get_sensorValue_cal(self):        
        with self.lock:
            data_dict = dict(self.cache)        
        data
        return data_dict
    def _clear_cache(self):
        with self.lock:
            self.cache = {}
    def get_setting_airgauge(self):
        return self.config.get("airgauge")
    def set_setting_airgauge(self , key  , value):
        return self.config.update_nested(["airgauge" , key ] , value)
    def get_all_settings(self):
        return self.config.all()
    def update_config(self, key, value):
        self.config.update(key, value)
    def update_allConfig(self, data_dict):
        self.config.update_multiple(data_dict)
        self._clear_cache()