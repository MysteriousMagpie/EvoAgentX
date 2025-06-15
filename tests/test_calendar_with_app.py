import datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

# ---- create a minimal clone of the production API ----
app = FastAPI()
EVENTS = {}

@app.get("/events")
def list_events():
    return list(EVENTS.values())

@app.post("/events")
def create_event(payload: dict):
    _id = str(len(EVENTS) + 1)
    EVENTS[_id] = {"id": _id, **payload}
    return EVENTS[_id]

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    if event_id not in EVENTS:
        raise HTTPException(404)
    EVENTS.pop(event_id)
    return {}

@app.put("/events/{event_id}")
def update_event(event_id: str, payload: dict):
    if event_id not in EVENTS:
        raise HTTPException(404)
    EVENTS[event_id].update(payload)
    return EVENTS[event_id]

# ---- the real unit-test --------------------------------
from evoagentx.utils import calendar as cal_utils  # noqa: E402

@pytest.fixture(autouse=True)
def _wire_requests_to_app(monkeypatch):
    """Replace HTTP calls with in-process FastAPI TestClient."""
    client = TestClient(app)
    for verb in ("get", "post", "delete", "put"):
        monkeypatch.setattr(cal_utils.requests, verb, getattr(client, verb))
    monkeypatch.setattr(cal_utils, "_base_url", lambda: "http://testserver")
    yield
    EVENTS.clear()

def test_calendar_roundtrip():
    today = datetime.date.today().isoformat()
    created = cal_utils.add_event("Meeting", today, today)
    assert created["title"] == "Meeting"
    events = cal_utils.get_today_events()
    assert len(events) == 1 and events[0]["title"] == "Meeting"
    updated = cal_utils.update_event(created["id"], "Party", today, today)
    assert updated["title"] == "Party"
    cal_utils.remove_event(created["id"])
    assert cal_utils.get_today_events() == []
