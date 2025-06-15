from fastapi import APIRouter, HTTPException

from server.models.schemas import CalendarEvent, Event, EventCreate
from server.core.macos_calendar import create_calendar_event
from .calendar_store import calendar_store

calendar_router = APIRouter(prefix="/calendar")

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
