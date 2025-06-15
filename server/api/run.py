from fastapi import APIRouter

from ..core.agent_runner import run_goal
from ..models.schemas import RunRequest, RunResponse

router = APIRouter()


@router.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    output = run_goal(request.goal)
    return RunResponse(goal=request.goal, output=output)
