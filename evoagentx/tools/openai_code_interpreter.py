"""
OpenAI Code Interpreter Tool Implementation
Integrates OpenAI's Code Interpreter via Assistants API
"""

import os
import time
import json
from typing import Dict, Any, List, Optional, Union
from openai import OpenAI
from pathlib import Path
import tempfile
import base64
from .interpreter_base import BaseInterpreter
from pydantic import Field


class OpenAICodeInterpreter(BaseInterpreter):
    """
    OpenAI Code Interpreter implementation using the Assistants API.
    Provides cloud-based code execution with file handling capabilities.
    """
    
    client: OpenAI = Field(default=None, description="OpenAI client instance")
    assistant_id: Optional[str] = Field(default=None, description="Assistant ID for code interpreter")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for conversation")
    model: str = Field(default="gpt-4-1106-preview", description="OpenAI model to use")
    
    def __init__(
        self,
        name: str = "OpenAICodeInterpreter",
        api_key: Optional[str] = None,
        model: str = "gpt-4-1106-preview",
        **data
    ):
        # Initialize schemas and tools
        schemas = data.pop('schemas', None) or self.get_tool_schemas()
        descriptions = data.pop('descriptions', None) or self.get_tool_descriptions()
        tools = data.pop('tools', None) or self.get_tools()
        
        super().__init__(
            name=name,
            schemas=schemas,
            descriptions=descriptions,
            tools=tools,
            **data
        )
        
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._initialize_assistant()

    def _initialize_assistant(self):
        """Initialize OpenAI Assistant with code interpreter tool."""
        try:
            # Create assistant with code interpreter capability
            assistant = self.client.beta.assistants.create(
                name="EvoAgentX Code Interpreter",
                instructions="""You are a code interpreter assistant integrated with EvoAgentX.
                Execute code requests and provide detailed analysis of results.
                Always explain your approach and any limitations or assumptions.""",
                model=self.model,
                tools=[{"type": "code_interpreter"}]
            )
            self.assistant_id = assistant.id
            
            # Create a new thread
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI Code Interpreter: {e}")

    def execute(self, code: str, language: str = "python") -> str:
        """
        Execute code using OpenAI's Code Interpreter.
        
        Args:
            code (str): The code to execute
            language (str): Programming language (currently supports python)
            
        Returns:
            str: Execution result with output and analysis
        """
        if language.lower() not in ["python", "py"]:
            return f"Error: OpenAI Code Interpreter currently only supports Python. Received: {language}"
        
        try:
            # Add message with code to execute
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=f"Execute this Python code and provide the output:\n\n```python\n{code}\n```"
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            return self._wait_for_completion(run.id)
            
        except Exception as e:
            return f"Error executing code: {str(e)}"

    def execute_with_files(self, code: str, files: List[str], language: str = "python") -> Dict[str, Any]:
        """
        Execute code with file uploads using OpenAI's Code Interpreter.
        
        Args:
            code (str): The code to execute
            files (List[str]): List of file paths to upload
            language (str): Programming language
            
        Returns:
            Dict[str, Any]: Execution result with files and output
        """
        if language.lower() not in ["python", "py"]:
            return {"error": f"OpenAI Code Interpreter currently only supports Python. Received: {language}"}
        
        try:
            # Upload files
            file_ids = []
            for file_path in files:
                if not os.path.exists(file_path):
                    return {"error": f"File not found: {file_path}"}
                    
                with open(file_path, "rb") as f:
                    file_obj = self.client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                    file_ids.append(file_obj.id)
            
            # Create message with files
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=f"Execute this Python code with the uploaded files:\n\n```python\n{code}\n```",
                file_ids=file_ids
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion and get results
            result = self._wait_for_completion(run.id)
            
            # Get any generated files
            generated_files = self._get_generated_files(run.id)
            
            return {
                "output": result,
                "generated_files": generated_files,
                "uploaded_file_ids": file_ids
            }
            
        except Exception as e:
            return {"error": f"Error executing code with files: {str(e)}"}

    def _wait_for_completion(self, run_id: str, timeout: int = 300) -> str:
        """Wait for run completion and return the result."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run_id
            )
            
            if run.status == "completed":
                # Get the latest message
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread_id,
                    order="desc",
                    limit=1
                )
                
                if messages.data:
                    return self._format_message_content(messages.data[0])
                else:
                    return "No response received"
                    
            elif run.status in ["failed", "cancelled", "expired"]:
                return f"Run {run.status}: {run.last_error.message if run.last_error else 'Unknown error'}"
            
            time.sleep(2)
        
        return "Timeout: Code execution took too long"

    def _format_message_content(self, message) -> str:
        """Format the assistant's response message."""
        content_parts = []
        
        for content in message.content:
            if content.type == "text":
                content_parts.append(content.text.value)
            elif content.type == "image_file":
                content_parts.append(f"[Generated image: {content.image_file.file_id}]")
        
        return "\n".join(content_parts)

    def _get_generated_files(self, run_id: str) -> List[Dict[str, str]]:
        """Get any files generated during code execution."""
        try:
            # Get run steps to find generated files
            run_steps = self.client.beta.threads.runs.steps.list(
                thread_id=self.thread_id,
                run_id=run_id
            )
            
            generated_files = []
            for step in run_steps.data:
                if hasattr(step, 'step_details') and hasattr(step.step_details, 'tool_calls'):
                    for tool_call in step.step_details.tool_calls:
                        if tool_call.type == "code_interpreter" and tool_call.code_interpreter.outputs:
                            for output in tool_call.code_interpreter.outputs:
                                if output.type == "image":
                                    generated_files.append({
                                        "type": "image",
                                        "file_id": output.image.file_id,
                                        "description": "Generated image"
                                    })
            
            return generated_files
            
        except Exception as e:
            return [{"error": f"Failed to retrieve generated files: {str(e)}"}]

    def download_file(self, file_id: str, save_path: str) -> str:
        """Download a file generated by the code interpreter."""
        try:
            file_content = self.client.files.content(file_id)
            
            with open(save_path, "wb") as f:
                f.write(file_content.content)
            
            return f"File downloaded successfully to: {save_path}"
            
        except Exception as e:
            return f"Error downloading file: {str(e)}"

    def cleanup(self):
        """Clean up resources (delete assistant and thread)."""
        try:
            if self.thread_id:
                self.client.beta.threads.delete(self.thread_id)
            if self.assistant_id:
                self.client.beta.assistants.delete(self.assistant_id)
        except Exception as e:
            print(f"Warning: Failed to cleanup resources: {e}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible function schemas."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute",
                    "description": "Execute Python code using OpenAI's Code Interpreter with cloud-based execution and file handling.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Python code to execute"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (currently only 'python' supported)",
                                "enum": ["python", "py"]
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_with_files",
                    "description": "Execute Python code with file uploads using OpenAI's Code Interpreter.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Python code to execute"
                            },
                            "files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to upload and use in code execution"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (currently only 'python' supported)",
                                "enum": ["python", "py"]
                            }
                        },
                        "required": ["code", "files"]
                    }
                }
            }
        ]

    def get_tool_descriptions(self) -> List[str]:
        """Return tool descriptions."""
        return [
            "Execute Python code using OpenAI's Code Interpreter with cloud-based execution",
            "Execute Python code with file uploads using OpenAI's Code Interpreter"
        ]

    def get_tools(self) -> List[callable]:
        """Return callable tools."""
        return [self.execute, self.execute_with_files]

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cleanup()
        except:
            pass
