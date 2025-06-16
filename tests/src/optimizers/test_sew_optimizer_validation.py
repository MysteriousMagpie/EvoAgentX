import unittest
from unittest.mock import Mock

from evoagentx.models import OpenAILLMConfig
from evoagentx.workflow.action_graph import ActionGraph
from evoagentx.optimizers.sew_optimizer import SEWOptimizer
from evoagentx.evaluators.evaluator import Evaluator


class InvalidActionGraph(ActionGraph):
    """ActionGraph without any operators for validation testing."""

    def __init__(self, llm_config: OpenAILLMConfig, **kwargs):
        super().__init__(name="Invalid", description="Invalid", llm_config=llm_config, **kwargs)
        # no operators defined


class TestSEWOptimizerValidation(unittest.TestCase):
    def setUp(self):
        self.llm_config = OpenAILLMConfig(model="gpt-4o-mini", openai_key="XXX")
        self.llm = Mock()
        self.evaluator = Evaluator(llm=self.llm)
        self.invalid_graph = InvalidActionGraph(llm_config=self.llm_config)

    def test_log_snapshot_with_invalid_graph(self):
        optimizer = SEWOptimizer(graph=self.invalid_graph, evaluator=self.evaluator, llm=self.llm, optimize_mode="prompt")
        with self.assertRaises(ValueError):
            optimizer.log_snapshot(self.invalid_graph, metrics={"score": 0})

    def test_select_graph_with_invalid_snapshot(self):
        optimizer = SEWOptimizer(graph=self.invalid_graph, evaluator=self.evaluator, llm=self.llm, optimize_mode="prompt")
        optimizer._snapshot.append({"index": 0, "graph": self.invalid_graph, "metrics": {"score": 1}})
        with self.assertRaises(ValueError):
            optimizer._select_graph_with_highest_score()


if __name__ == "__main__":
    unittest.main()
