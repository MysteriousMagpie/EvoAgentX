from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from evoagentx.tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES

app = FastAPI()

class ExecRequest(BaseModel):
    code: str
    runtime: str = "python:3.11"
    limits: DockerLimits = DockerLimits()

@app.post("/execute")
def execute(req: ExecRequest):
    if req.runtime not in ALLOWED_RUNTIMES:
        raise HTTPException(status_code=400, detail="Invalid runtime")
    interpreter = DockerInterpreter(runtime=req.runtime, limits=req.limits, print_stdout=False, print_stderr=False)
    language = "node" if req.runtime.startswith("node") else "python"
    try:
        res = interpreter.execute_verbose(req.code, language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "stdout": res.stdout,
        "stderr": res.stderr,
        "exit_code": res.exit_code,
        "runtime_seconds": res.runtime_seconds,
    }
