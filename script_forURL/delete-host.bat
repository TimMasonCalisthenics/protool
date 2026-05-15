@echo off
set HOST_NAME=%1

if "%HOST_NAME%"=="" (
    set HOST_NAME=measurement.protool
)

set HOST_FILE=C:\Windows\System32\drivers\etc\hosts
set TEMP_FILE=%TEMP%\hosts_temp

echo Removing %HOST_NAME% from hosts...

findstr /V "%HOST_NAME%" "%HOST_FILE%" > "%TEMP_FILE%"

copy /Y "%TEMP_FILE%" "%HOST_FILE%" >nul
del "%TEMP_FILE%"

echo Flushing DNS cache...
ipconfig /flushdns

echo Host entry removed.
pause