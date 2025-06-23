from typing import Any, Callable, Dict, List
from .tool import Tool
from ..utils.calendar import get_today_events, add_event, remove_event, update_event
from ..core.logging import logger


class CalendarTool(Tool):
    """Tool providing calendar operations."""

    def __init__(self, name: str = "calendar", **kwargs):
        super().__init__(name=name, **kwargs)

    def get_today(self) -> List[Dict[str, Any]]:
        try:
            return get_today_events()
        except Exception as e:
            logger.warning(f"Calendar service unavailable: {e}")
            return []

    def add_event(self, title: str, start: str, end: str) -> Dict[str, Any]:
        try:
            return add_event(title, start, end)
        except Exception as e:
            logger.error(f"Failed to add calendar event: {e}")
            return {"error": "Calendar service unavailable", "success": False}

    def remove_event(self, event_id: int) -> Dict[str, Any]:
        try:
            remove_event(str(event_id))
            return {"ok": True}
        except Exception as e:
            logger.error(f"Failed to remove calendar event: {e}")
            return {"error": "Calendar service unavailable", "success": False}

    def update_event(self, event_id: int, title: str, start: str, end: str) -> Dict[str, Any]:
        try:
            return update_event(str(event_id), title, start, end)
        except Exception as e:
            logger.error(f"Failed to update calendar event: {e}")
            return {"error": "Calendar service unavailable", "success": False}


    def get_tools(self) -> List[Callable]:
        return [self.get_today, self.add_event, self.remove_event, self.update_event]

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_today",
                    "description": "Get today's calendar events",

                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_event",
                    "description": "Add a calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Event title"},
                            "start": {"type": "string", "description": "Start time ISO"},
                            "end": {"type": "string", "description": "End time ISO"},
                        },
                        "required": ["title", "start", "end"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_event",
                    "description": "Remove a calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "integer", "description": "Event identifier"}
                        },

                        "required": ["event_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_event",
                    "description": "Update a calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_id": {"type": "integer", "description": "Event identifier"},
                            "title": {"type": "string", "description": "Event title"},
                            "start": {"type": "string", "description": "Start time ISO"},
                            "end": {"type": "string", "description": "End time ISO"},

                        },
                        "required": ["event_id", "title", "start", "end"],
                    },
                },
            },
        ]

    def get_tool_descriptions(self) -> List[str]:
        return [
            "Get today's calendar events",
            "Add a calendar event",
            "Remove a calendar event",
            "Update a calendar event",
        ]

