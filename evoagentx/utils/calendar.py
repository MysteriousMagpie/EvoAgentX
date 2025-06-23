import os
import requests
import datetime
from typing import Any, Dict, List
from ..core.logging import logger


def _base_url() -> str:
    return os.getenv("CALENDAR_API_URL", "http://127.0.0.1:8000").rstrip("/")


def get_today_events() -> List[Dict[str, Any]]:
    """Return today's events from the calendar API."""
    url = f"{_base_url()}/events/"  # Use trailing slash to avoid redirect
    try:
        resp = requests.get(url, timeout=10)  # Increased timeout to 10 seconds
        resp.raise_for_status()
        events = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to fetch events: {e}")
        return []

    today = datetime.date.today().isoformat()
    return [e for e in events if str(e.get("start", "")).startswith(today)]


def add_event(title: str, start: str, end: str) -> Dict[str, Any]:
    """Add a calendar event via the API."""
    url = f"{_base_url()}/events"
    try:
        resp = requests.post(url, json={"title": title, "start": start, "end": end}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to add event: {e}")
        raise


def remove_event(event_id: str) -> None:
    """Remove an event by id."""
    url = f"{_base_url()}/events/{event_id}"
    try:
        resp = requests.delete(url, timeout=5)
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to remove event: {e}")
        raise


def update_event(event_id: str, title: str, start: str, end: str) -> Dict[str, Any]:
    """Update an existing calendar event."""
    url = f"{_base_url()}/events/{event_id}"
    try:
        resp = requests.put(url, json={"title": title, "start": start, "end": end}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to update event: {e}")
        raise
