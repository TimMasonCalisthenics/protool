@echo off
setlocal
:: ==========================================
:: ระบุชื่อ Service ที่ต้องการลบให้ตรงกับตอนติดตั้ง
set "S_NAME=MyService_Alpha"
:: ==========================================

:: ตรวจสอบสิทธิ์ Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    pause
    exit /b
)

echo --------------------------------------------------
echo  Stopping and Removing Service: %S_NAME%
echo --------------------------------------------------

:: 1. สั่งหยุด Service
echo Stopping...
sc stop "%S_NAME%"

:: 2. รอสักครู่เพื่อให้ Service หยุดสนิท
timeout /t 2 /nobreak >nul

:: 3. ลบ Service ออกจากระบบ Windows
echo Removing...
sc delete "%S_NAME%"

:: 4. ลบ Registry Key ที่เราสร้างไว้ (แถมให้เพื่อความสะอาด)
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\%S_NAME%" /f >nul 2>&1

echo --------------------------------------------------
echo  [%S_NAME%] has been uninstalled successfully.
echo --------------------------------------------------
pause