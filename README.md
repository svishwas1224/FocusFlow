# FocusFlow

FocusFlow is a desktop productivity application that combines:

- a Python-powered monitoring backend for focus scoring, distraction detection, and application blocking
- a React + Tailwind dashboard for real-time productivity insights
- an Electron wrapper for desktop deployment and tray integration

## Project structure

- `backend/` — FastAPI service, async SQLite persistence, process and window monitoring, session tracking, settings, and reporting.
- `frontend/` — React + TypeScript UI with Tailwind styling and chart visualization.
- `electron/` — Electron desktop shell, system tray menu, backend sidecar process launcher, and IPC bridge.

## Local setup

This project can be run in three parts: backend, frontend, and Electron.

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend exposes APIs at `http://127.0.0.1:8000`.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the app at `http://127.0.0.1:5173/`.

### 3. Electron

```powershell
cd electron
npm install
npm start
```

The Electron shell launches the desktop app with tray integration and backend management.

## Full stack run order

1. Start the backend.
2. Start the frontend.
3. Start Electron.

## Testing

Run backend tests from the `backend/` folder:

```powershell
cd backend
pytest
```

## Notes

- If Tailwind styles are not applying, ensure the frontend build is up-to-date and the `tailwind.config.js` content paths include `.tsx`.
- The backend uses SQLite for local persistence under `backend/`.
- The Electron layer expects the frontend to be served locally or built into the app package.

## GitHub repository

This project is intended to be version-controlled and published under the GitHub account `svishwas1224`.

If this folder is not already a Git repository, initialize it with:

```powershell
git init
git add .
git commit -m "Initial FocusFlow project commit"
```

Then add the remote repository and push:

```powershell
git remote add origin https://github.com/svishwas1224/FocusFlow.git
git push -u origin main
```
