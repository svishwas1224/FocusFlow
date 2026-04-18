from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from .database import Base

class SessionRecord(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    focus_score = Column(Float, default=0.0, nullable=False)

class Distraction(Base):
    __tablename__ = "distractions"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration = Column(Float, default=0.0, nullable=False)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    blocked_urls = Column(String, default="", nullable=False)
    aggressive_mode = Column(Boolean, default=False, nullable=False)
