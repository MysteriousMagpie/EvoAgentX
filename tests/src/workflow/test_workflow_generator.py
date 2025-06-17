import unittest
from unittest.mock import Mock

from evoagentx.workflow.workflow_generator import WorkFlowGenerator
from evoagentx.agents.workflow_reviewer import WorkFlowReviewer
from evoagentx.workflow.workflow_graph import WorkFlowNode, WorkFlowGraph
from evoagentx.core.base_config import Parameter
from evoagentx.core.message import Message, MessageType
from evoagentx.agents.agent import Agent
from evoagentx.actions.agent_generation import AgentGenerationOutput, GeneratedAgent
from evoagentx.models.base_model import BaseLLM


class TestWorkFlowGenerator(unittest.TestCase):
    def test_reviewer_initialized(self):
        mock_llm = Mock(spec=BaseLLM)
        gen = WorkFlowGenerator(llm=mock_llm)
        self.assertIsInstance(gen.workflow_reviewer, WorkFlowReviewer)

    def test_generate_agents_merge_existing(self):
        node = WorkFlowNode(
            name="Task1",
            description="desc",
            inputs=[Parameter(name="x", type="str", description="")],
            outputs=[Parameter(name="y", type="str", description="")],
        )
        wf = WorkFlowGraph(goal="goal", nodes=[node], edges=[])

        existing_agent = Agent(
            name="ExistingAgent",
            description="old",
            llm=Mock(spec=BaseLLM),
            system_prompt="",
            actions=[],
        )

        generator = WorkFlowGenerator(llm=Mock(spec=BaseLLM))

        gen_agent = GeneratedAgent.model_construct(
            name="GeneratedAgent",
            description="new",
            inputs=[],
            outputs=[],
            prompt="prompt",
        )
        ag_output = AgentGenerationOutput(
            selected_agents=["ExistingAgent"],
            generated_agents=[gen_agent],
        )
        message = Message(content=ag_output, msg_type=MessageType.RESPONSE)
        generator.agent_generator.execute = Mock(return_value=message)

        generator.generate_agents(goal="goal", workflow=wf, existing_agents=[existing_agent])

        agent_names = wf.get_node("Task1").get_agents()
        self.assertIn("ExistingAgent", agent_names)
        self.assertIn("GeneratedAgent", agent_names)


if __name__ == "__main__":
    unittest.main()
