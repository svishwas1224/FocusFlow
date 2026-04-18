from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class SessionBase(BaseModel):
    focus_score: float = Field(ge=0.0, le=100.0)

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    start: datetime
    end: Optional[datetime]

    class Config:
        orm_mode = True

class DistractionBase(BaseModel):
    app_name: str
    duration: float = Field(ge=0.0)

class DistractionCreate(DistractionBase):
    pass

class DistractionRead(DistractionBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class SettingBase(BaseModel):
    blocked_urls: List[str] = []
    aggressive_mode: bool = False

    @validator("blocked_urls", pre=True)
    def normalize_blocked_urls(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

class SettingRead(SettingBase):
    id: int

    class Config:
        orm_mode = True
