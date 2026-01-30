@echo off
echo Starting GitHub Tech Radar for Windows...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b
)

:: Create venv if not exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

:: Install dependencies
if not exist installed.flag (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies.
        pause
        exit /b
    )
    echo. > installed.flag
)

:: Start Web Server
echo.
echo ========================================================
echo   GitHub Tech Radar is running!
echo   Open your browser at: http://localhost:5001
echo ========================================================
echo.

python src\web_server.py

pause
