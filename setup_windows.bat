@echo off
REM One-time setup for Jarvis on Windows. Double-click this file.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. Install Python 3.11 or 3.12 from python.org
  echo and tick "Add python.exe to PATH" in the installer. Then run this again.
  pause
  exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 ( echo Failed to create venv & pause & exit /b 1 )

echo [2/4] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/4] Installing packages (this takes a minute)...
pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Some package failed. If it was PyAudio, see the Troubleshooting section in README.md
  pause
  exit /b 1
)

echo [4/4] Creating .env file...
if not exist .env copy .env.example .env >nul

echo.
echo Setup complete!  Next: run  run_jarvis.bat   (or run_text_mode.bat to test without a mic)
pause
