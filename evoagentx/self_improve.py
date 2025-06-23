from evoagentx.workflow import WorkFlowGenerator
from evoagentx.agents.meta_agents import CodeSearchAgent, RefactorAgent, TestAgent, CriticAgent, PRAgent
from evoagentx.agents.agent_manager import AgentManager
import uuid

SELF_IMPROVE_TEMPLATE = """
1) CodeSearchAgent -> RefactorAgent
2) RefactorAgent   -> TestAgent
3) TestAgent       -> CriticAgent
4) CriticAgent (if 'retry') -> RefactorAgent
5) CriticAgent (if 'pass')  -> PRAgent
"""

def generate_self_improve_workflow(goal: str, llm):
    gen = WorkFlowGenerator(llm=llm)
    return gen.from_text_diagram(
        SELF_IMPROVE_TEMPLATE,
        context={"improvement_goal": goal},
    )

def self_improve(goal: str, llm, max_cycles=3, token_cap=20000):
    """Run the self-improvement workflow."""
    # Register meta-agents if not already present
    for agent_cls in [CodeSearchAgent, RefactorAgent, TestAgent, CriticAgent, PRAgent]:
        AgentManager().add_agent(agent_cls())
    # Create feature branch
    branch = f"self-improve-{uuid.uuid4()}"
    AgentManager.toolbox["shell.run"](f"git checkout -b {branch}")
    # Generate and run workflow
    generate_self_improve_workflow(goal, llm)
    # --- Loop logic ---
    cycles = 0
    tokens_spent = 0
    decision = "retry"
    while cycles < max_cycles and tokens_spent < token_cap and decision == "retry":
        # 1. CodeSearchAgent
        search_result = CodeSearchAgent().act(goal)
        # 2. RefactorAgent (stub: just echo search result)
        RefactorAgent().act("stub.py", search_result)
        # 3. TestAgent
        test_result = TestAgent().act()
        # 4. CriticAgent
        critic_result = CriticAgent().act("diff", test_result)
        import json
        try:
            critic_json = json.loads(critic_result)
            decision = critic_json.get("decision", "retry")
        except Exception:
            decision = "retry"
        cycles += 1
        tokens_spent += 1000  # stub: increment
    # 5. PRAgent if accepted
    if decision == "accept":
        PRAgent().act(branch)
    return decision

def self_improve_async(goal: str, llm=None):
    # Async stub for demonstration
    import asyncio
    return asyncio.create_task(async_self_improve(goal, llm))

async def async_self_improve(goal: str, llm=None):
    return self_improve(goal, llm)
