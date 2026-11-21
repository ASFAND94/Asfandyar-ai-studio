@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.11 or newer is required. Install it from https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating local Python environment...
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)

echo Installing project requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

".venv\Scripts\python.exe" setup_local.py
if errorlevel 1 goto failed

echo.
echo Opening Asfandyar AI Studio at http://127.0.0.1:8000/app/
echo Keep this window open while using the application.
echo Press CTRL+C to stop the server.
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
goto end

:failed
echo.
echo Setup failed. Check the error above and confirm Python and internet access.
pause
exit /b 1

:end
endlocal
