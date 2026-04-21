@echo off
title TR Manila Workstation System
color 0A
echo.
echo ============================================================
echo   TR MANILA WORKSTATION RESERVATION SYSTEM
echo ============================================================
echo.
echo   Starting application server...
echo   Please wait while the system initializes...
echo.
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Checking dependencies...
pip install -q -r requirements.txt

REM Run the launcher
echo.
echo Starting application...
echo.
python launcher.py

REM Deactivate virtual environment
deactivate

echo.
echo Application closed.
pause