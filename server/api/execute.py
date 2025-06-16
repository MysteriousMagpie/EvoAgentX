from fastapi import APIRouter, HTTPException
from evoagentx.tools.interpreter_docker import DockerInterpreter, ALLOWED_RUNTIMES
from server.models.schemas import ExecRequest, ExecResponse

router = APIRouter()

@router.post("/execute", response_model=ExecResponse)
async def execute(req: ExecRequest):
    if req.runtime not in ALLOWED_RUNTIMES:
        raise HTTPException(status_code=400, detail="Unsupported runtime")
    interpreter = DockerInterpreter(runtime=req.runtime, limits=req.limits, print_stdout=False, print_stderr=False)
    lang = "node" if req.runtime.startswith("node") else "python"
    result = interpreter.execute_with_result(req.code, lang)
    return ExecResponse(**result)
