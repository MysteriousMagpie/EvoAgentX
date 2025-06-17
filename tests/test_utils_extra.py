# tests/test_utils_extra.py
import datetime
import warnings
import pytest
from evoagentx.storages.storages_config import (
    DBConfig,
    VectorStoreConfig,
    GraphStoreConfig,
)
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from evoagentx.utils import factory
from evoagentx.utils import calendar as cal
warnings.filterwarnings("ignore", "`timeout`", DeprecationWarning)

# ------------------------------------------------------------------
#  FastAPI test-double for calendar utils (same as before)
# ------------------------------------------------------------------
app = FastAPI()
EVENTS = {}
@app.get("/events")           # happy-path
def list_events(): return list(EVENTS.values())
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
client = TestClient(app)

@pytest.fixture(autouse=True)
def _wire(monkeypatch):
    for verb in ("get", "post", "delete", "put"):
        monkeypatch.setattr(cal.requests, verb, getattr(client, verb))
    original_base_url = cal._base_url
    monkeypatch.setattr(cal, "_base_url", lambda: "http://testserver")
    original_base_url()
    yield
    EVENTS.clear()

def test_calendar_roundtrip():
    today = datetime.date.today().isoformat()
    created = cal.add_event("Meet", today, today)
    assert created["title"] == "Meet"
    assert len(cal.get_today_events()) == 1
    cal.remove_event(created["id"])
    assert cal.get_today_events() == []

def test_factory_load_success():
    assert factory.load_class("datetime.datetime") is datetime.datetime

def test_factory_load_failure():
    with pytest.raises((ImportError, AttributeError)):
        factory.load_class("nope.Nope")

def test_calendar_error_handling(monkeypatch):
    monkeypatch.setattr(cal.requests, "get", lambda *_, **__: (_ for _ in ()).throw(Exception("boom")))
    assert cal.get_today_events() == []

def test_factory_db_supported(monkeypatch):
    monkeypatch.setattr(factory, "load_class", lambda path: lambda **_: "db")
    cfg = DBConfig(db_name="sqlite", path=":memory:")
    got = factory.DBStoreFactory.create("sqlite", config=cfg)
    assert got == "db"

def test_factory_vector_and_graph():
    cfg = VectorStoreConfig()
    with pytest.raises(ValueError):
        factory.VectorStoreFactory.create(cfg)
    with pytest.raises(ValueError):
        factory.GraphStoreFactory.create(GraphStoreConfig())

def test_factory_graph_supported(monkeypatch):
    monkeypatch.setattr(factory, "load_class", lambda path: lambda **_: "graph")
    cfg = GraphStoreConfig(provider="neo4j")
    got = factory.GraphStoreFactory.create(cfg)
    assert got == "graph"

def test_factory_db_unsupported():
    with pytest.raises(ValueError):
        cfg = DBConfig(db_name="unknown")
        factory.DBStoreFactory.create("unknown", config=cfg)
