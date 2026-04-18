from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    focus_score: float = Field(ge=0.0, le=100.0)


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    id: int
    start: datetime
    end: Optional[datetime]
    deep_work: bool
    distraction_count: int

    model_config = ConfigDict(from_attributes=True)


class AppLogBase(BaseModel):
    app_name: str
    window_title: Optional[str] = None
    category: str
    focus_score: float = Field(ge=0.0, le=100.0)
    duration_seconds: float = Field(ge=0.0)


class AppLogRead(AppLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class SettingBase(BaseModel):
    blocked_apps: List[str] = []
    blocked_urls: List[str] = []
    aggressive_mode: bool = False
    pomodoro_enabled: bool = True


class SettingRead(SettingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class FocusState(BaseModel):
    title: str
    category: str
    focus_score: int
    activity_rate: float
    forbidden: bool
    intervention_required: bool


class TimerCommand(BaseModel):
    mode: str


class ReportPoint(BaseModel):
    label: str
    value: float


class PieSegment(BaseModel):
    name: str
    value: int
