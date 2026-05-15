@echo off
setlocal
set "MY_SVC_NAME=MyService_Alpha"

echo Resetting %MY_SVC_NAME%...

:: หยุดการทำงาน (Force stop ถ้าจำเป็น)
sc stop %MY_SVC_NAME%

:: รอสักครู่เพื่อให้ Process คืนทรัพยากร
timeout /t 2 /nobreak >nul

:: เริ่มการทำงานใหม่
sc start %MY_SVC_NAME%

echo.
echo Check Status:
sc query %MY_SVC_NAME% | findstr STATE
pause