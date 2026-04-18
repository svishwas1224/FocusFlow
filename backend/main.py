import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from . import analytics, config, database, schemas, monitor

app = FastAPI(title="FocusFlow AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class TimerState:
    mode: Optional[str] = None
    started_at: Optional[datetime] = None
    duration_seconds: int = 0
    is_running: bool = False
    session_id: Optional[int] = None


timer_state = TimerState()


async def get_db() -> AsyncSession:
    async for session in database.get_session():
        yield session


async def passive_logger():
    while True:
        await asyncio.sleep(60)
        async for session in database.get_session():
            current_score = float(monitor.monitor.state.focus_score)
            stmt = database.Session(
                focus_score=current_score,
                deep_work=current_score >= 50,
                distraction_count=0,
                start=datetime.now() - timedelta(minutes=1),
                end=datetime.now()
            )
            session.add(stmt)
            await session.commit()
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    monitor.monitor.start()
    task = asyncio.create_task(passive_logger())
    yield
    task.cancel()
    monitor.monitor.stop()


app.router.lifespan_context = lifespan


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions/start", response_model=schemas.SessionRead)
async def start_session(session_in: schemas.SessionCreate, db: AsyncSession = Depends(get_db)):
    stmt = database.Session(
        focus_score=session_in.focus_score,
        deep_work=session_in.focus_score >= 80,
        distraction_count=0,
    )
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    asyncio.create_task(_ensure_blocking())
    return stmt


@app.put("/sessions/{session_id}/close", response_model=schemas.SessionRead)
async def close_session(session_id: int, session_in: schemas.SessionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(database.Session).where(database.Session.id == session_id))
    session_record = result.scalars().first()
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.execute(
        update(database.Session)
        .where(database.Session.id == session_id)
        .values(end=datetime.now(), focus_score=session_in.focus_score)
    )
    await db.commit()
    await db.refresh(session_record)
    monitor.monitor.unblock_sites()
    return session_record


@app.get("/sessions", response_model=List[schemas.SessionRead])
async def list_sessions(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(database.Session).order_by(database.Session.start.desc()).limit(limit))
    return result.scalars().all()


@app.get("/monitor/state", response_model=schemas.FocusState)
def get_monitor_state() -> schemas.FocusState:
    return schemas.FocusState(
        title=monitor.monitor.state.title,
        category=monitor.monitor.state.category,
        focus_score=monitor.monitor.state.focus_score,
        activity_rate=monitor.monitor.state.activity_rate,
        forbidden=monitor.monitor.state.forbidden,
        intervention_required=monitor.monitor.state.intervention_required,
    )


@app.get("/monitor/processes")
def get_processes() -> Dict[str, List[str]]:
    return {"running": monitor.monitor.list_process_names()}


@app.post("/blocker/activate")
def activate_blocker(extra_urls: Optional[List[str]] = None) -> Dict[str, Any]:
    success = monitor.monitor.block_sites(extra_urls)
    return {
        "activated": success,
        "message": "Blocker enabled" if success else "Permission denied or hosts file unavailable",
    }


@app.post("/blocker/deactivate")
def deactivate_blocker() -> Dict[str, Any]:
    success = monitor.monitor.unblock_sites()
    return {"deactivated": success, "message": "Blocker disabled" if success else "Could not clean hosts entries"}


@app.get("/reports/pie")
async def get_pie_report(db: AsyncSession = Depends(get_db)) -> List[schemas.PieSegment]:
    result = await db.execute(select(database.Session))
    sessions = result.scalars().all()
    deep_work = sum(1 for item in sessions if item.deep_work)
    distraction = sum(1 for item in sessions if not item.deep_work)
    return [
        schemas.PieSegment(name="Deep Work", value=deep_work),
        schemas.PieSegment(name="Distraction", value=distraction),
    ]


@app.get("/reports/focus-line")
async def get_focus_line(db: AsyncSession = Depends(get_db)) -> List[schemas.ReportPoint]:
    result = await db.execute(select(database.Session).order_by(database.Session.start.asc()).limit(48))
    sessions = result.scalars().all()
    return [
        schemas.ReportPoint(label=item.start.isoformat(), value=item.focus_score)
        for item in sessions
    ]


@app.get("/settings", response_model=schemas.SettingRead)
async def get_settings(db: AsyncSession = Depends(get_db)) -> schemas.SettingRead:
    result = await db.execute(select(database.Setting).limit(1))
    setting = result.scalars().first()
    if not setting:
        setting = database.Setting()
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
    return schemas.SettingRead(
        id=setting.id,
        blocked_apps=setting.blocked_apps.split(",") if setting.blocked_apps else [],
        blocked_urls=setting.blocked_urls.split(",") if setting.blocked_urls else [],
        aggressive_mode=setting.aggressive_mode,
        pomodoro_enabled=setting.pomodoro_enabled,
    )


@app.post("/settings", response_model=schemas.SettingRead)
async def update_settings(setting_in: schemas.SettingBase, db: AsyncSession = Depends(get_db)) -> schemas.SettingRead:
    result = await db.execute(select(database.Setting).limit(1))
    setting = result.scalars().first()
    if not setting:
        setting = database.Setting()
        db.add(setting)
    setting.blocked_apps = ",".join(setting_in.blocked_apps)
    setting.blocked_urls = ",".join(setting_in.blocked_urls)
    setting.aggressive_mode = setting_in.aggressive_mode
    setting.pomodoro_enabled = setting_in.pomodoro_enabled
    await db.commit()
    await db.refresh(setting)
    return schemas.SettingRead(
        id=setting.id,
        blocked_apps=setting_in.blocked_apps,
        blocked_urls=setting_in.blocked_urls,
        aggressive_mode=setting.aggressive_mode,
        pomodoro_enabled=setting.pomodoro_enabled,
    )


@app.post("/timer/start")
async def start_timer(command: schemas.TimerCommand, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    mode = command.mode
    if mode not in config.POMODORO_SETTINGS:
        raise HTTPException(status_code=400, detail="Invalid timer mode")
    timer_state.mode = mode
    timer_state.started_at = datetime.now()
    timer_state.duration_seconds = config.POMODORO_SETTINGS[mode]
    timer_state.is_running = True
    monitor.monitor.block_sites()
    
    # Record to DB
    current_score = float(monitor.monitor.state.focus_score)
    stmt = database.Session(
        focus_score=current_score,
        deep_work=current_score >= 80,
        distraction_count=0,
    )
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    timer_state.session_id = stmt.id

    return {"mode": mode, "duration": timer_state.duration_seconds, "running": True}


@app.post("/timer/stop")
async def stop_timer(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    if timer_state.session_id:
        result = await db.execute(select(database.Session).where(database.Session.id == timer_state.session_id))
        session_record = result.scalars().first()
        if session_record:
            current_score = float(monitor.monitor.state.focus_score)
            await db.execute(
                update(database.Session)
                .where(database.Session.id == timer_state.session_id)
                .values(end=datetime.now(), focus_score=current_score, deep_work=current_score >= 50)
            )
            await db.commit()

    timer_state.mode = None
    timer_state.started_at = None
    timer_state.duration_seconds = 0
    timer_state.is_running = False
    timer_state.session_id = None
    monitor.monitor.unblock_sites()
    return {"running": False}


@app.get("/timer/state")
def read_timer_state() -> Dict[str, Any]:
    return {
        "mode": timer_state.mode,
        "started_at": timer_state.started_at.isoformat() if timer_state.started_at else None,
        "duration": timer_state.duration_seconds,
        "running": timer_state.is_running,
    }


@app.post("/intervention/acknowledge")
def acknowledge_intervention() -> Dict[str, str]:
    monitor.monitor._low_score_start = None
    return {"message": "Intervention acknowledged"}


async def _ensure_blocking() -> None:
    await asyncio.to_thread(monitor.monitor.block_sites)
