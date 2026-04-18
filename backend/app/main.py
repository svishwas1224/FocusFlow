from datetime import datetime
from typing import List
import asyncio

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .database import init_db, get_session
from .blocker import block_sites, unblock_sites
from .monitor import scan_active_window, categorize_window, list_process_names

app = FastAPI(title="FocusFlow API", version="0.1.0")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/sessions", response_model=schemas.SessionRead)
async def create_session(session_in: schemas.SessionCreate, db: AsyncSession = Depends(get_session)):
    record = await crud.create_session_record(db, session_in)
    asyncio.create_task(_activate_blocking())
    return record

@app.put("/sessions/{session_id}/close", response_model=schemas.SessionRead)
async def close_session(session_id: int, session_in: schemas.SessionCreate, db: AsyncSession = Depends(get_session)):
    record = await crud.get_session(db, session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Session not found")
    closed = await crud.close_session_record(db, session_id, datetime.utcnow(), session_in.focus_score)
    unblock_sites()
    return closed

@app.get("/sessions", response_model=List[schemas.SessionRead])
async def read_sessions(limit: int = 50, db: AsyncSession = Depends(get_session)):
    return await crud.list_sessions(db, limit)

@app.post("/distractions", response_model=schemas.DistractionRead)
async def log_distraction(distraction_in: schemas.DistractionCreate, db: AsyncSession = Depends(get_session)):
    return await crud.create_distraction(db, distraction_in)

@app.get("/distractions", response_model=List[schemas.DistractionRead])
async def read_distractions(limit: int = 100, db: AsyncSession = Depends(get_session)):
    return await crud.list_distractions(db, limit)

@app.get("/settings", response_model=schemas.SettingRead)
async def read_settings(db: AsyncSession = Depends(get_session)):
    setting = await crud.get_setting(db)
    if not setting:
        setting = await crud.upsert_setting(db, schemas.SettingBase())
    return setting

@app.post("/settings", response_model=schemas.SettingRead)
async def update_settings(setting_in: schemas.SettingBase, db: AsyncSession = Depends(get_session)):
    setting = await crud.upsert_setting(db, setting_in)
    return setting

@app.get("/monitor/active-window")
async def active_window():
    title = scan_active_window()
    return {"title": title, "category": categorize_window(title)}

@app.get("/monitor/processes")
async def processes():
    return {"running": list_process_names()}

async def _activate_blocking():
    await asyncio.to_thread(block_sites)
