# Serial Reader Windows Service

โปรแกรมสำหรับอ่านข้อมูลจาก Serial Port และส่งข้อมูลไปยัง Backend API โดยรันเป็น Windows Service (ทำงานเบื้องหลังอัตโนมัติ)

## 🛠 ความต้องการของระบบ (Prerequisites)

1. **Python 3.x**: ติดตั้ง Python และตรวจสอบว่าได้ติ๊กถูกที่ **"Add Python to PATH"** แล้ว
2. **Administrator Privilege**: ต้องใช้สิทธิ์ผู้ดูแลระบบ (Run as Administrator) ในการติดตั้ง Service
3. **Hardware**: อุปกรณ์ Serial (USB COM Port) ที่เชื่อมต่อกับเครื่อง

---

## 📂 โครงสร้างไฟล์ที่สำคัญ

* `main.py`: สคริปต์หลักของโปรแกรม (หัวใจการทำงาน)
* `config.json`: ไฟล์ตั้งค่า (Machine ID, COM Port, API URL)
* `serialManager.py` & `dataProcessor.py`: โมดูลจัดการ Serial และจัดการข้อมูล
* `manage_service.bat`: ไฟล์สำหรับจัดการ Service (Install, Start, Stop)
* `requirements.txt`: รายชื่อ Library ที่ต้องใช้

---

## 🚀 ขั้นตอนการติดตั้ง (Installation)

### 1. เตรียม Library
เปิด Command Prompt (CMD) หรือใช้ไฟล์ `manage_service.bat` เพื่อติดตั้ง Library ที่จำเป็น:
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่าโปรแกรม
แก้ไขไฟล์ config.json ให้ตรงกับหน้างาน:
serial: ตั้งค่า port (เช่น "COM3") และ baudrate
post_url: ที่อยู่ของ API ที่ต้องการส่งข้อมูลไป
mapping: ตั้งค่าการแมปข้อมูลตาม Protocol ของอุปกรณ์

🔍 การตรวจสอบการทำงาน (Monitoring)
ตรวจสอบสถานะ: ดูได้จากเมนู 6 (Check Status) ในไฟล์ .bat หรือดูที่แอป Services ของ Windows (ค้นหาชื่อ Serial Reader Service)
ตรวจสอบ Error: หาก Service ไม่รันหรือมีปัญหา ให้ตรวจสอบที่ Windows Event Viewer:
เปิด Start Menu พิมพ์ Event Viewer
ไปที่ Windows Logs > Application
มองหา Source: SerialReaderService

### คำแนะนำเพิ่มเติม:
หากในอนาคตคุณต้องการเปลี่ยนชื่อไฟล์หลักจาก `main.py`
เป็นชื่ออื่น อย่าลืมไปอัปเดตตัวแปรในไฟล์ `manage_service.bat` และใน `README.md` นี้ด้วยนะครับ