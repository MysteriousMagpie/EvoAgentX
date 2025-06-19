import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from typing import Optional, List, cast, Sequence
from litellm.utils import token_counter
from litellm.cost_calculator import cost_per_token
from ..core.registry import register_model
from .model_configs import OpenAILLMConfig
from .base_model import BaseLLM
from .model_utils import Cost, cost_manager, get_openai_model_cost 


@register_model(config_cls=OpenAILLMConfig, alias=["openai_llm"])
class OpenAILLM(BaseLLM):

    def init_model(self):
        if not isinstance(self.config, OpenAILLMConfig):
            raise TypeError("config must be an instance of OpenAILLMConfig")
        config: OpenAILLMConfig = self.config
        self._client = self._init_client(config)
        self._default_ignore_fields = [
            "llm_type", "output_response", "openai_key", "deepseek_key", "anthropic_key", 
            "gemini_key", "meta_llama_key", "openrouter_key", "openrouter_base", "perplexity_key", 
            "groq_key"
        ] # parameters in OpenAILLMConfig that are not OpenAI models' input parameters 
        if self.config.model not in get_openai_model_cost():
            raise KeyError(f"'{self.config.model}' is not a valid OpenAI model name!")
    
    def _init_client(self, config: OpenAILLMConfig):
        print(f"[DEBUG] OpenAI client initialized with key: {str(config.openai_key)[:8]}..." if config.openai_key else "[DEBUG] OpenAI client initialized with key: None")
        client = OpenAI(api_key=config.openai_key)
        return client

    def formulate_messages(self, prompts: List[str], system_messages: Optional[List[str]] = None) -> List[List[dict]]:
        if system_messages is not None:
            assert len(prompts) == len(system_messages), f"the number of prompts ({len(prompts)}) is different from the number of system_messages ({len(system_messages)})"
        else:
            system_messages = ["" for _ in range(len(prompts))]
        messages_list = []
        for prompt, system_message in zip(prompts, system_messages):
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            messages_list.append(messages)
        return messages_list

    def update_completion_params(self, params1: dict, params2: dict) -> dict:
        config_params: list = self.config.get_config_params()
        for key, value in params2.items():
            if key in self._default_ignore_fields:
                continue
            if key not in config_params:
                continue
            params1[key] = value
        return params1

    def get_completion_params(self, **kwargs):
        completion_params = self.config.get_set_params(ignore=self._default_ignore_fields)
        completion_params = self.update_completion_params(completion_params, kwargs)
        return completion_params
    
    def get_stream_output(self, response: Stream, output_response: bool=True) -> str:
        """
        Process stream response and return the complete output.

        Args:
            response: The stream response from OpenAI
            output_response: Whether to print the response in real-time
            
        Returns:
            str: The complete output text
        """
        output = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                if output_response:
                    print(content, end="", flush=True)
                output += content
        if output_response:
            print("")
        return output or ""
    
    async def get_stream_output_async(self, response, output_response: bool = False) -> str:
        """
        Process async stream response and return the complete output.
        
        Args:
            response (AsyncIterator[ChatCompletionChunk]): The async stream response from OpenAI
            output_response (bool): Whether to print the response in real-time
            
            
        Returns:
            str: The complete output text
        """
        output = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                if output_response:
                    print(content, end="", flush=True)
                output += content
        if output_response:
            print("")
        return output

    def get_completion_output(self, response: ChatCompletion, output_response: bool=True) -> str:
        output = response.choices[0].message.content or ""
        if output_response:
            print(output)
        return output

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def single_generate(self, messages: List[dict], **kwargs) -> str:
        stream = kwargs["stream"] if "stream" in kwargs else getattr(self.config, "stream", False)
        output_response = kwargs["output_response"] if "output_response" in kwargs else getattr(self.config, "output_response", False)
        try:
            completion_params = self.get_completion_params(**kwargs)
            formatted_messages = [
                cast(ChatCompletionMessageParam, {"role": m["role"], "content": m["content"]})
                for m in messages if "role" in m and "content" in m
            ]
            response = self._client.chat.completions.create(messages=formatted_messages, **completion_params)
            if stream:
                output = self.get_stream_output(response, output_response=output_response)
                # Convert TypedDicts to dicts for downstream compatibility
                cost = self._stream_cost(messages=[dict(m) for m in formatted_messages], output=output)
            else:
                output: str = self.get_completion_output(response=response, output_response=output_response)
                cost = self._completion_cost(response)
            self._update_cost(cost=cost)
        except Exception as e:
            raise RuntimeError(f"Error during single_generate of OpenAILLM: {str(e)}")
        return output

    def batch_generate(self, batch_messages: List[List[dict]], **kwargs) -> List[str]:
        return [self.single_generate(messages=one_messages, **kwargs) for one_messages in batch_messages]

    async def single_generate_async(self, messages: List[dict], **kwargs) -> str:
        stream = kwargs.get("stream", getattr(self.config, "stream", False))
        output_response = kwargs.get("output_response", getattr(self.config, "output_response", False))
        try:
            config = self.config
            if not isinstance(config, OpenAILLMConfig):
                raise TypeError("config must be an instance of OpenAILLMConfig")
            isolated_client = self._init_client(config)
            completion_params = self.get_completion_params(**kwargs)
            formatted_messages = [
                cast(ChatCompletionMessageParam, {"role": m["role"], "content": m["content"]})
                for m in messages if "role" in m and "content" in m
            ]
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: isolated_client.chat.completions.create(
                    messages=formatted_messages,
                    **completion_params
                )
            )
            if stream:
                if hasattr(response, "__aiter__"):
                    output = await self.get_stream_output_async(response, output_response=output_response)
                else:
                    output = self.get_stream_output(response, output_response=output_response)
                # Convert TypedDicts to dicts for downstream compatibility
                cost = self._stream_cost(messages=[dict(m) for m in formatted_messages], output=output)
            else:
                output: str = self.get_completion_output(response=response, output_response=output_response)
                cost = self._completion_cost(response)
            self._update_cost(cost=cost)
        except Exception as e:
            raise RuntimeError(f"Error during single_generate_async of OpenAILLM: {str(e)}")
        return output

    def _completion_cost(self, response: ChatCompletion) -> Cost:
        input_tokens = getattr(response.usage, 'prompt_tokens', 0)
        output_tokens = getattr(response.usage, 'completion_tokens', 0)
        return self._compute_cost(input_tokens=input_tokens, output_tokens=output_tokens)

    def _stream_cost(self, messages: Sequence[dict], output: str) -> Cost:
        model: str = self.config.model
        # Ensure messages are plain dicts for token_counter
        input_tokens = token_counter(model=model, messages=list(messages))
        output_tokens = token_counter(model=model, text=output)
        return self._compute_cost(input_tokens=input_tokens, output_tokens=output_tokens)

    def _compute_cost(self, input_tokens: int, output_tokens: int) -> Cost:
        # use LiteLLM to compute cost, require the model name to be a valid model name in LiteLLM.
        input_cost, output_cost = cost_per_token(
            model=self.config.model, 
            prompt_tokens=input_tokens, 
            completion_tokens=output_tokens, 
        )
        cost = Cost(input_tokens=input_tokens, output_tokens=output_tokens, input_cost=input_cost, output_cost=output_cost)
        return cost
    
    def _update_cost(self, cost: Cost):
        cost_manager.update_cost(cost=cost, model=self.config.model)
