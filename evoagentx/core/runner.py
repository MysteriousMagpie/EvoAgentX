from evoagentx.models import OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlowGenerator, WorkFlowGraph, WorkFlow
from evoagentx.workflow.environment import Environment
from evoagentx.agents import AgentManager
from evoagentx.utils.calendar import get_today_events
import os
import asyncio
from dotenv import load_dotenv
from typing import Tuple, Union

load_dotenv()




async def run_workflow_async(goal: str, progress_cb=None, return_graph: bool = False) -> Union[str, Tuple[str, dict]]:
    """
    Run EvoAgentX workflow asynchronously.
    Raises ValueError if goal too short (handled by caller).
    """
    if len(goal.strip()) < 10:
        raise ValueError("Goal must be at least 10 characters")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("[DEBUG] OpenAI key loaded in runner:", openai_key[:8], "...")
    else:
        print("[DEBUG] OpenAI key loaded in runner: MISSING")

    llm_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=openai_key,
        stream=False,
        output_response=True,
        max_tokens=16000,
    )
    llm = OpenAILLM(config=llm_config)

    context = {
        "today_events": get_today_events(),
        "goal": goal,
    }

    wf_generator = WorkFlowGenerator(llm=llm)
    workflow_graph: WorkFlowGraph = wf_generator.generate_workflow(goal=goal, context=context)

    agent_manager = AgentManager()
    agent_manager.add_agents_from_workflow(workflow_graph, llm_config=llm_config)
    env = Environment()
    if progress_cb:
        orig_update = env.update

        def patched_update(message, state=None, error=None, **kwargs):
            import json
            progress_data = {
                "type": "progress",
                "message": str(message),
                "state": state,
                "error": error,
                **kwargs
            }
            asyncio.create_task(progress_cb(json.dumps(progress_data)))
            # Ensure state and error are not None before passing
            if state is None or error is None:
                raise ValueError("'state' and 'error' must not be None")
            return orig_update(message, state=state, error=error, **kwargs)

        env.update = patched_update  # type: ignore

    workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm, environment=env)
    context = {"today_events": get_today_events(), "goal": goal}
    if progress_cb:
        import json
        await progress_cb(json.dumps({"type": "status", "message": "Workflow started"}))
    result = await workflow.async_execute(context)
    if progress_cb:
        import json
        await progress_cb(json.dumps({"type": "status", "message": "Workflow completed"}))
    if return_graph:
        return result, workflow_graph.get_config()
    return result

