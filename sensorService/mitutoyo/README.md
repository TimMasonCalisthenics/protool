# คู่มือการติดตั้งและใช้งาน build.bat (สำหรับการ Build Executable ด้วย Nuitka)

ไฟล์ `build.bat` ใช้สำหรับแปลงโค้ด Python (`main.py`) ของโปรเจกต์นี้ให้เป็นไฟล์ Executable (.exe) แบบ Standalone (Onefile) โดยอัตโนมัติ 

## สิ่งที่ต้องติดตั้ง (Prerequisites)

ก่อนที่จะรัน `build.bat` ได้ คุณจำเป็นต้องติดตั้งโปรแกรมและไลบรารีที่เกี่ยวข้องดังนี้:

1. **Python**: ตรวจสอบให้แน่ใจว่าได้ติดตั้ง Python ไว้ในเครื่องแล้ว (แนะนำ Python 3.8 ขึ้นไป) และตั้งค่า Path ใน Environment Variables ให้เรียบร้อย
2. **C Compiler** (สำหรับ Nuitka): Nuitka จำเป็นต้องใช้ C Compiler ในการคอมไพล์โค้ด (เช่น MinGW-w64 หรือ Microsoft Visual Studio)
3. **ติดตั้งไลบรารีใน `requirements.txt`**:
   เปิด Command Prompt หรือ Terminal ในโฟลเดอร์เดียวกับไฟล์ `requirements.txt` และรันคำสั่งต่อไปนี้เพื่อติดตั้งไลบรารีที่จำเป็น (รวมถึง Nuitka):
   ```cmd
   pip install -r requirements.txt
   ```
   *(ไลบรารีหลักๆ ได้แก่: `waitress`, `flask`, `tenacity`, และ `Nuitka`)*

## การใช้งาน `build.bat`

เพื่อเริ่มต้นการ Build ระบบ ให้ทำตามขั้นตอนดังนี้:

1. เปิดเข้าไปที่โฟลเดอร์ `src` ของโปรเจกต์ (ซึ่งเป็นที่เก็บไฟล์ `build.bat` และ `main.py`)
2. ดับเบิลคลิกที่ไฟล์ `build.bat` หรือรันผ่าน Command Prompt:
   ```cmd
   build.bat
   ```
3. รอให้กระบวนการทำงานจนเสร็จสมบูรณ์ ซึ่งหน้าต่างจะแสดงข้อความ `BUILD COMPLETE! Please run: bin\main.exe` ให้กดคีย์ใดๆ เพื่อปิดหน้าต่าง

## ลำดับการทำงานของ `build.bat`

เมื่อรัน `build.bat` ระบบจะทำงาน 4 ขั้นตอน ดังนี้:

**[1/4] Killing existing processes...**
- ตรวจสอบและบังคับปิด (Task Kill) ตัวโปรแกรม `main.exe` เก่าที่อาจจะยังทำงานค้างอยู่ เพื่อป้องกันการ Error ขณะเขียนทับไฟล์ใหม่

**[2/4] Cleaning old build files and cache...**
- ลบโฟลเดอร์ผลลัพธ์การ Build เก่าๆ (โฟลเดอร์ `bin`)
- ลบโฟลเดอร์ Cache ของ Nuitka (`main.build`, `main.onefile-build`) เพื่อบังคับให้ระบบเริ่มขั้นตอน Build ใหม่ทั้งหมดตั้งแต่ต้น ป้องกันบั๊กจากการใช้ของเก่า

**[3/4] Starting Nuitka Build (Fresh Start)...**
- ใช้ `nuitka` เพื่อทำการคอมไพล์ `main.py`
- จะทำการสร้างไฟล์ให้ออกมาเป็นไฟล์เดียวโดยสมบูรณ์ (`--onefile`, `--standalone`) 
- ส่งผลลัพธ์ทั้งหมดเก็บไว้ในโฟลเดอร์ `bin`
- นำโฟลเดอร์ `config` ใส่ประกอบเข้าไปในข้อมูลของโปรแกรมด้วย (`--include-data-dir=config=config`)

**[4/4] Preparing External Dependencies...**
- ทำการคัดลอกโฟลเดอร์ไลบรารีภายนอก `IBR_lib` เข้ามาวางคู่กับไฟล์ `.exe` ภายในโฟลเดอร์ `bin` เพื่อให้โปรแกรมสามารถเรียกใช้งานการอ้างอิงของ `sys.executable` ได้อย่างถูกต้อง

## ผลลัพธ์จากการ Build

เมื่อการทำงานบรรลุเสร็จสิ้น คุณจะได้รับไฟล์และโฟลเดอร์ดังต่อไปนี้ภายในโฟลเดอร์ `bin`:
- `main.exe`: ไฟล์โปรแกรมหลัก (.exe) ที่พร้อมใช้งานได้ทันทีโดยไม่ต้องติดตั้ง Python 
- โฟลเดอร์ `IBR_lib`: โฟลเดอร์ Dependencies ที่ได้ก๊อปปี้มาไว้ด้วย

**วิธีใช้งานโปรแกรมที่ Build แล้ว:** เข้าไปที่โฟลเดอร์ `bin` และเรียกเปิดใช้งาน `main.exe` ได้เลย
