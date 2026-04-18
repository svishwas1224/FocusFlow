from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

async def create_session_record(db: AsyncSession, session_in: schemas.SessionCreate) -> models.SessionRecord:
    record = models.SessionRecord(focus_score=session_in.focus_score)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

async def close_session_record(db: AsyncSession, session_id: int, end_time, focus_score: float) -> Optional[models.SessionRecord]:
    query = update(models.SessionRecord).where(models.SessionRecord.id == session_id).values(end=end_time, focus_score=focus_score)
    await db.execute(query)
    await db.commit()
    return await get_session(db, session_id)

async def get_session(db: AsyncSession, session_id: int) -> Optional[models.SessionRecord]:
    result = await db.execute(select(models.SessionRecord).where(models.SessionRecord.id == session_id))
    return result.scalars().first()

async def list_sessions(db: AsyncSession, limit: int = 50) -> List[models.SessionRecord]:
    result = await db.execute(select(models.SessionRecord).order_by(models.SessionRecord.start.desc()).limit(limit))
    return result.scalars().all()

async def create_distraction(db: AsyncSession, distraction_in: schemas.DistractionCreate) -> models.Distraction:
    distraction = models.Distraction(app_name=distraction_in.app_name, duration=distraction_in.duration)
    db.add(distraction)
    await db.commit()
    await db.refresh(distraction)
    return distraction

async def list_distractions(db: AsyncSession, limit: int = 100) -> List[models.Distraction]:
    result = await db.execute(select(models.Distraction).order_by(models.Distraction.timestamp.desc()).limit(limit))
    return result.scalars().all()

async def get_setting(db: AsyncSession) -> Optional[models.Setting]:
    result = await db.execute(select(models.Setting).limit(1))
    return result.scalars().first()

async def upsert_setting(db: AsyncSession, setting_in: schemas.SettingBase) -> models.Setting:
    existing = await get_setting(db)
    if existing:
        await db.execute(
            update(models.Setting)
            .where(models.Setting.id == existing.id)
            .values(blocked_urls=','.join(setting_in.blocked_urls), aggressive_mode=setting_in.aggressive_mode)
        )
        await db.commit()
        await db.refresh(existing)
        return existing
    setting = models.Setting(blocked_urls=','.join(setting_in.blocked_urls), aggressive_mode=setting_in.aggressive_mode)
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting
