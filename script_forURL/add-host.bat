@echo off

set HOST_NAME=%1

if "%HOST_NAME%"=="" (
    set HOST_NAME=measurement.protool
)

set HOST_ENTRY=127.0.0.1 %HOST_NAME%
set HOST_FILE=C:\Windows\System32\drivers\etc\hosts

echo Checking hosts file for %HOST_NAME%...

findstr /C:"%HOST_NAME%" "%HOST_FILE%" >nul

if %errorlevel%==0 (
    echo Host already exists.
) else (
    echo Adding host entry...
    echo %HOST_ENTRY% >> "%HOST_FILE%"
    echo Host added.
)

echo.
echo Flushing DNS cache...
ipconfig /flushdns

echo Done.
pause