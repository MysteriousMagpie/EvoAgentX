from fastapi import APIRouter, HTTPException
from server.models.schemas import Event, EventCreate

router = APIRouter()

_events: list[Event] = []
_next_id = 1

@router.get("/events", response_model=list[Event])
def list_events():
    return _events

@router.post("/events", response_model=Event)
def add_event(event: EventCreate):
    global _next_id
    new = Event(id=_next_id, **event.dict())
    _events.append(new)
    _next_id += 1
    return new

@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventCreate):
    for e in _events:
        if e.id == event_id:
            e.title = event.title
            e.start = event.start
            e.end = event.end
            return e
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/events/{event_id}")
def delete_event(event_id: int):
    for i, e in enumerate(_events):
        if e.id == event_id:
            _events.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Event not found")
