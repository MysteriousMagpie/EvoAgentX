import unittest
from evoagentx.actions.action import Action
from evoagentx.tools.tool import Tool

class DummyTool(Tool):
    name: str = "dummy"
    def get_tools(self):
        return [self.do]
    def get_tool_schemas(self):
        return []
    def do(self):
        return "done"
    def get_tool_descriptions(self):
        return ["dummy"]

class DummyAction(Action):
    def execute(self, llm=None, inputs=None, sys_msg=None, return_prompt=False, **kwargs):
        return {}

class TestActionSerialization(unittest.TestCase):
    def test_tool_roundtrip(self):
        action = DummyAction(name="a", description="b", tools=[DummyTool()])
        data = action.to_dict()
        loaded = DummyAction.from_dict(data)
        self.assertIsInstance(loaded.tools[0], DummyTool)
        self.assertEqual(loaded.tools[0].name, "dummy")

if __name__ == "__main__":
    unittest.main()
