# tests/test_utils_extra.py
import sys, types, datetime, pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import cast

# ------------------------------------------------------------------
#  Inject a minimal fake storages.storages_config  ❱ breaks the cycle
# ------------------------------------------------------------------
stub_cfg = types.ModuleType("evoagentx.storages.storages_config")
class _DummyCfg:        # just needs a model_dump method for factory.create
    def model_dump(self): return {}

stub_cfg.__dict__["DBConfig"] = _DummyCfg
stub_cfg.__dict__["VectorStoreConfig"] = _DummyCfg

# also make sure the parent package exists in sys.modules
sys.modules.setdefault("evoagentx.storages", types.ModuleType("evoagentx.storages"))
sys.modules["evoagentx.storages.storages_config"] = stub_cfg

# NOW it’s safe to import factory
from evoagentx.utils import factory
from evoagentx.utils import calendar as cal

# ------------------------------------------------------------------
#  FastAPI test-double for calendar utils (same as before)
# ------------------------------------------------------------------
app = FastAPI()
EVENTS = {}
@app.get("/events")           # happy-path
def list_events(): return list(EVENTS.values())
client = TestClient(app)

@pytest.fixture(autouse=True)
def _wire(monkeypatch):
    for verb in ("get", "post", "delete", "put"):
        monkeypatch.setattr(cal.requests, verb, getattr(client, verb))
    monkeypatch.setattr(cal, "_base_url", lambda: "http://testserver")
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
def test_factory_db_unsupported():
    with pytest.raises(ValueError):
        factory.DBStoreFactory.create("unknown", cast(factory.DBConfig, _DummyCfg()))
        factory.DBStoreFactory.create("unknown", cast(factory.DBConfig, _DummyCfg()))
