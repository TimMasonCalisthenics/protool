@echo off
echo [1/4] Killing existing processes...
taskkill /F /IM main.exe /T 2>nul

echo [2/4] Cleaning old build files and cache...
:: ลบโฟลเดอร์ผลลัพธ์
if "%1"=="clean" (
    if exist bin rmdir /s /q bin
    :: ลบโฟลเดอร์ Build Cache ของ Nuitka (สำคัญมาก)
    if exist main.build rmdir /s /q main.build
    if exist main.onefile-build rmdir /s /q main.onefile-build
)

echo [3/4] Starting Nuitka Build (Fresh Start)...
:: สั่ง Build ใหม่โดยไม่เอาโฟลเดอร์ code เข้าไป เพื่อให้มันไล่ตาม import เอง
nuitka --standalone --onefile --output-dir=bin --include-data-dir=config=config main.py --output-filename=AirGaugeService.exe --company-name="protool" --product-name="AirGaugeService" --file-version=1.0.0

echo [4/4] Preparing External Dependencies...
:: ก๊อบปี้ IBR_lib มาวางคู่กับ exe เพื่อให้ sys.executable ทำงานได้
xcopy /E /I /Y "IBR_lib" "bin\IBR_lib"

:: ก๊อบปี้ config.json ไปวางคู่กับ exe
xcopy "config\config.json" "bin\config\" /Y /I

echo =========================================
echo BUILD COMPLETE! Please run: bin\main.exe
echo =========================================
pause