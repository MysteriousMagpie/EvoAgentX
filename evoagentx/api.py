from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES

app = FastAPI()


class ExecRequest(BaseModel):
    code: str
    runtime: str = "python:3.11"
    limits: DockerLimits = DockerLimits()


class ExecResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    runtime_seconds: float


@app.post("/execute", response_model=ExecResponse)
def execute(req: ExecRequest):
    if req.runtime not in ALLOWED_RUNTIMES:
        raise HTTPException(status_code=400, detail="Invalid runtime")

    interpreter = DockerInterpreter(runtime=req.runtime, limits=req.limits, print_stdout=False, print_stderr=False)
    language = "node" if req.runtime.startswith("node") else "python"
    start = time.monotonic()
    try:
        output = interpreter.execute(req.code, language)
        runtime = time.monotonic() - start
        return ExecResponse(stdout=output, stderr="", exit_code=0, runtime_seconds=runtime)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
