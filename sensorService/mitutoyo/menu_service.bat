@echo off
setlocal enabledelayedexpansion

:: ==========================================
:: CONFIGURATION
:: ==========================================
set "MY_SVC_NAME=MitutoyoService"
set "MY_SVC_DISPLAY=MitutoyoService (Python)"
@REM set "TARGET_EXE=C:\Users\user\Documents\python_webDev\sensorService\mitutoyo\src\bin\main.exe"
set "TARGET_EXE=C:\Users\user\Documents\python_webDev\sensorService\airgauge\src\bin\MitutoyoService.exe"
:: ==========================================

:: ตรวจสอบสิทธิ์ Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please run this script as Administrator!
    pause
    exit /b
)

:MENU
cls
echo ==================================================
echo      Service Management Tool: %MY_SVC_NAME%
echo ==================================================
echo  1. Install / Reinstall Service
echo  2. Restart Service (Quick Reset)
echo  3. Uninstall / Remove Service
echo  4. Check Service Status
echo  5. Exit
echo ==================================================
set /p "CHOICE=Select an option (1-5): "

if "%CHOICE%"=="1" goto INSTALL
if "%CHOICE%"=="2" goto RESTART
if "%CHOICE%"=="3" goto UNINSTALL
if "%CHOICE%"=="4" goto STATUS
if "%CHOICE%"=="5" exit
goto MENU

:INSTALL
echo.
echo [1/3] Stopping and Removing old service (if any)...
sc stop "%MY_SVC_NAME%" >nul 2>&1
sc delete "%MY_SVC_NAME%" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Installing Service...
py -3 "%~dp0service_wrapper.py" --startup auto install

echo [3/3] Configuring Registry Path...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\%MY_SVC_NAME%\Parameters" /v "ExePath" /t REG_SZ /d "%TARGET_EXE%" /f

sc start "%MY_SVC_NAME%"
goto FINISH

:RESTART
echo.
echo Restarting %MY_SVC_NAME%...
sc stop "%MY_SVC_NAME%"
timeout /t 2 /nobreak >nul
sc start "%MY_SVC_NAME%"
goto FINISH

:UNINSTALL
echo.
echo [1/2] Stopping Service...
sc stop "%MY_SVC_NAME%"
timeout /t 2 /nobreak >nul

echo [2/2] Removing Service and Registry...
sc delete "%MY_SVC_NAME%"
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\%MY_SVC_NAME%" /f >nul 2>&1
goto FINISH

:STATUS
echo.
echo Current Status:
sc query "%MY_SVC_NAME%" | findstr "STATE"
if %errorLevel% neq 0 echo Service is not installed.
pause
goto MENU

:FINISH
echo.
echo Operation completed.
echo --------------------------------------------------
sc query "%MY_SVC_NAME%" | findstr "STATE"
pause
goto MENU