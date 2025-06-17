from datetime import datetime
from pydantic import BaseModel


class RunRequest(BaseModel):
    goal: str


class RunResponse(BaseModel):
    goal: str
    output: str
    graph: dict | None = None


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
