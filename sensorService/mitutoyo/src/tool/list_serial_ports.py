import serial.tools.list_ports

def list_ports():
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("No serial ports found")
        return

    for port in ports:
        print("=" * 50)
        print(f"Device        : {port.device}")
        print(f"Description   : {port.description}")
        print(f"HWID          : {port.hwid}")
        print(f"VID           : {port.vid}")
        print(f"PID           : {port.pid}")
        print(f"Serial Number : {port.serial_number}")
        print(f"Manufacturer  : {port.manufacturer}")
        print(f"Product       : {port.product}")
        print(f"Location      : {port.location}")

if __name__ == "__main__":
    list_ports()