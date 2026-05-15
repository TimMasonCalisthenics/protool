import ctypes
import time
from ctypes import wintypes
import os
from contextlib import contextmanager
import sys


def get_base_path(external=True):    
    if hasattr(sys, "frozen"):
        # ถ้าเป็น Onefile/Standalone
        if external:
            # คืนค่าโฟลเดอร์ที่ .exe วางอยู่ (ใช้ sys.argv[0])
            return os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            # คืนค่าโฟลเดอร์ชั่วคราว (ใช้ __file__)
            return os.path.dirname(os.path.abspath(__file__))
    
    # ถ้ารัน .py ปกติ
    return os.path.dirname(os.path.abspath(__file__))
class IMBController:
    def __init__(self, dll_path="ibr_ddk.dll"):
        self.is_connected = False
        try:
            ##original
            # self.script_dir = os.path.dirname(os.path.abspath(__file__))
            # self.dll_folder = os.path.join(self.script_dir, "IBR_lib")
            # dll_full_path = os.path.join(self.dll_folder, "ibr_ddk.dll")

            
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.dll_folder = os.path.join(base_dir, "IBR_lib")
            dll_full_path = os.path.join(self.dll_folder, "ibr_ddk.dll")
            self.lib = ctypes.WinDLL(dll_full_path)

            # --- กำหนด Signature ของฟังก์ชันให้ชัดเจน (หัวใจสำคัญ) ---

            # Device_Init(int handle, char* path, int window, int mode)
            self.lib.Device_Init.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
            self.lib.Device_Init.restype = ctypes.c_int

            # Device_Value(int channel, int unit, double* value)
            # เราใช้ POINTER(c_double) แทนการส่งแบบลอยๆ
            self.lib.Device_Value.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
            self.lib.Device_Value.restype = ctypes.c_int

            self.lib.Device_Setup.argtypes = [ctypes.c_int, ctypes.c_char_p, wintypes.HWND, ctypes.c_char_p]
            self.lib.Device_Setup.restype = ctypes.c_int

            print("DLL Loaded and Signatures Defined Successfully")
        except Exception as e:
            print(f"Failed to load DLL: {e}")

    @contextmanager
    def _hold_cwd(self, temp_path):
        old_pwd = os.getcwd()
        os.chdir(temp_path)
        try:
            yield
        finally:
            os.chdir(old_pwd)

    # def init_device(self, ddk_file="IMB_Test.ddk"):
    #     # ไฟล์ .ddk มักต้องอ่านจาก path ตรงๆ หรือชื่อไฟล์ในโฟลเดอร์เดียวกัน
    #     ddk_full_path = os.path.join(self.dll_folder, ddk_file)
    #     with self._hold_cwd(self.dll_folder):
    #         # บางที DLL ต้องการแค่ชื่อไฟล์ ไม่เอา Path เต็ม ลองเช็คดูครับ
    #         res = self.lib.Device_Init(1, ddk_full_path.encode('utf-8'), 0, 0)
    #     return res == 0
    def init_device(self, ddk_file="IMB_Test.ddk"):
        try:

            ddk_full_path = os.path.join(self.dll_folder, ddk_file)
            with self._hold_cwd(self.dll_folder):
                # บางที DLL ต้องการแค่ชื่อไฟล์ ไม่เอา Path เต็ม ลองเช็คดูครับ
                res = self.lib.Device_Init(1, ddk_full_path.encode('utf-8'), 0, 0)
            res = res == 0
            self.is_connected = res
            return res
        except Exception as e:
            print(f"Error initializing device: {e}")
            return False

    def get_value(self, channel):
        # จองหน่วยความจำสำหรับ double (8 bytes)
        mv = ctypes.c_double(0.0)

        # เรียกใช้โดยส่ง pointer ผ่าน byref
        # ค่า unit (ตัวที่สอง) ลองเช็คใน C# ว่าส่ง 1 หรือ 0
        res = self.lib.Device_Value(ctypes.c_int(1), ctypes.c_int(channel), ctypes.byref(mv))

        if res == 0:
            return mv.value
        else:
            # ถ้าไม่ได้ 0 ลอง Print ดูว่า Error Code คืออะไร
            # เช่น -1 อาจหมายถึงหา Channel ไม่เจอ
            return f"Error({res})"
    def get_value_by_moduleChannel(self, module , channel):
        # จองหน่วยความจำสำหรับ double (8 bytes)
        mv = ctypes.c_double(0.0)

        # เรียกใช้โดยส่ง pointer ผ่าน byref
        # ค่า unit (ตัวที่สอง) ลองเช็คใน C# ว่าส่ง 1 หรือ 0
        res = self.lib.Device_Value(ctypes.c_int(module), ctypes.c_int(channel), ctypes.byref(mv))

        if res == 0:
            return mv.value
        else:
            # ถ้าไม่ได้ 0 ลอง Print ดูว่า Error Code คืออะไร
            # เช่น -1 อาจหมายถึงหา Channel ไม่เจอ
            return f"Error({res})"

    def close_device(self):
        try:
            self.is_connected = False
            self.lib.Device_DeInit()
        except Exception as e:
            print(f"Error closing device: {e}")




# --- ส่วนทดสอบ ---
if __name__ == "__main__":
    air_gauge = IMBController()
    if air_gauge.init_device():
        print("Device Initialized")
        try:
            while True:
                results = []
                for i in range(1, 4): # ลองอ่าน 1, 2, 3
                    val = air_gauge.get_value(i)
                    results.append(f"CH{i}: {val}")
                print(" | ".join(results))
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopping...")
    else:
        print("Initialization Failed!")

    air_gauge.close_device()