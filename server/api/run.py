from fastapi import APIRouter, HTTPException
from server.models.schemas import RunRequest, RunResponse
from evoagentx.core.runner import run_workflow_async
from server.core.websocket_manager import manager

router = APIRouter()

@router.post("/run", response_model=RunResponse)
async def run(request: RunRequest):
    try:
        output = await run_workflow_async(request.goal, progress_cb=manager.broadcast)
    except ValueError as e:
        # < 10 characters or other validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # unexpected agent errors
        raise HTTPException(status_code=500, detail="EvoAgent failed") from e

    return RunResponse(goal=request.goal, output=output)
