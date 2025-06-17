"""
Thin wrapper around `osascript` so the API layer can stay platform-agnostic.
If the host isn’t macOS, calls just raise NotImplementedError for now.
"""

from __future__ import annotations

import datetime as _dt
import platform
import subprocess
from typing import TypedDict


class CalendarEvent(TypedDict):
    title: str
    start: _dt.datetime  # naive → local time
    end: _dt.datetime
    notes: str | None
    calendar: str        # e.g. "Home", "Work"


def _run_applescript(script: str) -> str:
    """Execute an AppleScript snippet and return its stdout."""

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr or exc.stdout) from exc

    return result.stdout.strip()


def _assert_macos() -> None:
    if platform.system() != "Darwin":
        raise NotImplementedError("macOS-only calendar integration")


# ────────────────────────────────────────────────────────
# PUBLIC API
# ────────────────────────────────────────────────────────

def create_calendar_event(evt: CalendarEvent) -> str:
    """Drop an event into the user’s default Calendar collection.

    Returns the created event's UID.
    """

    _assert_macos()

    # AppleScript coercion requires a string in ISO 8601 *with seconds*
    start_iso = evt["start"].strftime("%Y-%m-%d %H:%M:%S")
    end_iso = evt["end"].strftime("%Y-%m-%d %H:%M:%S")
    notes = evt["notes"] or ""

    # AppleScript block (we escape quotes ↓)
    script = f'''
    set calName to "{evt["calendar"]}"
    set theSummary to "{evt["title"]}"
    set theDescription to "{notes}"
    set theStartDate to date "{start_iso}"
    set theEndDate to date "{end_iso}"

    tell application "Calendar"
        if (calendars whose name is calName) is {{}} then
            make new calendar with properties {{name:calName}}
        end if
        set targetCal to calendar calName
        set newEvent to make new event at end of events of targetCal with properties ¬
            {{summary:theSummary, description:theDescription, start date:theStartDate, end date:theEndDate}}
        return uid of newEvent
    end tell
    '''
    return _run_applescript(script)


def update_calendar_event(event_uid: str, evt: CalendarEvent) -> None:  # noqa: D401
    """Update an existing event identified by ``event_uid``."""

    _assert_macos()

    start_iso = evt["start"].strftime("%Y-%m-%d %H:%M:%S")
    end_iso = evt["end"].strftime("%Y-%m-%d %H:%M:%S")
    notes = evt["notes"] or ""

    script = f'''
    set eventId to "{event_uid}"
    set theSummary to "{evt["title"]}"
    set theDescription to "{notes}"
    set theStartDate to date "{start_iso}"
    set theEndDate to date "{end_iso}"

    tell application "Calendar"
        set targetEvent to first event of calendars whose uid is eventId
        set summary of targetEvent to theSummary
        set description of targetEvent to theDescription
        set start date of targetEvent to theStartDate
        set end date of targetEvent to theEndDate
    end tell
    '''
    _run_applescript(script)


def delete_calendar_event(event_uid: str) -> None:  # noqa: D401
    """Remove an event by its Calendar UID."""

    _assert_macos()

    script = f'''
    tell application "Calendar"
        delete (every event of calendars whose uid is "{event_uid}")
    end tell
    '''
    _run_applescript(script)


def list_calendar_events(from_: _dt.datetime, to_: _dt.datetime) -> list[dict]:
    """Return events in range (optional future use)."""
    raise NotImplementedError
