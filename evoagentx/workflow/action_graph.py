import json
from pydantic import Field
from typing import Dict, Any, List

from ..core.logging import logger
from ..core.module import BaseModule
from ..core.registry import MODEL_REGISTRY, MODULE_REGISTRY
from ..models.model_configs import LLMConfig
from .operators import Operator, AnswerGenerate, QAScEnsemble 


class ActionGraph(BaseModule):

    name: str = Field(description="The name of the ActionGraph.")
    description: str = Field(description="The description of the ActionGraph.")
    llm_config: LLMConfig = Field(description="The config of LLM used to execute the ActionGraph.")

    def init_module(self):
        if self.llm_config:
            llm_cls = MODEL_REGISTRY.get_model(self.llm_config.llm_type)
            self._llm = llm_cls(config=self.llm_config)
    
    # def __call__(self, *args: Any, **kwargs: Any) -> dict:
    #     return self.execute(*args, **kwargs)
    
    def execute(self, *args, **kwargs) -> dict:
        """
        Execute the action graph.
        
        Basic implementation that executes operators in sequence.
        Subclasses should override this for custom execution logic.
        """
        try:
            logger.info(f"Executing ActionGraph: {self.name}")
            
            # Get all operators from extra fields
            operators = {}
            if hasattr(self, '__pydantic_extra__') and self.__pydantic_extra__:
                for extra_name, extra_value in self.__pydantic_extra__.items():
                    if isinstance(extra_value, Operator):
                        operators[extra_name] = extra_value
            
            if not operators:
                logger.warning("No operators found in ActionGraph")
                return {"result": "No operators to execute", "status": "warning"}
            
            results = {}
            for operator_name, operator in operators.items():
                logger.info(f"Executing operator: {operator_name}")
                try:
                    result = operator.execute(*args, **kwargs)
                    results[operator_name] = result
                except Exception as e:
                    logger.error(f"Error executing operator {operator_name}: {e}")
                    results[operator_name] = {"error": str(e)}
            
            return {
                "status": "completed",
                "results": results,
                "graph_name": self.name
            }
            
        except Exception as e:
            logger.error(f"Error executing ActionGraph {self.name}: {e}")
            return {"status": "error", "error": str(e), "graph_name": self.name}
    
    async def async_execute(self, *args, **kwargs) -> dict:
        """
        Asynchronously execute the action graph.
        
        Basic implementation that executes operators in sequence asynchronously.
        Subclasses should override this for custom async execution logic.
        """
        try:
            logger.info(f"Async executing ActionGraph: {self.name}")
            
            # Get all operators from extra fields
            operators = {}
            if hasattr(self, '__pydantic_extra__') and self.__pydantic_extra__:
                for extra_name, extra_value in self.__pydantic_extra__.items():
                    if isinstance(extra_value, Operator):
                        operators[extra_name] = extra_value
            
            if not operators:
                logger.warning("No operators found in ActionGraph")
                return {"result": "No operators to execute", "status": "warning"}
            
            results = {}
            for operator_name, operator in operators.items():
                logger.info(f"Async executing operator: {operator_name}")
                try:
                    result = await operator.async_execute(*args, **kwargs)
                    results[operator_name] = result
                except Exception as e:
                    logger.error(f"Error async executing operator {operator_name}: {e}")
                    results[operator_name] = {"error": str(e)}
            
            return {
                "status": "completed",
                "results": results,
                "graph_name": self.name
            }
            
        except Exception as e:
            logger.error(f"Error async executing ActionGraph {self.name}: {e}")
            return {"status": "error", "error": str(e), "graph_name": self.name}
    
    def get_graph_info(self, **kwargs) -> dict:
        """
        Get the information of the action graph, including all operators from the instance.
        """
        operators = {}
        # the extra fields are the fields that are not defined in the Pydantic model 
        if hasattr(self, '__pydantic_extra__') and self.__pydantic_extra__:
            for extra_name, extra_value in self.__pydantic_extra__.items():
                if isinstance(extra_value, Operator):
                    operators[extra_name] = extra_value

        config = {
            "class_name": self.__class__.__name__,
            "name": self.name,
            "description": self.description, 
            "operators": {
                operator_name: {
                    "class_name": operator.__class__.__name__,
                    "name": operator.name,
                    "description": operator.description,
                    "interface": operator.interface,
                    "prompt": operator.prompt
                }
                for operator_name, operator in operators.items()
            }
        }
        return config

    def validate(self):
        """Validate required fields and operators structure."""
        missing_fields = []
        if not getattr(self, "name", None):
            missing_fields.append("name")
        if not getattr(self, "description", None):
            missing_fields.append("description")
        if not getattr(self, "llm_config", None):
            missing_fields.append("llm_config")
        if missing_fields:
            raise ValueError(f"ActionGraph is missing required fields: {missing_fields}")

        operators = {}
        for extra_name, extra_value in self.__pydantic_extra__.items():
            if isinstance(extra_value, Operator):
                operators[extra_name] = extra_value

        if not operators:
            raise ValueError("ActionGraph must contain at least one Operator")

        for op_name, op in operators.items():
            op_missing = []
            if not getattr(op, "name", None):
                op_missing.append("name")
            if not getattr(op, "description", None):
                op_missing.append("description")
            if getattr(op, "interface", None) is None:
                op_missing.append("interface")
            if getattr(op, "prompt", None) is None:
                op_missing.append("prompt")
            if op_missing:
                raise ValueError(f"Operator '{op_name}' is missing fields: {op_missing}")

        return True
    
    @classmethod
    def load_module(cls, path: str, llm_config: LLMConfig = None, **kwargs) -> Dict:
        """
        Load the ActionGraph from a file.
        """
        assert llm_config is not None, "must provide `llm_config` when using `load_module` or `from_file` to load the ActionGraph from local storage" 
        action_graph_data = super().load_module(path, **kwargs) 
        action_graph_data["llm_config"] = llm_config.to_dict()
        return action_graph_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> "ActionGraph":
        """
        Create an ActionGraph from a dictionary.
        """
        class_name = data.get("class_name", None)
        if class_name:
            cls = MODULE_REGISTRY.get_module(class_name)
        operators_info = data.pop("operators", None)
        module = cls._create_instance(data)
        if operators_info:
            for extra_name, extra_value in module.__pydantic_extra__.items():
                if isinstance(extra_value, Operator) and extra_name in operators_info:
                    extra_value.set_operator(operators_info[extra_name])
        return module
    
    def save_module(self, path: str, ignore: List[str] = [], **kwargs):
        """
        Save the workflow graph to a module file.
        """
        logger.info("Saving {} to {}", self.__class__.__name__, path)
        config = self.get_graph_info()
        for ignore_key in ignore:
            config.pop(ignore_key, None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return path
    
    def get_config(self) -> dict:
        """
        Get a dictionary containing all necessary configuration to recreate this action graph.
        
        Returns:
            dict: A configuration dictionary that can be used to initialize a new ActionGraph instance
            with the same properties as this one.
        """
        config = self.get_graph_info()
        config["llm_config"] = self.llm_config.to_dict()
        return config

class QAActionGraph(ActionGraph):

    def __init__(self, llm_config: LLMConfig, **kwargs):

        name = kwargs.pop("name") if "name" in kwargs else "Simple QA Workflow"
        description = kwargs.pop("description") if "description" in kwargs else \
            "This is a simple QA workflow that use self-consistency to make predictions."
        super().__init__(name=name, description=description, llm_config=llm_config, **kwargs)
        self.answer_generate = AnswerGenerate(self._llm)
        self.sc_ensemble = QAScEnsemble(self._llm)
        
    def execute(self, problem: str) -> dict:

        solutions = [] 
        for _ in range(3):
            response = self.answer_generate(input=problem)
            answer = response["answer"]
            solutions.append(answer)
        ensemble_result = self.sc_ensemble(solutions=solutions)
        best_answer = ensemble_result["response"]
        return {"answer": best_answer}
    
    async def async_execute(self, problem: str) -> dict:
        solutions = [] 
        for _ in range(3):
            response = await self.answer_generate(input=problem)
            answer = response["answer"]
            solutions.append(answer)
        ensemble_result = await self.sc_ensemble(solutions=solutions)
        best_answer = ensemble_result["response"]
        return {"answer": best_answer}
    