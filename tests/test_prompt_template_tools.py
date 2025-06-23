import pytest
from evoagentx.prompts.template import PromptTemplate
from evoagentx.tools.tool import Tool
from typing import List, Dict, Any, Callable

from evoagentx.models.base_model import LLMOutputParser

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

def test_check_required_inputs_populates_missing_fields():
    class DummyParser(LLMOutputParser):
        required1: str
        required2: int
        optional1: str = "default"

    tmpl = PromptTemplate(instruction="instr")
    values = {"required1": "foo"}
    tmpl.check_required_inputs(DummyParser, values)
    # required2 should be added as ""
    assert "required2" in values
    assert values["required2"] == ""
    # required1 should remain unchanged
    assert values["required1"] == "foo"
    # optional1 should not be added
    assert "optional1" not in values

def test_check_required_inputs_with_all_fields_present():
    class DummyParser2(LLMOutputParser):
        required1: str
        required2: int
    tmpl = PromptTemplate(instruction="instr")
    values = {"required1": "foo", "required2": 42}
    tmpl.check_required_inputs(DummyParser2, values)
    assert values["required1"] == "foo"
    assert values["required2"] == 42
