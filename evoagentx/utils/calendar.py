import os
import requests
from typing import Any, Dict, List
from ..core.logging import logger


def _base_url() -> str:
    return os.getenv("CALENDAR_API_URL", "http://localhost:8000").rstrip("/")


def get_today_events() -> List[Dict[str, Any]]:
    """Return today's events from the calendar API."""
    url = f"{_base_url()}/calendar/today"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Failed to fetch today's events: {e}")
        return []


def add_event(title: str, start: str, end: str) -> Dict[str, Any]:
    """Add a calendar event via the API."""
    url = f"{_base_url()}/calendar/event"
    try:
        resp = requests.post(url, json={"title": title, "start": start, "end": end}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Failed to add event: {e}")
        raise


def remove_event(event_id: int) -> None:
    """Remove an event by id."""
    url = f"{_base_url()}/calendar/event/{event_id}"
    try:
        resp = requests.delete(url, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to remove event: {e}")
        raise


def update_event(event_id: int, title: str, start: str, end: str) -> Dict[str, Any]:
    """Update an existing calendar event."""
    url = f"{_base_url()}/calendar/event/{event_id}"
    try:
        resp = requests.put(url, json={"title": title, "start": start, "end": end}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Failed to update event: {e}")
        raise
