from fastapi import APIRouter, HTTPException

from server.models.schemas import Event, EventCreate, CalendarEvent
from datetime import datetime
import subprocess
from .calendar_store import calendar_store

calendar_router = APIRouter(prefix="/calendar")


def create_calendar_event(title: str, start: datetime, end: datetime, calendar_name: str = "Home") -> None:
    """Create a macOS Calendar event via AppleScript."""
    start_str = start.strftime("%A, %B %d, %Y at %I:%M %p")
    end_str = end.strftime("%A, %B %d, %Y at %I:%M %p")
    script = (
        'tell application "Calendar"\n'
        f'  tell calendar "{calendar_name}"\n'
        f'    make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"}}\n'
        '  end tell\n'
        'end tell'
    )
    subprocess.run(["osascript", "-e", script], check=True)

@calendar_router.get("/today", response_model=list[Event])
def get_today():
    return calendar_store.list_today()

@calendar_router.post("/event", response_model=Event)
def create_event(event: EventCreate):
    return calendar_store.add(event)

@calendar_router.put("/event/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventCreate):
    try:
        return calendar_store.update(event_id, event)
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")

@calendar_router.delete("/event/{event_id}")
def delete_event(event_id: int):
    try:
        calendar_store.delete(event_id)
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")


@calendar_router.post("/add-events")
def add_calendar_events(events: list[CalendarEvent]):
    """Add multiple events to macOS Calendar."""
    for event in events:
        create_calendar_event(event.title, event.start, event.end, event.calendar_name)
    return {"added": len(events)}
