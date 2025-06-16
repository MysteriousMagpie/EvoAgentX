from datetime import datetime
from pydantic import BaseModel
from evoagentx.tools.interpreter_docker import DockerLimits, ALLOWED_RUNTIMES


class RunRequest(BaseModel):
    goal: str


class RunResponse(BaseModel):
    goal: str
    output: str


class ExecRequest(BaseModel):
    code: str
    runtime: str = "python:3.11"
    limits: DockerLimits = DockerLimits()

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "code": "print('hi')",
                "runtime": "python:3.11",
                "limits": {"memory": "512m", "cpus": "1.0", "timeout": 20},
            }]
        }
    }


class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    runtime_seconds: float


class EventBase(BaseModel):
    title: str
    start: str
    end: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int


class MacCalendarEvent(BaseModel):
    """Schema for creating macOS Calendar events."""


    title: str
    start: datetime
    end: datetime
    calendar_name: str = "Home"
