from __future__ import annotations

import os
from dotenv import load_dotenv
from evoagentx.models import OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlowGenerator, WorkFlowGraph, WorkFlow
from evoagentx.agents import AgentManager


def run_workflow(goal: str) -> str:
    """Generate and execute a workflow for a given goal and return output."""
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")

    llm_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=openai_key,
        stream=True,
        output_response=True,
        max_tokens=16000,
    )
    llm = OpenAILLM(config=llm_config)

    wf_generator = WorkFlowGenerator(llm=llm)
    workflow_graph: WorkFlowGraph = wf_generator.generate_workflow(goal=goal)

    agent_manager = AgentManager()
    agent_manager.add_agents_from_workflow(workflow_graph, llm_config=llm_config)

    workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm)
    output = workflow.execute()
    return output
