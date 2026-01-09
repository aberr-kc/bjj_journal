@echo off
echo Building BJJ Journal Connect IQ App...
echo.

REM Set portable Java path
set JAVA_HOME=C:\Users\barra\Downloads\CommonFiles\Java64
set PATH=%JAVA_HOME%\bin;%PATH%

REM Use your specific SDK location
set SDK_PATH="C:\Users\barra\AppData\Roaming\Garmin\ConnectIQ\Sdks\connectiq-sdk-win-8.4.0-2025-12-03-5122605dc\bin\"

echo Checking Java...
java -version
if %errorlevel% neq 0 (
    echo ERROR: Java not found at %JAVA_HOME%
    pause
    exit /b 1
)

if not exist %SDK_PATH%monkeyc.bat (
    echo ERROR: monkeyc.bat not found at %SDK_PATH%
    echo Please check your Connect IQ SDK installation
    pause
    exit /b 1
)

echo Using SDK at: %SDK_PATH%
echo Using Java at: %JAVA_HOME%
echo.

REM Generate developer key using Python cryptography
if not exist developer_key.der (
    echo Generating developer key...
    python generate_key.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to generate key. Installing cryptography...
        pip install cryptography
        python generate_key.py
    )
)

REM Build using jungle file
echo Building with jungle file...
%SDK_PATH%monkeyc.bat -d vivoactive4 -f monkey.jungle -o BJJTest.prg -y developer_key.der

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build successful! BJJTest.prg created
    echo.
    echo Next steps:
    echo 1. Start your journal server: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    echo 2. Copy BJJTest.prg to your Garmin watch APPS folder
    echo 3. Or test in simulator with: connectiq
) else (
    echo.
    echo ❌ Build failed - check errors above
)

pause