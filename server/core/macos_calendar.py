from __future__ import annotations

from datetime import datetime
import subprocess


def create_calendar_event(
    title: str,
    start: datetime,
    end: datetime,
    calendar_name: str = "Home",
) -> None:
    """Create an event in macOS Calendar using AppleScript."""
    start_str = start.strftime("%A, %B %d, %Y at %I:%M %p")
    end_str = end.strftime("%A, %B %d, %Y at %I:%M %p")

    title_esc = title.replace("\"", "\\\"")
    cal_esc = calendar_name.replace("\"", "\\\"")

    script_lines = [
        'tell application "Calendar"',
        f'tell calendar "{cal_esc}"',
        f'make new event with properties {{summary:"{title_esc}", start date:date "{start_str}", end date:date "{end_str}"}}',
        'end tell',
        'end tell',
    ]

    cmd = ["osascript"]
    for line in script_lines:
        cmd.extend(["-e", line])
    subprocess.run(cmd, check=True)
"""Utilities for interacting with the macOS Calendar via AppleScript."""

from __future__ import annotations

import subprocess
from datetime import datetime


def _format_as_applescript_date(dt: datetime) -> str:
    """Return a date string formatted for AppleScript."""

    return dt.strftime("%A, %B %d, %Y at %I:%M %p")


def create_calendar_event(title: str, start: datetime, end: datetime, calendar_name: str = "Home") -> None:
    """Create an event in the macOS Calendar using AppleScript."""

    start_str = _format_as_applescript_date(start)
    end_str = _format_as_applescript_date(end)
    script = (
        f'tell application "Calendar" '
        f'to tell calendar "{calendar_name}" '
        f'to make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"}}'
    )
    subprocess.run(["osascript", "-e", script], check=True)

