@echo off
echo Checking Java installation...
echo.

java -version
if %errorlevel% equ 0 (
    echo ✅ Java is installed
    echo Now try running build.bat again
) else (
    echo ❌ Java is not installed or not in PATH
    echo.
    echo Please install Java:
    echo 1. Go to: https://adoptium.net/temurin/releases/
    echo 2. Download Java 17 or later
    echo 3. Install and make sure to add to PATH
    echo 4. Restart Command Prompt
    echo 5. Try build.bat again
)

pause