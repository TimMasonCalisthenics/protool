@echo off

set CLEAN_BUILD=false
if /I "%1"=="clean" set CLEAN_BUILD=true


echo [1/4] Killing existing processes...
taskkill /F /IM main.exe /T 2>nul

if "%CLEAN_BUILD%"=="true" (
    echo [2/4] Cleaning old build files and cache...

    if exist bin rmdir /s /q bin
    if exist main.build rmdir /s /q main.build
    if exist main.onefile-build rmdir /s /q main.onefile-build

) else (
    echo [2/4] Skipping cache clean (normal build)
)


echo [3/4] Starting Nuitka Build (Fresh Start)...
nuitka --standalone --onefile --output-dir=bin main.py --output-filename=MitutoyoService.exe --company-name="protool" --product-name="MitutoyoService" --file-version=1.0.0

echo [4/4] Preparing External Dependencies...
copy /Y "config.json" "bin\config.json" >nul

echo =========================================
echo BUILD COMPLETE! Please run: bin\main.exe
echo =========================================
pause