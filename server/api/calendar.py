from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from server.core.macos_calendar import create_calendar_event, CalendarEvent
import datetime as dt
import uuid

calendar_router = APIRouter(prefix="/events", tags=["calendar"])

# in-memory store for now
_EVENT_DB: dict[str, CalendarEvent] = {}


class EventIn(BaseModel):
    title: str
    start: dt.datetime = Field(..., example="2025-06-16T14:00:00")
    end: dt.datetime = Field(..., example="2025-06-16T16:00:00")
    notes: str | None = None
    calendar: str = "Home"


class EventOut(EventIn):
    id: str


@calendar_router.post("/", response_model=EventOut, status_code=201)
def add_event(evt: EventIn):
    try:
        create_calendar_event(evt.model_dump())   # push to macOS
    except NotImplementedError:
        pass  # running on non-mac dev box → just store
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"Calendar error: {exc}") from exc

    evt_id = str(uuid.uuid4())
    _EVENT_DB[evt_id] = evt.model_dump()
    return EventOut(id=evt_id, **evt.model_dump())


@calendar_router.get("/", response_model=list[EventOut])
def list_events():
    return [EventOut(id=k, **v) for k, v in _EVENT_DB.items()]


@calendar_router.put("/{evt_id}", response_model=EventOut)
def update_event(evt_id: str, evt: EventIn):
    if evt_id not in _EVENT_DB:
        raise HTTPException(404, "Not found")
    _EVENT_DB[evt_id] = evt.model_dump()
    # TODO: update macOS event when helper ready
    return EventOut(id=evt_id, **evt.model_dump())


@calendar_router.delete("/{evt_id}", status_code=204)
def delete_event(evt_id: str):
    if evt_id not in _EVENT_DB:
        raise HTTPException(404, "Not found")
    # TODO: also remove from macOS by UID when helper ready
    _EVENT_DB.pop(evt_id)
