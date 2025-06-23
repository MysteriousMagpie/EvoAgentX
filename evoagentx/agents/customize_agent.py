import json
import inspect
from pydantic import create_model, Field
from typing import Union, Optional, Callable, Type, List, Tuple, cast

from .agent import Agent
from ..core.logging import logger
from ..core.registry import MODULE_REGISTRY, PARSE_FUNCTION_REGISTRY
from ..core.module_utils import parse_json_from_llm_output
from ..core.message import Message, MessageType
from ..models.model_configs import LLMConfig 
from ..models.base_model import BaseLLM, PARSER_VALID_MODE
from ..prompts.utils import DEFAULT_SYSTEM_PROMPT
from ..prompts.template import PromptTemplate
from ..actions.action import Action, ActionInput, ActionOutput
from ..utils.utils import generate_dynamic_class_name, make_parent_folder

OUTPUT_EXTRACTION_PROMPT = """
You are given the following text:
{text}

Within this text, there are specific outputs we want to extract. Please locate and extract the content for each of the following outputs:
{output_description}

**Instructions:**
1. Read through the provided text carefully.
2. For each of the listed output names, extract the corresponding content from the text. 
3. Return your findings in a single JSON object, where the JSON keys **exactly match** the output names given above.
4. If you cannot find content for an output, set its value to an empty string ("") or `null`.
5. Do not include any additional keys in the JSON. 
6. Your final output should be valid JSON and should not include any explanatory text.

**Example JSON format:**
{{
  "<OUTPUT_NAME_1>": "Extracted content here",
  "<OUTPUT_NAME_2>": "Extracted content here",
  "<OUTPUT_NAME_3>": "Extracted content here"
}}

Now, based on the text and the instructions above, provide your final JSON output.
"""


def prepare_action_prompt(self, inputs: Optional[dict] = None, system_prompt: Optional[str] = None) -> Union[str, List[dict]]:
    """Prepare prompt for action execution.
    
    This helper function transforms the input dictionary into a formatted prompt
    for the language model.
    
    Args:
        self: The action instance
        inputs: Dictionary of input parameters
        
    Returns:
        str: Formatted prompt ready for LLM
        
    Raises:
        TypeError: If an input value type is not supported
    """
    inputs = inputs or {}
    prompt_params_names = self.inputs_format.get_attrs()
    prompt_params_values = {}
    for param in prompt_params_names:
        value = inputs.get(param, "")
        if isinstance(value, str):
            prompt_params_values[param] = value
        elif isinstance(value, (dict, list)):
            prompt_params_values[param] = json.dumps(value, indent=4)
        else:
            raise TypeError(f"The input type {type(value)} is invalid! Valid types: [str, dict, list].")
    
    # return self.prompt.format(**prompt_params_values) if prompt_params_values else self.prompt
    if self.prompt is not None:
        return self.prompt.format(**prompt_params_values) if prompt_params_values else self.prompt
    elif self.prompt_template is not None:
        return self.prompt_template.format(
            system_prompt=system_prompt, 
            values=prompt_params_values, 
            inputs_format=self.inputs_format, 
            outputs_format=self.outputs_format, 
            parse_mode=self.parse_mode, 
            title_format=self.title_format, 
            custom_output_format=self.custom_output_format
        )
    else:
        raise ValueError("`prompt` or `prompt_template` is required when creating a CustomizeAgent.")

def prepare_extraction_prompt(self, llm_output_content: str) -> str:
    """Prepare extraction prompt for fallback extraction when parsing fails.
    
    Args:
        self: The action instance
        llm_output_content: Raw output content from LLM
        
    Returns:
        str: Formatted extraction prompt
    """
    attr_descriptions: dict = self.outputs_format.get_attr_descriptions()
    output_description_list = [] 
    for i, (name, desc) in enumerate(attr_descriptions.items()):
        output_description_list.append(f"{i+1}. {name}\nDescription: {desc}")
    output_description = "\n\n".join(output_description_list)
    return OUTPUT_EXTRACTION_PROMPT.format(text=llm_output_content, output_description=output_description)

