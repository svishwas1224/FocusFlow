@echo off
setlocal
cd /d "%~dp0"

echo Launching FocusFlow backend...
start "FocusFlow Backend" /D "%~dp0" cmd /k "(if not exist backend\.venv (python -m venv backend\.venv & backend\.venv\Scripts\python -m pip install -r backend\requirements.txt)) & set PYTHONPATH=%~dp0 & backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo Launching FocusFlow frontend...
start "FocusFlow Frontend" /D "%~dp0frontend" cmd /k "(if not exist node_modules npm install) & npm run dev -- --host 127.0.0.1 --port 5173"

echo Launching FocusFlow Electron wrapper...
start "FocusFlow Electron" /D "%~dp0electron" cmd /k "(if not exist node_modules npm install) & npm start"

echo FocusFlow startup commands issued.
pause
