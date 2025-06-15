from __future__ import annotations

import json
from pathlib import Path
from datetime import date, datetime
from typing import List

from server.models.schemas import Event, EventCreate

class CalendarStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self._events: List[Event] = []
        self._next_id = 1
        if self.path and self.path.exists():
            self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text())
            self._events = [Event(**e) for e in data.get("events", [])]
            if self._events:
                self._next_id = max(e.id for e in self._events) + 1
        except Exception:
            self._events = []
            self._next_id = 1

    def _save(self) -> None:
        if not self.path:
            return
        self.path.write_text(
            json.dumps({"events": [e.dict() for e in self._events]}, indent=2)
        )

    def list_today(self) -> List[Event]:
        today = date.today()
        results = []
        for e in self._events:
            try:
                event_date = datetime.fromisoformat(e.start).date()
            except Exception:
                continue
            if event_date == today:
                results.append(e)
        return results

    def add(self, event: EventCreate) -> Event:
        new = Event(id=self._next_id, **event.dict())
        self._events.append(new)
        self._next_id += 1
        self._save()
        return new

    def update(self, event_id: int, event: EventCreate) -> Event:
        for e in self._events:
            if e.id == event_id:
                e.title = event.title
                e.start = event.start
                e.end = event.end
                self._save()
                return e
        raise KeyError("Event not found")

    def delete(self, event_id: int) -> None:
        for i, e in enumerate(self._events):
            if e.id == event_id:
                self._events.pop(i)
                self._save()
                return
        raise KeyError("Event not found")

calendar_store = CalendarStore()
