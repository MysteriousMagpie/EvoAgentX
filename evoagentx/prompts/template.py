import regex
from pydantic import Field
from pydantic_core import PydanticUndefined
from typing import Union, Optional, List, Any, Type

from ..tools.tool import Tool

from ..core.logging import logger 
from ..core.module import BaseModule 
from ..models.base_model import LLMOutputParser


class PromptTemplate(BaseModule):

    instruction: str = Field(description="The instruction that the LLM will follow.")
    context: Optional[str] = Field(default=None, description="Additional context that can help the LLM understand the instruction.")
    constraints: Optional[Union[List[str], str]] = Field(default=None, description="Constraints that the LLM must follow.")
    tools: Optional[List[Union[str, Tool]]] = Field(
        default=None,
        description="Tools that the LLM can use. May be descriptions or Tool objects.")
    demonstrations: Optional[List[dict]] = Field(default=None, description="Examples of how to use the instruction.")
    history: Optional[List[Any]] = Field(default=None, description="History of the conversation between the user and the LLM.")

    def get_field_names(self) -> List[str]:
        return [name for name, _ in type(self).model_fields.items() if name != "class_name"]
    
    def get(self, key: str) -> Any:
        fields = self.get_field_names()
        if key not in fields:
            raise ValueError(f"Invalid key `{key}` for `{self.__class__.__name__}`. Valid keys are: {fields}")
        return getattr(self, key)
    
    def set(self, key: str, value: Any):
        fields = self.get_field_names()
        if key not in fields:
            raise ValueError(f"Invalid key `{key}` for `{self.__class__.__name__}`. Valid keys are: {fields}")
        setattr(self, key, value)

    def get_instruction(self) -> str:
        return self.instruction

    def get_demonstrations(self) -> list[Any]:
        # Ensure return is always a list
        return self.demonstrations if self.demonstrations is not None else []
    
    def get_context(self) -> Optional[str]:
        return self.context
    
    def get_history(self) -> Optional[List[Any]]:
        return self.history
    
    def get_constraints(self) -> Optional[Union[List[str], str]]:
        return self.constraints
    
    def get_tools(self) -> Optional[List[Union[str, Tool]]]:
        return self.tools
    
    def set_instruction(self, instruction: str):
        self.set("instruction", instruction)

    def set_demonstrations(self, demonstrations: List[Any]):
        self.set("demonstrations", demonstrations)

    def set_context(self, context: str):
        self.set("context", context)

    def set_history(self, history: List[Any]):
        self.set("history", history)

    def set_constraints(self, constraints: Union[List[str], str]):
        self.set("constraints", constraints)

    def set_tools(self, tools: List[Union[str, Tool]]):
        self.set("tools", tools)

    def get_required_inputs_or_outputs(self, format: Type[LLMOutputParser]) -> List[str]:
        """
        Get the required fields of the format.
        """
        required_fields = []
        attrs = format.get_attrs()
        for field_name, field_info in format.model_fields.items():
            if field_name not in attrs:
                continue
            field_default = field_info.default
            # A field is required if it doesn't have a default value
            if field_default is PydanticUndefined:
                required_fields.append(field_name)
        return required_fields

    def clear_placeholders(self, text: str) -> str:
        """
        Find all {xx} placeholders in the text, and replace them with `xx`,
        adding backticks only if not already present.
        """
        # Step 1: Find all unique {xx} placeholders (single braces only)
        matches = set(regex.findall(r"(?<!\{)\{([^\{\},\s]+)\}(?!\})", text))

        for field in matches:
            # Pattern: only single-brace {field}, not {{field}} or {{{field}}}
            pattern = r"(?<!\{)\{" + regex.escape(field) + r"\}(?!\})"

            def replacer(match):
                start, end = match.start(), match.end()
                before = text[start - 1] if start > 0 else ""
                after = text[end] if end < len(text) else ""

                replacement = field
                if before != "`":
                    replacement = "`" + replacement
                if after != "`":
                    replacement = replacement + "`"

                return replacement

            text = regex.sub(pattern, replacer, text)

        return text
    
    def check_required_inputs(self, inputs_format: Type[LLMOutputParser], values: dict):
        if inputs_format is None:
            return
        required_inputs = self.get_required_inputs_or_outputs(inputs_format)
        missing_required_inputs = [field for field in required_inputs if field not in values]
        if missing_required_inputs:
            logger.warning(f"Missing required inputs (without default values) for `{inputs_format.__name__}`: {missing_required_inputs}, will set them to empty strings.")
            for field in missing_required_inputs:
                # Try to get a default value if available, else use empty string
                default = inputs_format.model_fields[field].default
                values[field] = default if default is not PydanticUndefined else ""

    def render_input_example(self, inputs_format: Type[LLMOutputParser], values: dict, missing_field_value: str = "") -> str:
        if inputs_format is None and values is None:
            return ""
        if inputs_format is not None:
            fields = inputs_format.get_attrs()
            field_values = {field: values.get(field, missing_field_value) for field in fields}
        else: 
            field_values = values
        return "\n".join(f"[[ **{field}** ]]:\n{value}" for field, value in field_values.items())
    
    def get_output_template(self, outputs_format: Type[LLMOutputParser], parse_mode: str = "title", title_format: str = "## {title}") -> tuple[str, list[str]]:
        output_template: str = ""
        output_keys: list[str] = []
        
        if outputs_format is None:
            raise ValueError("`outputs_format` is required in `get_output_format`.")
        valid_modes = ["json", "xml", "title"]
        if parse_mode not in valid_modes:
            raise ValueError(f"Invalid parse mode `{parse_mode}` for `{self.__class__.__name__}.get_output_template`. Valid modes are: {valid_modes}.")
        
        fields = outputs_format.get_attrs()
        required_fields = self.get_required_inputs_or_outputs(outputs_format)
        if parse_mode == "json":
            json_template = "{{\n"
            for field in fields: 
                json_template += f"    \"{field}\""
                json_template += f": \"{{{field}}}\",\n" if field in required_fields else f" (Optional): \"{{{field}}}\",\n"
            json_template = json_template.rstrip(",\n") + "\n}}"
            output_template, output_keys = json_template, [str(f) for f in fields]
        elif parse_mode == "xml":
            xml_template = ""
            for field in fields:
                xml_template += f"<{field}>\n" if field in required_fields else f"<{field}> (Optional)\n" 
                xml_template += f"{{{field}}}\n</{field}>\n"
            xml_template = xml_template.rstrip("\n")
            output_template, output_keys = xml_template, [str(f) for f in fields]
        elif parse_mode == "title":
            title_template = ""
            for field in fields:
                title_section = title_format.format(title=field)
                title_section += "\n" if field in required_fields else " (Optional)\n"
                title_section += f"{{{field}}}\n\n"
                title_template += title_section
            title_template = title_template.rstrip("\n")
            output_template, output_keys = title_template, [str(f) for f in fields]
        return output_template, output_keys

    def render_instruction(self) -> str:
        # clear the potential placeholders in the instruction. we will use the input section to specify the inputs. 
        instruction_str = self.clear_placeholders(self.instruction)
        return f"### Instruction\nThis is the main task instruction you must follow:\n{instruction_str}\n"
    
    def render_context(self) -> str:
        if not self.context:
            return ""
        return f"### Context\nHere is some additional background information to help you understand the task:\n{self.context}\n"

    def render_tools(self) -> str:
        if not self.tools:
            return ""
        descriptions: List[str] = []
        for tool in self.tools:
            if isinstance(tool, Tool):
                desc_list = tool.get_tool_descriptions()
                try:
                    tool_funcs = tool.get_tools()
                except Exception:
                    tool_funcs = []
                if tool_funcs and len(desc_list) != len(tool_funcs):
                    raise ValueError(
                        f"Mismatch between descriptions and tools for {tool.name}: "
                        f"{len(desc_list)} descriptions for {len(tool_funcs)} functions")
                descriptions.extend(desc_list)
            elif isinstance(tool, str):
                descriptions.append(tool)
            else:
                raise TypeError(
                    f"Invalid tool type {type(tool)}. Expected str or Tool instance")
        tools_str = "\n".join(f"- {d}" for d in descriptions)
        return (
            "### Tools\n" "You can use the following tools or capabilities (if applicable):\n" +
            f"{tools_str}\n"
        )
    
    def render_constraints(self) -> str:
        if not self.constraints:
            return ""
        if isinstance(self.constraints, list):
            constraints_str = "\n".join(f"- {c}" for c in self.constraints)
        else:
            constraints_str = self.constraints
        return f"### Constraints\nYou must follow these rules or constraints when generating your output:\n{constraints_str}\n"
    
    def _render_system_message(self, system_prompt: Optional[str] = None) -> str:
        """
        Render the system message by combining system prompt, instruction, context, tools and constraints.
        """
        prompt_pieces = []
        if system_prompt:
            prompt_pieces.append(system_prompt + "\n")
        prompt_pieces.append(self.render_instruction())
        if self.context:
            prompt_pieces.append(self.render_context())
        if self.tools:
            prompt_pieces.append(self.render_tools())
        if self.constraints:
            prompt_pieces.append(self.render_constraints())
        
        return "\n".join(prompt_pieces)
    
    def render_outputs(self, outputs_format: Type[LLMOutputParser], parse_mode: str="title", title_format: str="## {title}") -> str:

        if outputs_format is None or parse_mode in [None, "str", "custom"] or len(outputs_format.get_attrs()) == 0:
            return "### Outputs Format\nPlease generate a response that best fits the task instruction.\n"
        
        ouptut_template, output_keys = self.get_output_template(outputs_format, parse_mode=parse_mode, title_format=title_format)
        output_str = "### Outputs Format\nYou MUST strictly follow the following format when generating your output:\n\n"
        if parse_mode == "json":
            output_str += "Format your output in json format, such as:\n"
        elif parse_mode == "xml":
            output_str += "Format your output in xml format, such as:\n"
        elif parse_mode == "title":
            output_str += "Format your output in sectioned title format, such as:\n"
        
        example_values = {} 
        for key in output_keys:
            field_info = outputs_format.model_fields.get(key)
            if field_info and field_info.description:
                example_values[key] = "[" + field_info.description + "]"
            else:
                example_values[key] = "[Your output here]"
        output_str += ouptut_template.format(**example_values)

        if "(Optional)" in ouptut_template:
            output_str += "\n\nNote: For optional fields, you can omit them in your output if they are not necessary."
        output_str += "\n"
        return output_str
    
    def format(
        self,
        inputs_format: Optional[Type[LLMOutputParser]] = None,
        outputs_format: Optional[Type[LLMOutputParser]] = None,
        values: Optional[dict] = None,
        parse_mode: Optional[str] = "title",
        title_format: Optional[str] = "## {title}",
        output_format: Optional[str] = None,
        **kwargs
    ) -> str:
        # Only use methods defined in this class
        prompt_pieces = []
        prompt_pieces.append(self.render_instruction())
        if self.context:
            prompt_pieces.append(self.render_context())
        if self.tools:
            prompt_pieces.append(self.render_tools())
        if self.constraints:
            prompt_pieces.append(self.render_constraints())
        return "\n".join(prompt_pieces)
    

