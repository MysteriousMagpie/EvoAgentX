from fastapi import APIRouter, HTTPException
import subprocess
from datetime import datetime


from server.models.schemas import CalendarEvent, Event, EventCreate
from server.core.macos_calendar import create_calendar_event
from .calendar_store import calendar_store

calendar_router = APIRouter(prefix="/calendar")



def create_calendar_event(title: str, start: str, end: str, calendar_name: str = "Home") -> None:
    """Create a macOS Calendar event via AppleScript."""
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    start_str = start_dt.strftime("%A, %B %d, %Y at %I:%M %p")
    end_str = end_dt.strftime("%A, %B %d, %Y at %I:%M %p")
    script = (
        f'tell application "Calendar"\n'
        f'  tell calendar "{calendar_name}"\n'
        f'    make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"}}\n'
        f'  end tell\n'
        f'end tell'
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

def add_events(events: list[CalendarEvent]):
    """Add multiple events to the macOS Calendar."""

    for e in events:
        create_calendar_event(e.title, e.start, e.end, e.calendar_name)
    return {"added": len(events)}
