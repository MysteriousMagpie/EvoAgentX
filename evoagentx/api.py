from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES

app = FastAPI()


class ExecRequest(BaseModel):
    code: str
    runtime: str = "python:3.11"
    limits: DockerLimits = DockerLimits()


@app.post("/execute")
def execute(req: ExecRequest):
    if req.runtime not in ALLOWED_RUNTIMES:
        raise HTTPException(status_code=400, detail="Unsupported runtime")
    interpreter = DockerInterpreter(
        runtime=req.runtime,
        limits=req.limits,
        print_stdout=False,
        print_stderr=False,
    )
    lang = "node" if req.runtime.startswith("node") else "python"
    result = interpreter.execute_details(req.code, lang)
    return result

