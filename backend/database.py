from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from pathlib import Path

from .config import SQLITE_URL

engine = create_async_engine(SQLITE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    focus_score = Column(Float, default=0.0, nullable=False)
    deep_work = Column(Boolean, default=False, nullable=False)
    distraction_count = Column(Integer, default=0, nullable=False)


class AppLog(Base):
    __tablename__ = "app_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    app_name = Column(String, nullable=False)
    window_title = Column(String, nullable=True)
    category = Column(String, nullable=False)
    focus_score = Column(Float, default=0.0, nullable=False)
    duration_seconds = Column(Float, default=0.0, nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    blocked_apps = Column(String, default="", nullable=False)
    blocked_urls = Column(String, default="", nullable=False)
    aggressive_mode = Column(Boolean, default=False, nullable=False)
    pomodoro_enabled = Column(Boolean, default=True, nullable=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
