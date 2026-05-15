@echo off
setlocal
:: ==========================================
set "MY_SVC_NAME=Mitutoyo_service"
set "MY_SVC_DISPLAY=Mitutoyo_service(Python)"
set "TARGET_EXE=path"
:: ==========================================

py -3 "%~dp0service_wrapper.py" --startup auto install

:: 2. บันทึก Path ลง Registry
reg add "HKLM\SYSTEM\CurrentControlSet\Services\%MY_SVC_NAME%\Parameters" /v "ExePath" /t REG_SZ /d "%TARGET_EXE%" /f

sc start %MY_SVC_NAME%

echo.
echo Check Status:
sc query %MY_SVC_NAME% | findstr STATE
pause