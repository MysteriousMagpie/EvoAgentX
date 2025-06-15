from fastapi import APIRouter, HTTPException

from server.models.schemas import Event, EventCreate
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
