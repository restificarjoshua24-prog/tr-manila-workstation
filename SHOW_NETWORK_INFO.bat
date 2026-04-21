@echo off
title TR Manila Workstation - Network Information
color 0B
cls

echo.
echo ============================================================
echo   TR MANILA WORKSTATION SYSTEM - NETWORK INFORMATION
echo ============================================================
echo.

echo Finding your computer's IP address...
echo.

REM Get IPv4 address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo ============================================================
    echo   YOUR COMPUTER'S IP ADDRESS
    echo ============================================================
    echo.
    echo   IP Address: %%a
    echo.
    echo ============================================================
    echo.
    echo   ACCESS FROM OTHER DEVICES:
    echo ============================================================
    echo.
    echo   1. Make sure other device is on the SAME WiFi network
    echo   2. Open web browser on that device
    echo   3. Go to: http:%%a:5000
    echo.
    echo   Example URLs to try:
    for /f "tokens=2 delims=:" %%b in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
        echo   - http:%%b:5000
    )
    echo.
    echo ============================================================
    echo.
)

echo.
echo   FIREWALL SETUP (if needed):
echo   ----------------------------------------------------------
echo   If other devices can't connect, run this as Administrator:
echo.
echo   netsh advfirewall firewall add rule name="TR Manila Port 5000" dir=in action=allow protocol=TCP localport=5000
echo.
echo ============================================================
echo.
echo   MOBILE DEVICE INSTRUCTIONS:
echo ============================================================
echo.
echo   iPhone/iPad:
echo   1. Open Safari
echo   2. Go to the URL shown above
echo   3. Tap Share -^> Add to Home Screen
echo.
echo   Android:
echo   1. Open Chrome
echo   2. Go to the URL shown above
echo   3. Tap Menu -^> Add to Home screen
echo.
echo ============================================================
echo.
echo   CURRENT STATUS:
echo ============================================================
echo.

REM Check if app is running
netstat -an | findstr :5000 >nul 2>&1
if %errorlevel%==0 (
    echo   Status: SERVER IS RUNNING on port 5000
    echo.
    echo   Other devices can now connect!
) else (
    echo   Status: SERVER IS NOT RUNNING
    echo.
    echo   Please start the application first by running:
    echo   - START_APPLICATION.bat
    echo   or
    echo   - python app.py
)

echo.
echo ============================================================
echo.
echo   For more help, see: NETWORK_ACCESS_GUIDE.md
echo.
echo ============================================================
echo.
pause