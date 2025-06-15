from pydantic import BaseModel
from datetime import datetime


class RunRequest(BaseModel):
    goal: str


class RunResponse(BaseModel):
    goal: str
    output: str


class EventBase(BaseModel):
    title: str
    start: str
    end: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int


class MacCalendarEvent(BaseModel):
    """Schema for creating macOS Calendar events."""

    title: str
    start: datetime
    end: datetime
    calendar_name: str = "Home"
