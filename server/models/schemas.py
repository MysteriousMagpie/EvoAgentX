from pydantic import BaseModel


class RunRequest(BaseModel):
    goal: str


class RunResponse(BaseModel):
    goal: str
    output: str
