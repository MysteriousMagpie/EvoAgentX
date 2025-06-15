from typing import List, Callable, Dict, Any
from pydantic import Field

from .tool import Tool
from server.models.schemas import EventCreate

def _store():
    from server.api.calendar_store import calendar_store
    return calendar_store

class CalendarTool(Tool):
    """Simple tool for interacting with the built-in calendar store."""

    name: str = "calendar"

    def get_today(self) -> List[dict]:
        """Return today's events as a list of dictionaries."""
        store = _store()
        return [e.dict() for e in store.list_today()]

    def add_event(self, title: str, start: str, end: str) -> dict:
        """Add an event to the calendar."""
        store = _store()
        event = EventCreate(title=title, start=start, end=end)
        return store.add(event).dict()

    def remove_event(self, event_id: int) -> dict:
        """Remove an event from the calendar."""
        store = _store()
        store.delete(event_id)
        return {"deleted": event_id}

    def update_event(self, event_id: int, title: str, start: str, end: str) -> dict:
        """Update an existing calendar event."""
        store = _store()
        event = EventCreate(title=title, start=start, end=end)
        return store.update(event_id, event).dict()

    def get_tools(self) -> List[Callable]:
        return [self.get_today, self.add_event, self.remove_event, self.update_event]

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_today",
                    "description": "Return today's calendar events.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_event",
                    "description": "Add a calendar event.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                        "required": ["title", "start", "end"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_event",
                    "description": "Remove a calendar event by id.",
                    "parameters": {
                        "type": "object",
                        "properties": {"event_id": {"type": "integer"}},
                        "required": ["event_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_event",
                    "description": "Update an existing calendar event.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "integer"},
                            "title": {"type": "string"},
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                        "required": ["event_id", "title", "start", "end"],
                    },
                },
            },
        ]

    def get_tool_descriptions(self) -> List[str]:
        return ["Calendar management tool providing today's events and update operations."]
