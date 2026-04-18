@echo off
setlocal
cd /d %~dp0

echo Launching FocusFlow backend...
start "FocusFlow Backend" cmd /k "cd /d "%~dp0backend" && if not exist .venv python -m venv .venv && .\.venv\Scripts\python -m pip install -r requirements.txt && .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Launching FocusFlow frontend...
start "FocusFlow Frontend" cmd /k "cd /d "%~dp0frontend" && if not exist node_modules npm install && npm run dev"

echo Launching FocusFlow Electron wrapper...
start "FocusFlow Electron" cmd /k "cd /d "%~dp0electron" && if not exist node_modules npm install && npm start"

echo FocusFlow startup commands issued.
pause
