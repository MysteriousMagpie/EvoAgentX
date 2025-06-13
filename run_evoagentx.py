from evoagentx.models import OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlowGenerator, WorkFlow
from evoagentx.agents import AgentManager
from dotenv import load_dotenv
import os

# Load .env and get key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Configure LLM
config = OpenAILLMConfig(model="gpt-4o-mini", openai_key=api_key, stream=True)
llm = OpenAILLM(config=config)

# Set goal and build workflow
goal = "Build a simple HTML page about mushrooms"
workflow_graph = WorkFlowGenerator(llm=llm).generate_workflow(goal)

# Manage agents
agent_manager = AgentManager()
agent_manager.add_agents_from_workflow(workflow_graph, llm_config=config)

# Run workflow
workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm)
output = workflow.execute()

print("\n🧠 Final Output:\n", output)
