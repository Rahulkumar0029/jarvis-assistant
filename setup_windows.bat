@echo off
REM One-time setup for Jarvis on Windows. Double-click this file.
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
  set "PY_CMD=py -3.12"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PY_CMD=python"
  ) else (
    echo Python is not installed. Install Python 3.11 or 3.12 from python.org
    echo and tick "Add python.exe to PATH" in the installer. Then run this again.
    pause
    exit /b 1
  )
)

echo [1/4] Creating virtual environment...
%PY_CMD% -m venv venv 2>nul
if errorlevel 1 (
  python -m venv venv
  if errorlevel 1 ( echo Failed to create venv & pause & exit /b 1 )
)

echo [2/4] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip

echo [3/4] Installing packages (this takes a minute)...
venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
  echo Retrying PyAudio installation with binary options...
  venv\Scripts\pip.exe install pipwin
  venv\Scripts\pipwin.exe install pyaudio
  venv\Scripts\pip.exe install PyAudio --only-binary :all:
)

echo [4/4] Creating .env file...
if not exist .env copy .env.example .env >nul

echo.
echo Setup complete! Next: run run_jarvis.bat (or run_text_mode.bat to test without a mic)
pause