def customize_action_execute(self, llm: Optional[BaseLLM] = None, inputs: Optional[dict] = None, sys_msg: Optional[str]=None, return_prompt: bool = False, **kwargs) -> Union[ActionOutput, Tuple[ActionOutput, str]]:
    """Execute a customized action using the language model.
    
    Args:
        self: The action instance
        llm: Language model to use for generating outputs
        inputs: Dictionary of input parameters to format the prompt
        sys_msg: Optional system message to provide to the LLM
        return_prompt: Whether to return the formatted prompt alongside the output
        **kwargs: Additional parameters to pass to the language model
        
    Returns:
        If return_prompt is False, returns the parsed output
        If return_prompt is True, returns a tuple (parsed_output, formatted_prompt)
        
    Raises:
        TypeError: If an input value type is not supported
    """
    # ensure llm is BaseLLM for type checker
    llm = cast(BaseLLM, llm or self.llm)
    prompt = self.prepare_action_prompt(inputs, system_prompt=sys_msg)
    
    # generate output
    if isinstance(prompt, str):
        llm_output = llm.generate(prompt=prompt, system_message=sys_msg)
    else:
        llm_output = llm.generate(messages=prompt)
    if isinstance(llm_output, list):
        llm_output = llm_output[0]
    
    try:
        output = self.outputs_format.parse(llm_output.content, parse_mode=self.parse_mode, parse_func=self.parse_func, title_format=self.title_format)
    except Exception:
        logger.warning(f"Couldn't automatically extract output data for '{self.name}'. Use LLM to extract output data ...")
        extraction_prompt = self.prepare_extraction_prompt(llm_output.content)
        llm_extracted_output = llm.generate(prompt=extraction_prompt)
        if isinstance(llm_extracted_output, list):
            llm_extracted_output = llm_extracted_output[0]
        llm_extracted_data = parse_json_from_llm_output(llm_extracted_output.content)
        output = self.outputs_format.from_dict(llm_extracted_data)

    if return_prompt:
        return output, prompt
    return output

async def customize_action_async_execute(self, llm: Optional[BaseLLM] = None, inputs: Optional[dict] = None, sys_msg: Optional[str]=None, return_prompt: bool = False, **kwargs) -> Union[ActionOutput, Tuple[ActionOutput, str]]:
    """Asynchronously execute a customized action using the language model.
    
    This is the async version of customize_action_execute method, using async_generate instead of generate.
    
    Args:
        self: The action instance
        llm: Language model to use for generating outputs
        inputs: Dictionary of input parameters to format the prompt
        sys_msg: Optional system message to provide to the LLM
        return_prompt: Whether to return the formatted prompt alongside the output
        **kwargs: Additional parameters to pass to the language model
        
    Returns:
        If return_prompt is False, returns the parsed output
        If return_prompt is True, returns a tuple (parsed_output, formatted_prompt)
        
    Raises:
        TypeError: If an input value type is not supported
    """
    # ensure llm is BaseLLM for type checker
    llm = cast(BaseLLM, llm or self.llm)
    prompt = self.prepare_action_prompt(inputs, system_prompt=sys_msg)
    
    # generate async output
    if isinstance(prompt, str):
        llm_output = await llm.async_generate(prompt=prompt, system_message=sys_msg)
    else:
        llm_output = await llm.async_generate(messages=prompt)
    if isinstance(llm_output, list):
        llm_output = llm_output[0]
    
    try:
        output = self.outputs_format.parse(llm_output.content, parse_mode=self.parse_mode, parse_func=self.parse_func, title_format=self.title_format)
    except Exception:
        logger.warning(f"Couldn't automatically extract output data for '{self.name}'. Use LLM to extract output data ...")
        extraction_prompt = self.prepare_extraction_prompt(llm_output.content)
        
        llm_extracted_output = await llm.async_generate(prompt=extraction_prompt)
        if isinstance(llm_extracted_output, list):
            llm_extracted_output = llm_extracted_output[0]
        llm_extracted_data = parse_json_from_llm_output(llm_extracted_output.content)
        output = self.outputs_format.from_dict(llm_extracted_data)

    if return_prompt:
        return output, prompt
    return output

