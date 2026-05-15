import json
import os
import threading
import time

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, path="config/config.json"):
        if self._initialized:
            return
            
        # ใช้ Absolute Path เพื่อป้องกันปัญหาเวลาเปลี่ยน Working Directory
        self.path = os.path.abspath(path)
        self._config = {}
        self._last_mtime = 0
        self._data_lock = threading.Lock()

        self.load()

        # สร้าง Thread เฝ้าดูไฟล์
        thread = threading.Thread(target=self._watch_file, name="ConfigWatcher", daemon=True)
        thread.start()
        
        self._initialized = True
        print(f"[*] ConfigManager Online (PID: {os.getpid()})")

    def load(self):
        if not os.path.exists(self.path):
            print(f"[!] Config file not found: {self.path}")
            return

        with self._data_lock:
            try:
                # หน่วงเวลาเล็กน้อยเพื่อให้ OS เขียนไฟล์เสร็จสมบูรณ์ (ป้องกันไฟล์ว่างตอนกำลังเซฟ)
                time.sleep(0.1) 
                
                with open(self.path, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                
                # อัปเดตข้อมูลและเวลาล่าสุด
                self._config = new_data
                self._last_mtime = os.path.getmtime(self.path)
                print(f"[+] Config reloaded at {time.strftime('%H:%M:%S')}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[x] Reload failed (JSON/IO Error): {e}")
            except Exception as e:
                print(f"[x] Unexpected error: {e}")

    def _watch_file(self):
        while True:
            try:
                if os.path.exists(self.path):
                    current_mtime = os.path.getmtime(self.path)
                    if current_mtime > self._last_mtime:
                        self.load()
            except Exception:
                pass
            time.sleep(2)

    def update(self, key, value):
        """อัปเดตค่าเดิม หรือเพิ่ม Field ใหม่เข้าไปใน Config"""
        with self._data_lock:
            try:                
                self._config[key] = value                
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4, ensure_ascii=False)           
                self._last_mtime = os.path.getmtime(self.path)
                
                print(f"[✓] Config updated: {key} = {value}")
                return True
            except Exception as e:
                print(f"[x] Update failed: {e}")
                return False
    def update_nested(self, keys, value):
        """
        อัปเดตค่าแบบเจาะจง Path เช่น keys=['airgauge', 'key1', 'x']
        """
        with self._data_lock:
            try:
                # ไล่ลงไปตามโครงสร้าง dict
                target = self._config
                for key in keys[:-1]:
                    target = target.setdefault(key, {})
                
                target[keys[-1]] = value

                # เขียนลงไฟล์
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4, ensure_ascii=False)
                
                self._last_mtime = os.path.getmtime(self.path)
                return True
            except Exception as e:
                print(f"Update nested failed: {e}")
                return False
    def update_multiple(self, data_dict):        
        if not isinstance(data_dict, dict):
            return False
            
        with self._data_lock:
            try:
                self._config.update(data_dict)
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4, ensure_ascii=False)
                self._last_mtime = os.path.getmtime(self.path)
                print(f"[✓] Multiple configs updated")
                return True
            except Exception as e:
                print(f"[x] Batch update failed: {e}")
                return False

    def get(self, key, default=None):
        with self._data_lock:
            return self._config.get(key, default)
    def all(self):
        with self._data_lock:
            return self._config.copy()
    
# สร้าง Instance ทิ้งไว้เพื่อให้เป็น Singleton ทั่วทั้งระบบ
cfg = ConfigManager()