import pytest
from evoagentx.prompts.template import PromptTemplate
from evoagentx.tools.tool import Tool
from evoagentx.models.base_model import LLMOutputParser
from typing import List, Dict, Any, Callable

class SimpleTool(Tool):
    name: str = "simple"

    def get_tools(self) -> List[Callable]:
        return [self.do]

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return []

    def do(self):
        pass

    def get_tool_descriptions(self) -> List[str]:
        return ["simple description"]

class BadTool(SimpleTool):
    name: str = "bad"
    def get_tools(self) -> List[Callable]:
        return [self.do, self.other]

    def other(self):
        pass

    def get_tool_descriptions(self) -> List[str]:
        return ["only one"]

def test_render_tools_with_strings():
    tmpl = PromptTemplate(instruction="instr", tools=["a", "b"])
    rendered = tmpl.render_tools()
    assert "- a" in rendered
    assert "- b" in rendered

def test_render_tools_with_objects():
    tmpl = PromptTemplate(instruction="instr", tools=[SimpleTool()])
    rendered = tmpl.render_tools()
    assert "simple description" in rendered

def test_render_tools_mismatch():
    tmpl = PromptTemplate(instruction="instr", tools=[BadTool()])
    with pytest.raises(ValueError):
        tmpl.render_tools()


class SimpleInput(LLMOutputParser):
    required_field: str
    optional_field: str = "opt"


def test_missing_required_inputs_are_added():
    tmpl = PromptTemplate(instruction="instr")
    values = {}
    tmpl.check_required_inputs(SimpleInput, values)
    assert "required_field" in values
    assert values["required_field"] == ""
    assert "optional_field" not in values