class CustomizeAgent(Agent):

    """
    CustomizeAgent provides a flexible framework for creating specialized LLM-powered agents without 
    writing custom code. It enables the creation of agents with well-defined inputs and outputs, 
    custom prompt templates, and configurable parsing strategies. 
    
    Attributes:
        name (str): The name of the agent.
        description (str): A description of the agent's purpose and capabilities.
        prompt_template (PromptTemplate, optional): The prompt template that will be used for the agent's primary action. 
        prompt (str, optional): The prompt template that will be used for the agent's primary action.
            Should contain placeholders in the format `{input_name}` for each input parameter.
        llm_config (LLMConfig, optional): Configuration for the language model.
        inputs (List[dict], optional): List of input specifications, where each dict (e.g., `{"name": str, "type": str, "description": str, ["required": bool]}`) contains:
            - name (str): Name of the input parameter
            - type (str): Type of the input
            - description (str): Description of what the input represents
            - required (bool, optional): Whether this input is required (default: True)
        outputs (List[dict], optional): List of output specifications, where each dict (e.g., `{"name": str, "type": str, "description": str, ["required": bool]}`) contains:
            - name (str): Name of the output field
            - type (str): Type of the output
            - description (str): Description of what the output represents
            - required (bool, optional): Whether this output is required (default: True)
        system_prompt (str, optional): The system prompt for the LLM. Defaults to DEFAULT_SYSTEM_PROMPT.
        output_parser (Type[ActionOutput], optional): A custom class for parsing the LLM's output.
            Must be a subclass of ActionOutput.
        parse_mode (str, optional): Mode for parsing LLM output. Options are:
            - "title": Parse outputs using section titles (default)
            - "str": Parse as plain text
            - "json": Parse as JSON
            - "xml": Parse as XML
            - "custom": Use a custom parsing function
        parse_func (Callable, optional): Custom function for parsing LLM output when parse_mode is "custom".
            Must accept a "content" parameter and return a dictionary.
        title_format (str, optional): Format string for title parsing mode with {title} placeholder.
            Default is "## {title}".
        custom_output_format (str, optional): Specify the output format. Only used when `prompt_template` is used. 
            If not provided, the output format will be constructed from the `outputs` specification and `parse_mode`. 
    """
    def __init__(
        self, 
        name: str, 
        description: str, 
        prompt: Optional[str] = None, 
        prompt_template: Optional[PromptTemplate] = None, 
        llm_config: Optional[LLMConfig] = None, 
        inputs: Optional[List[dict]] = None, 
        outputs: Optional[List[dict]] = None, 
        system_prompt: Optional[str] = None,
        output_parser: Optional[Type[ActionOutput]] = None, 
        parse_mode: Optional[str] = "title", 
        parse_func: Optional[Callable] = None, 
        title_format: Optional[str] = None, 
        custom_output_format: Optional[str] = None, 
        **kwargs
    ):
        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        inputs = inputs or [] 
        outputs = outputs or [] 

        if prompt is not None and prompt_template is not None:
            logger.warning("Both `prompt` and `prompt_template` are provided in `CustomizeAgent`. `prompt_template` will be used.")
            prompt = None 

        if isinstance(parse_func, str):
            if not PARSE_FUNCTION_REGISTRY.has_function(parse_func):
                raise ValueError(f"parse function `{parse_func}` is not registered! To instantiate a CustomizeAgent from a file, you should use decorator `@register_parse_function` to register the parse function.")
            parse_func = PARSE_FUNCTION_REGISTRY.get_function(parse_func)
        
        if isinstance(output_parser, str):
            output_parser = MODULE_REGISTRY.get_module(output_parser)
        
        # set default title format 
        if parse_mode == "title" and title_format is None:
            title_format = "## {title}"

        # validate the data 
        self._validate_data(
            prompt=prompt,
            prompt_template=prompt_template,
            inputs=inputs,
            outputs=outputs,
            output_parser=output_parser,
            parse_mode=parse_mode,
            parse_func=parse_func,
            title_format=title_format
        )

        customize_action = self.create_customize_action(
            name=name, 
            desc=description, 
            prompt=prompt, 
            prompt_template=prompt_template, 
            inputs=inputs, 
            outputs=outputs, 
            parse_mode=parse_mode, 
            parse_func=parse_func,
            output_parser=output_parser,
            title_format=title_format,
            custom_output_format=custom_output_format 
        )
        super().__init__(
            name=name, 
            description=description, 
            llm_config=llm_config, 
            system_prompt=system_prompt, 
            actions=[customize_action], 
            **kwargs
        )
        self._store_inputs_outputs_info(inputs, outputs)
        self.output_parser = output_parser 
        self.parse_mode = parse_mode 
        self.parse_func = parse_func 
        self.title_format = title_format
        self.custom_output_format = custom_output_format

    @property
    def customize_action_name(self) -> str:
        """
        Get the name of the primary custom action for this agent.
        
        Returns:
            The name of the primary custom action
        """
        for action in self.actions:
            if action.name != self.cext_action_name:
                return action.name
        raise ValueError("Couldn't find the customize action name!")

    @property
    def action(self) -> Action:
        """
        Get the primary custom action for this agent.
        
        Returns:
            The primary custom action
        """
        return self.get_action(self.customize_action_name) 
    
    @property
    def prompt(self) -> Optional[str]:
        """
        Get the prompt for the primary custom action.
        
        Returns:
            The prompt for the primary custom action
        """
        return self.action.prompt
    
    def _validate_data(self, prompt: Optional[str], prompt_template: Optional[PromptTemplate], inputs: List[dict], outputs: List[dict], output_parser: Optional[Type[ActionOutput]], parse_mode: Optional[str], parse_func: Optional[Callable], title_format: Optional[str]):
        """Validate the agent data including prompt, inputs, outputs, and parsing settings.
        
        Args:
            prompt (str): The prompt template for the agent.
            prompt_template (PromptTemplate): The prompt template object for the agent.
            inputs (List[dict]): The list of input specifications.
            outputs (List[dict]): The list of output specifications.
            output_parser (Type[ActionOutput]): The output parser class.
            parse_mode (str): The mode for parsing the LLM output.
            parse_func (Callable): The custom parsing function.
            title_format (str): The format for the title in title parsing mode.
        
        Raises:
            ValueError: If any of the validation checks fail.
            KeyError: If required input parameters are not found in the prompt.
        """
        # check if the prompt is provided
        if not prompt and not prompt_template:
            raise ValueError("`prompt` or `prompt_template` is required when creating a CustomizeAgent.")
        
        # check if all the inputs are in the prompt (only used when prompt_template is not provided)
        # if using raw prompt, ensure placeholders exist
        if prompt_template is None and inputs and prompt:
            all_input_names = [input_item["name"] for input_item in inputs]
            missing = [name for name in all_input_names if f'{{{name}}}' not in prompt]
            if missing:
                raise KeyError(f"The following inputs are not found in the prompt: {missing}.")
        
        # check if the output_parser is valid 
        if output_parser is not None:
            # validate outputs list, ensure list passed
            self._check_output_parser(outputs or [], output_parser)
        
        # check the parse_mode, parse_func, and title_format
        if parse_mode not in PARSER_VALID_MODE:
            raise ValueError(f"'{parse_mode}' is an invalid value for `parse_mode`. Available choices: {PARSER_VALID_MODE}.")
        
        if parse_mode == "custom":
            if parse_func is None:
                raise ValueError("`parse_func` (a callable function with an input argument `content`) must be provided when `parse_mode` is 'custom'.")
        
        if parse_func is not None:
            if not callable(parse_func):
                raise ValueError("`parse_func` must be a callable function with an input argument `content`.")
            signature = inspect.signature(parse_func)
            if "content" not in signature.parameters:
                raise ValueError("`parse_func` must have an input argument `content`.")
            if not PARSE_FUNCTION_REGISTRY.has_function(parse_func.__name__):
                logger.warning(
                    f"parse function `{parse_func.__name__}` is not registered. This can cause issues when loading the agent from a file. "
                    f"It is recommended to register the parse function using `register_parse_function`:\n"
                    f"from evoagentx.core.registry import register_parse_function\n"
                    f"@register_parse_function\n"
                    f"def {parse_func.__name__}(content: str) -> dict:\n"
                    r"    return {'output_name': output_value}" 
                )

        if title_format is not None:
            if parse_mode != "title":
                logger.warning(f"`title_format` will not be used because `parse_mode` is '{parse_mode}', not 'title'. Set `parse_mode='title'` to use title formatting.")
            if r'{title}' not in title_format:
                raise ValueError(r"`title_format` must contain the placeholder `{title}`.")
    
    def create_customize_action(
        self,
        name: str,
        desc: str,
        inputs: List[dict],
        outputs: List[dict],
        parse_mode: Optional[str],
        prompt: Optional[str] = None,
        prompt_template: Optional[PromptTemplate] = None,
        parse_func: Optional[Callable] = None,
        output_parser: Optional[Type[ActionOutput]] = None,
        title_format: Optional[str] = "## {title}",
        custom_output_format: Optional[str] = None
    ) -> Action:
        """Create a custom action based on the provided specifications.
        
        This method dynamically generates an Action class and instance with:
        - Input parameters defined by the inputs specification
        - Output format defined by the outputs specification
        - Custom execution logic using the customize_action_execute function
        
        Args:
            name: Base name for the action
            desc: Description of the action
            prompt: Prompt template for the action
            prompt_template: Prompt template for the action
            inputs: List of input field specifications
            outputs: List of output field specifications
            parse_mode: Mode to use for parsing LLM output
            parse_func: Optional custom parsing function
            output_parser: Optional custom output parser class
            
        Returns:
            A newly created Action instance
        """
        # create the action input type
        action_input_fields = {}
        for field in inputs:
            required = field.get("required", True)
            if required:
                action_input_fields[field["name"]] = (str, Field(description=field["description"]))
            else:
                action_input_fields[field["name"]] = (Optional[str], Field(default=None, description=field["description"]))
        
        action_input_type = create_model(
            self._get_unique_class_name(
                generate_dynamic_class_name(name+" action_input")
            ),
            **action_input_fields, 
            __base__=ActionInput
        )

        # create the action output type
        if output_parser is None:
            action_output_fields = {}
            for field in outputs:
                required = field.get("required", True)
                if required:
                    action_output_fields[field["name"]] = (Union[str, dict, list], Field(description=field["description"]))
                else:
                    action_output_fields[field["name"]] = (Optional[Union[str, dict, list]], Field(default=None, description=field["description"]))
            
            action_output_type = create_model(
                self._get_unique_class_name(
                    generate_dynamic_class_name(name+" action_output")
                ),
                **action_output_fields, 
                __base__=ActionOutput,
                # get_content_data=customize_get_content_data,
                # to_str=customize_to_str
            )
        else:
            # self._check_output_parser(outputs, output_parser)
            action_output_type = output_parser

        action_cls_name = self._get_unique_class_name(
            generate_dynamic_class_name(name+" action")
        )
        customize_action_cls = create_model(
            action_cls_name,
            parse_mode=(Optional[str], Field(default="title", description="the parse mode of the action, must be one of: ['title', 'str', 'json', 'xml', 'custom']")),
            parse_func=(Optional[Callable], Field(default=None, exclude=True, description="the function to parse the LLM output. It receives the LLM output and returns a dict.")),
            title_format=(Optional[str], Field(default="## {title}", exclude=True, description="the format of the title. It is used when the `parse_mode` is 'title'.")),
            custom_output_format=(Optional[str], Field(default=None, exclude=True, description="the format of the output. It is used when the `prompt_template` is provided.")),
            __base__=Action, 
            execute=customize_action_execute,
            async_execute=customize_action_async_execute,
            prepare_action_prompt=prepare_action_prompt,
            prepare_extraction_prompt=prepare_extraction_prompt
        )

        customize_action = customize_action_cls(
            name = action_cls_name,
            description=desc, 
            prompt=prompt, 
            prompt_template=prompt_template, 
            inputs_format=action_input_type, 
            outputs_format=action_output_type,
            parse_mode=parse_mode,
            parse_func=parse_func,
            title_format=title_format
        )
        return customize_action
    
    def _check_output_parser(self, outputs: List[dict], output_parser: Type[ActionOutput]):

        if output_parser is not None:
            if not isinstance(output_parser, type):
                raise TypeError(f"output_parser must be a class, but got {type(output_parser).__name__}")
            if not issubclass(output_parser, ActionOutput):
                raise ValueError(f"`output_parser` must be a class and a subclass of `ActionOutput`, but got `{output_parser.__name__}`.")
        
        # check if the output parser is compatible with the outputs
        output_parser_fields = output_parser.get_attrs()
        all_output_names = [output_item["name"] for output_item in outputs]
        for field in output_parser_fields:
            if field not in all_output_names:
                raise ValueError(
                    f"The output parser `{output_parser.__name__}` is not compatible with the `outputs`.\n"
                    f"The output parser fields: {output_parser_fields}.\n"
                    f"The outputs: {all_output_names}.\n"
                    f"All the fields in the output parser must be present in the outputs." 
                )
    
    def _store_inputs_outputs_info(self, inputs: List[dict], outputs: List[dict]):

        self._action_input_types, self._action_input_required = {}, {} 
        for field in inputs:
            required = field.get("required", True)
            self._action_input_types[field["name"]] = field["type"]
            self._action_input_required[field["name"]] = required
        self._action_output_types, self._action_output_required = {}, {}
        for field in outputs:
            required = field.get("required", True)
            self._action_output_types[field["name"]] = field["type"]
            self._action_output_required[field["name"]] = required
    
    def __call__(self, inputs: Optional[dict] = None, return_msg_type: MessageType = MessageType.UNKNOWN, **kwargs) -> Message:
        """
        Call the customize action.

        Args:
            inputs (dict): The inputs to the customize action.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            ActionOutput: The output of the customize action.
        """
        # return self.execute(action_name=self.customize_action_name, action_input_data=inputs, **kwargs) 
        inputs = inputs or {} 
        return super().__call__(action_name=self.customize_action_name, action_input_data=inputs, return_msg_type=return_msg_type, **kwargs)
    
    def get_customize_agent_info(self) -> dict:
        """
        Get the information of the customize agent.
        """
        customize_action = self.get_action(self.customize_action_name)
        inputs_fmt = customize_action.inputs_format
        outputs_fmt = customize_action.outputs_format
        # Get attribute names safely
        action_input_params = getattr(inputs_fmt, 'get_attrs', lambda: [])() if inputs_fmt else []
        action_output_params = getattr(outputs_fmt, 'get_attrs', lambda: [])() if outputs_fmt else []
        
        config = {
            "class_name": "CustomizeAgent",
            "name": self.name,
            "description": self.description,
            "prompt": customize_action.prompt,
            "prompt_template": getattr(customize_action.prompt_template, 'to_dict', lambda **kwargs: None)(exclude_none=True) if getattr(customize_action, 'prompt_template', None) else None, 
            # "llm_config": self.llm_config.to_dict(exclude_none=True),
            "inputs": [
                {
                    "name": field,
                    "type": self._action_input_types[field],
                    "description": field_info.description,
                    "required": self._action_input_required[field]
                }
                for field, field_info in getattr(getattr(customize_action, 'inputs_format', None), 'model_fields', {}).items() if field in action_input_params
            ],
            "outputs": [
                {
                    "name": field,
                    "type": self._action_output_types[field],
                    "description": field_info.description,
                    "required": self._action_output_required[field]
                }
                for field, field_info in getattr(getattr(customize_action, 'outputs_format', None), 'model_fields', {}).items() if field in action_output_params
            ],
            "system_prompt": self.system_prompt,
            "output_parser": self.output_parser.__name__ if self.output_parser is not None else None,
            "parse_mode": self.parse_mode,
            "parse_func": self.parse_func.__name__ if self.parse_func is not None else None,
            "title_format": self.title_format 
        }
        return config
    
    def save_module(self, path: str, ignore: List[str] = [], **kwargs)-> str:
        """Save the customize agent's configuration to a JSON file.
        
        Args:
            path: File path where the configuration should be saved
            ignore: List of keys to exclude from the saved configuration
            **kwargs (Any): Additional parameters for the save operation
            
        Returns:
            The path where the configuration was saved
        """
        config = self.get_customize_agent_info()

        for ignore_key in ignore:
            config.pop(ignore_key, None)
        
        # Save to JSON file
        make_parent_folder(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        return path
    
    def _get_unique_class_name(self, candidate_name: str) -> str:
        """
        Get a unique class name by checking if it already exists in the registry.
        If it does, append "Vx" to make it unique.
        """
        if not MODULE_REGISTRY.has_module(candidate_name):
            return candidate_name 
        
        i = 1 
        while True:
            unique_name = f"{candidate_name}V{i}"
            if not MODULE_REGISTRY.has_module(unique_name):
                break
            i += 1 
        return unique_name 
    
    def get_config(self) -> dict:
        """
        Get a dictionary containing all necessary configuration to recreate this agent.
        
        Returns:
            dict: A configuration dictionary that can be used to initialize a new Agent instance
            with the same properties as this one.
        """
        config = self.get_customize_agent_info()
        if getattr(self, 'llm_config', None):
            config["llm_config"] = getattr(self.llm_config, 'to_dict', lambda **kwargs: {})(exclude_none=True)
        return config
    
    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> "CustomizeAgent":
        """Create a CustomizeAgent from a dictionary."""
        return cls(**data)
