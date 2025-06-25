import pytest
import requests
from evoagentx.utils import calendar as cal

# use monkeypatch to patch requests.* methods to raise errors

def test_get_today_events_connection_error(monkeypatch):
    monkeypatch.setattr(cal.requests, "get", lambda *_, **__: (_ for _ in ()).throw(requests.exceptions.ConnectionError))
    assert cal.get_today_events() == []

def test_add_event_timeout(monkeypatch):
    monkeypatch.setattr(cal.requests, "post", lambda *_, **__: (_ for _ in ()).throw(requests.exceptions.ConnectTimeout))
    with pytest.raises(requests.exceptions.ConnectTimeout):
        cal.add_event("title", "start", "end")

def test_remove_event_conn_error(monkeypatch):
    monkeypatch.setattr(cal.requests, "delete", lambda *_, **__: (_ for _ in ()).throw(requests.exceptions.ConnectionError))
    with pytest.raises(requests.exceptions.ConnectionError):
        cal.remove_event("1")

def test_update_event_generic(monkeypatch):
    monkeypatch.setattr(cal.requests, "put", lambda *_, **__: (_ for _ in ()).throw(Exception("boom")))
    with pytest.raises(Exception):
        cal.update_event("1", "title", "start", "end")
