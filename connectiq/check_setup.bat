@echo off
echo Checking Connect IQ setup...
echo.

echo 1. Checking Connect IQ SDK...
monkeyc --version
if %errorlevel% neq 0 (
    echo ERROR: monkeyc not found. Check SDK installation.
    pause
    exit /b 1
)

echo.
echo 2. Checking simulator...
connectiq --version
if %errorlevel% neq 0 (
    echo WARNING: connectiq simulator not found, but not required for device testing
)

echo.
echo 3. Your computer's IP addresses:
ipconfig | findstr "IPv4"

echo.
echo 4. Checking if journal server is running...
curl -s http://127.0.0.1:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Journal server is running
) else (
    echo ❌ Journal server not running - start with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
)

echo.
echo 5. Project structure check:
if exist "manifest.xml" (
    echo ✅ manifest.xml found
) else (
    echo ❌ manifest.xml missing
)

if exist "source\BJJTestApp.mc" (
    echo ✅ BJJTestApp.mc found
) else (
    echo ❌ BJJTestApp.mc missing
)

echo.
echo Setup verification complete!
echo.
echo Next steps:
echo 1. Update IP address in source\BJJTestApp.mc (line ~95)
echo 2. Build the app: monkeyc -o BJJTest.prg -m manifest.xml -z resources\drawables\drawables.xml -z resources\strings\strings.xml source\BJJTestApp.mc
echo 3. Test on simulator or sideload to device
echo.
pause