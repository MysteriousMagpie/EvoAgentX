from datetime import datetime
from pydantic import BaseModel


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


class CalendarEvent(BaseModel):

    """Event information for adding to the macOS Calendar."""

    title: str
    start: datetime
    end: datetime
    calendar_name: str = "Home"