class StringTemplate(PromptTemplate):
    def render_demonstrations(
        self,
        inputs_format: Type[LLMOutputParser],
        outputs_format: Type[LLMOutputParser],
        parse_mode: str,
        title_format: str = "## {title}",
        custom_output_format: str = "",
        **kwargs
    ) -> str:
        if custom_output_format is None:
            custom_output_format = ""
        if title_format is None:
            title_format = "## {title}"
        
        if not self.demonstrations:
            return "" 
        
        if inputs_format is None or outputs_format is None:
            raise ValueError("`inputs_format` and `outputs_format` are required in `render_demonstrations`.")
        if len(inputs_format.get_attrs()) == 0 or len(outputs_format.get_attrs()) == 0:
            raise ValueError("`inputs_format` and `outputs_format` must have at least one attribute.")
        
        demo_str_list = [] 
        for i, demo in enumerate(self.demonstrations):
            demo_str = f"Example {i+1}:\n"
            
            demo_str += "### Inputs\n"
            input_fields = inputs_format.get_attrs()
            input_values = {field: demo.get(field, "Not provided") for field in input_fields}
            demo_str += self.render_input_example(inputs_format, input_values, missing_field_value="Not provided")
            demo_str += "\n\n"

            demo_str += "### Outputs\n"
            output_fields = outputs_format.get_attrs()
            output_values = {field: demo.get(field, "Not provided") for field in output_fields}
            if custom_output_format is not None or parse_mode in [None, "str", "custom"]:
                output_str = "\n".join(f"{field}:\n{value}" for field, value in output_values.items())
            else:
                output_template, output_keys = self.get_output_template(outputs_format, parse_mode=parse_mode, title_format=title_format)
                output_str = output_template.format(**output_values)
                output_str = output_str.replace("(Optional)", "")
            demo_str += output_str
            demo_str_list.append(demo_str)
        
        result = "### Examples\n" + "\n\n".join(demo_str_list) + "\n\n=== End of Examples ===\n"
        return result

    # def render_history(self) -> str:
    #     logger.warning(f"`render_history` method is not supported for `{self.__class__.__name__}`. Returning empty string.")
    #     return ""
    
    def render_inputs(self, inputs_format: Type[LLMOutputParser], values: dict) -> str:
        if inputs_format is None:
            raise ValueError("inputs_format must not be None")
        if values is None:
            values = {}
        # Check if all required fields are provided
        self.check_required_inputs(inputs_format, values)
        input_str = "### Inputs\nThese are the input values provided by the user (with input names emplasized):\n"
        input_str += self.render_input_example(inputs_format, values, missing_field_value="Not provided")
        input_str += "\n"
        return input_str

    def format(
        self,
        inputs_format: Optional[Type[LLMOutputParser]] = None,
        outputs_format: Optional[Type[LLMOutputParser]] = None,
        values: Optional[dict] = None,
        parse_mode: Optional[str] = "title",
        title_format: Optional[str] = "## {title}",
        output_format: Optional[str] = None,
        **kwargs
    ) -> str:
        # Use only methods defined in this class
        safe_inputs_format = inputs_format if inputs_format is not None else LLMOutputParser
        safe_outputs_format = outputs_format if outputs_format is not None else LLMOutputParser
        safe_title_format = title_format if title_format is not None else "## {title}"
        safe_output_format = output_format if output_format is not None else ""
        safe_values = values if values is not None else {}
        safe_parse_mode = parse_mode if parse_mode is not None else "title"
        prompt_pieces = []
        prompt_pieces.append(self._render_system_message(""))
        if self.demonstrations:
            prompt_pieces.append(
                self.render_demonstrations(
                    safe_inputs_format,
                    safe_outputs_format,
                    safe_parse_mode,
                    safe_title_format,
                    safe_output_format
                )
            )
        if safe_inputs_format or safe_values:
            prompt_pieces.append("-"*20)
            prompt_pieces.append(self.render_inputs(safe_inputs_format, safe_values))
        if safe_output_format:
            prompt_pieces.append(f"### Outputs Format\n{safe_output_format}")
        else:
            prompt_pieces.append(self.render_outputs(safe_outputs_format, safe_parse_mode, safe_title_format))
        prompt_pieces = [piece for piece in prompt_pieces if piece]
        prompt = "\n".join(prompt_pieces)
        return prompt.strip()
    

class ChatTemplate(StringTemplate):
    # Inherit all methods from StringTemplate without override
    pass
