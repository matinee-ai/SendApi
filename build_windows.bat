@echo off
echo Building SendApi for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Building executable with PyInstaller...
pyinstaller --clean sendapi.spec

if errorlevel 1 (
    echo Error: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo The executable can be found in: dist\SendApi.exe
echo.
echo To run the application, double-click on SendApi.exe
echo.
pause 