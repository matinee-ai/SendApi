@echo off
echo Starting API Tester...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Installing dependencies globally...
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

REM Run the application
echo Starting API Tester application...
python main.py

pause 