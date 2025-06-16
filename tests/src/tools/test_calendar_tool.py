import datetime
import pytest

from evoagentx.tools.calendar import CalendarTool
from server.api.calendar_store import CalendarStore
from server.models.schemas import EventCreate
import server.api.calendar_store


@pytest.fixture
def temp_calendar_store(monkeypatch):
    store = CalendarStore()
    monkeypatch.setattr(server.api.calendar_store, "calendar_store", store)
    return store


@pytest.fixture
def calendar_tool():
    return CalendarTool()


def test_get_today_returns_todays_events(temp_calendar_store, calendar_tool):
    today = datetime.date.today()
    temp_calendar_store.add(EventCreate(title="today", start=f"{today.isoformat()}T09:00:00", end=f"{today.isoformat()}T10:00:00"))
    tomorrow = today + datetime.timedelta(days=1)
    temp_calendar_store.add(EventCreate(title="tomorrow", start=f"{tomorrow.isoformat()}T09:00:00", end=f"{tomorrow.isoformat()}T10:00:00"))
    result = calendar_tool.get_today()
    assert len(result) == 1
    assert result[0]["title"] == "today"


def test_add_event_adds_to_store(temp_calendar_store, calendar_tool):
    today = datetime.date.today()
    event = calendar_tool.add_event("meeting", f"{today.isoformat()}T09:00:00", f"{today.isoformat()}T10:00:00")
    assert len(temp_calendar_store._events) == 1
    assert temp_calendar_store._events[0].title == "meeting"
    assert event["id"] == temp_calendar_store._events[0].id


def test_remove_event_removes_from_store(temp_calendar_store, calendar_tool):
    today = datetime.date.today()
    event = temp_calendar_store.add(EventCreate(title="obsolete", start=f"{today.isoformat()}T09:00:00", end=f"{today.isoformat()}T10:00:00"))
    result = calendar_tool.remove_event(event.id)
    assert result == {"deleted": event.id}
    assert len(temp_calendar_store._events) == 0


def test_update_event_updates_store(temp_calendar_store, calendar_tool):
    today = datetime.date.today()
    event = temp_calendar_store.add(EventCreate(title="old", start=f"{today.isoformat()}T09:00:00", end=f"{today.isoformat()}T10:00:00"))
    new_start = f"{today.isoformat()}T11:00:00"
    update = calendar_tool.update_event(event.id, "new", new_start, f"{today.isoformat()}T12:00:00")
    assert temp_calendar_store._events[0].title == "new"
    assert temp_calendar_store._events[0].start == new_start
    assert update["title"] == "new"
