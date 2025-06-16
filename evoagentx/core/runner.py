from evoagentx.models import OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlowGenerator, WorkFlowGraph, WorkFlow
from evoagentx.agents import AgentManager
from evoagentx.utils.calendar import get_today_events
import os
from dotenv import load_dotenv

load_dotenv()


async def run_workflow_async(goal: str) -> str:
    """
    Run EvoAgentX workflow asynchronously.
    Raises ValueError if goal too short (handled by caller).
    """
    if len(goal.strip()) < 10:
        raise ValueError("Goal must be at least 10 characters")

    openai_key = os.getenv("OPENAI_API_KEY")

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
    workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm)
    context = {"today_events": get_today_events(), "goal": goal}
    return await workflow.async_execute(context)

