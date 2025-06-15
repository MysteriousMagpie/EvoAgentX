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
