import win32serviceutil
import win32service
import win32event
import servicemanager
import winreg
import subprocess
import sys
import os

# อ่านชื่อจาก Environment Variable ที่ส่งมาจาก Batch
# ถ้าไม่มีให้ใช้ชื่อเริ่มต้น
SVC_NAME = os.environ.get("MY_SVC_NAME", "Mitutoyo_service")
SVC_DISPLAY = os.environ.get("MY_SVC_DISPLAY", "Mitutoyo_service(Python)")

class MyExeService(win32serviceutil.ServiceFramework):
    _svc_name_ = SVC_NAME
    _svc_display_name_ = SVC_DISPLAY

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.exe_path = self._get_exe_path()

    def _get_exe_path(self):
        try:
            key_path = f"SYSTEM\\CurrentControlSet\\Services\\{self._svc_name_}\\Parameters"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            path, _ = winreg.QueryValueEx(key, "ExePath")
            winreg.CloseKey(key)
            return path
        except: return None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        if self.exe_path:
            subprocess.run(["taskkill", "/F", "/IM", os.path.basename(self.exe_path)], shell=True)

    def SvcDoRun(self):
        self.main()

    def main(self):
        log_file = os.path.join(os.path.dirname(__file__), "debug_log.txt")
        try:
            if not self.exe_path:
                with open(log_file, "a") as f: f.write("Error: ExePath is None\n")
                return

            exe_dir = os.path.dirname(self.exe_path)
            process = subprocess.Popen(self.exe_path, cwd=exe_dir)

            while self.is_running:
                if process.poll() is not None and self.is_running:
                    process = subprocess.Popen(self.exe_path, cwd=exe_dir)
                if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                    break
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"Critical Error: {str(e)}\n")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyExeService)