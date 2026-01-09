@echo off
echo Starting build...
pause

echo Checking SDK path...
set SDK_PATH="C:\Users\barra\AppData\Roaming\Garmin\ConnectIQ\Sdks\connectiq-sdk-win-8.4.0-2025-12-03-5122605dc\bin\"
echo SDK_PATH is: %SDK_PATH%
pause

echo Checking if monkeyc.bat exists...
if exist %SDK_PATH%monkeyc.bat (
    echo Found monkeyc.bat
) else (
    echo monkeyc.bat NOT found
)
pause

echo Running build command...
%SDK_PATH%monkeyc.bat -o BJJTest.prg -m manifest.xml -z resources\drawables\drawables.xml -z resources\strings\strings.xml source\BJJTestApp.mc

echo Build command finished
pause