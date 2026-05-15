import serial
import serial.tools.list_ports
import time


class SerialManager:
    def __init__(self, serial_config):
        self.config = serial_config
        self.ser = None
        self.connected = False
    def _match(self, value, target):
        """Return True if target empty or value == target"""
        if target in ("", None):
            return True
        if value is None:
            return False
        return str(value).lower() == str(target).lower()
    def find_serial_port(self):
        mode = self.config.get("mode", "auto")

        if mode == "manual":
            return self.config.get("port")

        vid = self.config.get("vid")
        pid = self.config.get("pid")
        serial_number = self.config.get("serial_number")
        hwid = self.config.get("hwid")

        for port in serial.tools.list_ports.comports():
            if not self._match(port.serial_number, serial_number):
                continue
            if not self._match(port.vid, vid):
                continue
            if not self._match(port.pid, pid):
                continue
            if not self._match(port.hwid, hwid):
                continue
            return port.device
        return None

    def connect(self, retry_interval=3):
        while not self.connected:
            try:
                port_name = self.find_serial_port()
                if not port_name:
                    print("Serial device not found. Retrying...")
                    time.sleep(retry_interval)
                    continue

                self.ser = serial.Serial(
                    port=port_name,
                    baudrate=self.config.get("baudrate", 115200),
                    timeout=self.config.get("timeout", 1)
                )

                self.connected = True
                print(f"Connected to {port_name}")

            except Exception as e:
                print("Connection failed:", e)
                time.sleep(retry_interval)

    def reconnect(self):
        print("Reconnecting...")
        self.connected = False
        if self.ser:
            try:
                self.ser.close()
            except:
                pass
        self.connect()

    def heartbeat(self, heartbeat_cmd="PING\n", expected_response="PONG"):
        try:
            self.ser.write(heartbeat_cmd.encode())
            response = self.ser.readline().decode().strip()
            return response == expected_response
        except:
            return False

    def read_line(self):
        try:
            line = self.ser.readline().decode().strip()
            if line:
                return line
            return None

        except Exception as e:
            print("Serial error:", e)
            self.reconnect()
            return None