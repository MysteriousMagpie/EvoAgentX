import io
import shlex
import tarfile
import uuid
from dataclasses import dataclass
from threading import Thread
import time
import docker
from pathlib import Path
from typing import ClassVar, Dict, Any, List
from .interpreter_base import BaseInterpreter
import os
from pydantic import Field


@dataclass
class DockerLimits:
    """Resource limits for Docker containers."""

    memory: str = "512m"
    cpus: str = "1.0"
    pids: int = 64
    timeout: int = 20


ALLOWED_RUNTIMES = {
    "python:3.11": "python:3.11-slim",
    "node:20": "node:20-slim",
    "python:3.11-gpu": "nvidia/cuda:12.4.0-runtime-ubuntu22.04",
}

class DockerInterpreter(BaseInterpreter):
    """
    A Docker-based interpreter for executing Python, Bash, and R scripts in an isolated environment.
    """
    
    CODE_EXECUTE_CMD_MAPPING: ClassVar[Dict[str, str]] = {
        "python": "python {file_name}",
        "node": "node {file_name}",
    }

    CODE_TYPE_MAPPING: ClassVar[Dict[str, str]] = {
        "python": "python",
        "py3": "python",
        "python3": "python",
        "py": "python",
        "javascript": "node",
        "js": "node",
        "node": "node",
    }

    require_confirm: bool = Field(default=False, description="Whether to require confirmation before executing code")
    print_stdout: bool = Field(default=True, description="Whether to print stdout")
    print_stderr: bool = Field(default=True, description="Whether to print stderr")
    host_directory: str = Field(default="", description="The path to the host directory to use for the container")
    container_directory: str = Field(default="/home/app/", description="The directory to use for the container")
    container_command: str = Field(default="tail -f /dev/null", description="The command to use for the container")
    tmp_directory: str = Field(default="/tmp", description="The directory to use for the container")
    runtime: str = Field(default="python:3.11", description="The runtime environment to use")
    limits: DockerLimits = Field(default_factory=DockerLimits, description="Resource limits for the container")
    
    class Config:
        arbitrary_types_allowed = True  # Allow non-pydantic types like sets

    def __init__(
        self,
        name: str = "DockerInterpreter",
        runtime: str = "python:3.11",
        limits: DockerLimits | None = None,
        require_confirm: bool = False,
        print_stdout: bool = True,
        print_stderr: bool = True,
        host_directory: str = "",
        container_directory: str = "/home/app/",
        container_command: str = "tail -f /dev/null",
        tmp_directory: str = "/tmp",
        **data,
    ):
        """
        Initialize a Docker-based interpreter for executing code in an isolated environment.
        
        Args:
            name (str): The name of the interpreter
            runtime (str): The runtime to use. Must be one of ``ALLOWED_RUNTIMES``.
            limits (DockerLimits): Resource limits for the container
            require_confirm (bool): Whether to require confirmation before executing code
            print_stdout (bool): Whether to print stdout from code execution
            print_stderr (bool): Whether to print stderr from code execution
            host_directory (str): The path to the host directory to mount in the container
            container_directory (str): The target directory inside the container
            container_command (str): The command to run in the container
            tmp_directory (str): The temporary directory to use for file creation in the container
            **data: Additional data to pass to the parent class
        """
        # Extract or generate schemas, descriptions, tools
        schemas = data.pop('schemas', None) or self.get_tool_schemas()
        descriptions = data.pop('descriptions', None) or self.get_tool_descriptions()
        tools = data.pop('tools', None)
        tools = self.get_tools()
        
        # Pass these to the parent class initialization
        super().__init__(
            name=name,
            schemas=schemas,
            descriptions=descriptions,
            tools=tools,
            **data
        )
        self.require_confirm = require_confirm
        self.print_stdout = print_stdout
        self.print_stderr = print_stderr
        self.host_directory = host_directory
        self.container_directory = container_directory
        self.container_command = container_command
        self.tmp_directory = tmp_directory
        self.runtime = runtime
        self.limits = limits or DockerLimits()

        if self.runtime not in ALLOWED_RUNTIMES:
            raise ValueError(f"Unsupported runtime: {self.runtime}")

        # Initialize Docker client and container
        self.client = docker.from_env()
        self.container = None
        self.image_tag = ALLOWED_RUNTIMES[self.runtime]
        self._initialize_if_needed()
        
        # Upload directory if specified
        if self.host_directory:
            self._upload_directory_to_container(self.host_directory)

    def __del__(self):
        try:
            if hasattr(self, 'container') and self.container is not None:
                import sys
                if sys.meta_path is not None:  # Check if Python is shutting down
                    self.container.remove(force=True)
        except Exception:
            pass  # Silently ignore errors during shutdown

    def _initialize_if_needed(self):
        image_tag = self.image_tag
        try:
            self.client.images.get(image_tag)
        except docker.errors.ImageNotFound:
            # Pull image if not present locally
            self.client.images.pull(image_tag)
        except Exception as e:
            raise ValueError(f"Failed to fetch image {image_tag}: {e}")

        # Check if Docker daemon is running
        try:
            self.client.ping()
        except Exception as e:
            raise RuntimeError(f"Docker daemon is not running: {e}")

        # Run the container using the image with resource limits
        try:
            cpus = float(self.limits.cpus)
            if cpus <= 0:
                raise ValueError
        except Exception:
            raise ValueError(f"Invalid CPU limit: {self.limits.cpus}")

        self.container = self.client.containers.run(
            image_tag,
            detach=True,
            command=self.container_command,
            working_dir=self.container_directory,
            mem_limit=self.limits.memory,
            memswap_limit=self.limits.memory,
            nano_cpus=int(cpus * 1_000_000_000),
            pids_limit=self.limits.pids,
        )

    def _upload_directory_to_container(self, host_directory: str):
        """
        Uploads all files and directories from the given host directory to the container directory.

        :param host_directory: Path to the local directory containing files to upload.
        :param container_directory: Target directory inside the container (defaults to self.container_directory).
        """
        host_directory = Path(host_directory).resolve()
        if not host_directory.exists() or not host_directory.is_dir():
            raise FileNotFoundError(f"Directory not found: {host_directory}")

        tar_stream = io.BytesIO()
        
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            for file_path in host_directory.rglob("*"):
                if file_path.is_file():
                    # Ensure path is relative to the given directory
                    relative_path = file_path.relative_to(host_directory)
                    target_path = Path(self.container_directory) / relative_path
                    
                    tarinfo = tarfile.TarInfo(name=str(target_path.relative_to(self.container_directory)))
                    tarinfo.size = file_path.stat().st_size
                    with open(file_path, "rb") as f:
                        tar.addfile(tarinfo, f)

        tar_stream.seek(0)

        if self.container is None:
            raise RuntimeError("Container is not initialized.")

        self.container.put_archive(self.container_directory, tar_stream)

        # Ensure the uploaded directory is in sys.path for imports
        # self.container.exec_run(f"echo 'export PYTHONPATH={self.container_directory}:$PYTHONPATH' | sudo tee -a /etc/environment")

    def _create_file_in_container(self, content: str) -> Path:
        filename = str(uuid.uuid4())
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content.encode('utf-8'))
            tar.addfile(tarinfo, io.BytesIO(content.encode('utf-8')))
        tar_stream.seek(0)

        if self.container is None:
            raise RuntimeError("Container is not initialized.")
            
        try:
            self.container.put_archive(self.tmp_directory, tar_stream)
        except Exception as e:
            raise RuntimeError(f"Failed to create file in container: {e}")
            
        return Path(f"{self.tmp_directory}/{filename}")

    def _run_file_in_container(self, file: Path, language: str) -> dict:
        """Execute a file in the container with timeout and security checks.

        Returns a dict with execution details.
        """
        if not self.container:
            raise RuntimeError("Container is not initialized")
            
        # Check container status
        container_info = self.client.api.inspect_container(self.container.id)
        if not container_info['State']['Running']:
            raise RuntimeError("Container is not running")
            
        language = self._check_language(language)
        command = shlex.split(self.CODE_EXECUTE_CMD_MAPPING[language].format(file_name=file.as_posix()))
        if self.container is None:
            raise RuntimeError("Container is not initialized.")

        result_holder = {}
        start = time.time()

        def target():
            result_holder['res'] = self.container.exec_run(command, demux=True)

        thread = Thread(target=target)
        thread.start()
        thread.join(self.limits.timeout)
        if thread.is_alive():
            self.container.kill()
            thread.join()
            raise RuntimeError("Execution timed out")

        runtime = time.time() - start
        result = result_holder.get('res')

        stdout, stderr = result.output
        if self.print_stdout and stdout:
            print(stdout.decode())
        if self.print_stderr and stderr:
            print(stderr.decode())

        if result.exit_code != 0:
            if result.exit_code == 137:
                raise RuntimeError("Execution failed: OOM (memory limit exceeded)")
            raise RuntimeError(f"Execution failed with code {result.exit_code}")

        stdout_str = stdout.decode() if stdout else ""
        stderr_str = stderr.decode() if stderr else ""
        return {
            "stdout": stdout_str,
            "stderr": stderr_str,
            "exit_code": result.exit_code,
            "runtime_seconds": runtime,
        }

    def execute(self, code: str, language: str) -> str:
        """
        Executes code in a Docker container.
        
        Args:
            code (str): The code to execute
            language (str): The programming language to use
            
        Returns:
            str: The execution output
            
        Raises:
            RuntimeError: If container is not properly initialized or execution fails
            ValueError: If code content is invalid or exceeds limits
        """
        if not code or not code.strip():
            raise ValueError("Code content cannot be empty")
            
        if not self.container:
            raise RuntimeError("Container is not initialized")
            
        # Check container status
        try:
            container_info = self.client.api.inspect_container(self.container.id)
            if not container_info['State']['Running']:
                raise RuntimeError("Container is not running")
        except Exception as e:
            raise RuntimeError(f"Failed to check container status: {e}")

        if self.host_directory:
            code = f"import sys; sys.path.insert(0, '{self.container_directory}');" + code
            
        language = self._check_language(language)
        
        if self.require_confirm:
            confirmation = input(f"Confirm execution of {language} code? [Y/n]: ")
            if confirmation.lower() not in ["y", "yes", ""]:
                raise RuntimeError("Execution aborted by user.")
        
        try:
            file_path = self._create_file_in_container(code)
            result = self._run_file_in_container(file_path, language)
            return result["stdout"] + result["stderr"]
        except Exception as e:
            raise RuntimeError(f"Code execution failed: {e}")
        finally:
            # Clean up temporary files
            try:
                if hasattr(self, 'container') and self.container:
                    self.container.exec_run(f"rm -f {file_path}")
            except Exception:
                pass  # Ignore cleanup errors

    def execute_details(self, code: str, language: str) -> dict:
        """Execute code and return detailed results."""
        if not code or not code.strip():
            raise ValueError("Code content cannot be empty")
        if self.host_directory:
            code = f"import sys; sys.path.insert(0, '{self.container_directory}');" + code
        file_path = self._create_file_in_container(code)
        try:
            return self._run_file_in_container(file_path, language)
        finally:
            try:
                if hasattr(self, 'container') and self.container:
                    self.container.exec_run(f"rm -f {file_path}")
            except Exception:
                pass

    def run(self, code: str) -> str:
        """Convenience wrapper to execute Python code."""
        return self.execute(code, "python")

    def run_details(self, code: str) -> dict:
        """Convenience wrapper returning execution details for Python code."""
        return self.execute_details(code, "python")

    def execute_script(self, file_path: str, language: str = None) -> str:
        """
        Reads code from a file and executes it in a Docker container.
        
        Args:
            file_path (str): The path to the script file to execute
            language (str, optional): The programming language of the code. If None, will be determined from the file extension.
                                    
        Returns:
            str: The execution output
            
        Raises:
            FileNotFoundError: If the script file does not exist
            RuntimeError: If container is not properly initialized or execution fails
            ValueError: If file content is invalid or exceeds limits
        """
        # Check if file exists and is readable
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Script file not found: {file_path}")
            
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read script file: {file_path}")
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read script file: {e}")
            
        # Execute the code
        return self.execute(code, language)

    def _check_language(self, language: str) -> str:
        if language not in self.CODE_TYPE_MAPPING:
            raise ValueError(f"Unsupported language: {language}")
        return self.CODE_TYPE_MAPPING[language]

    def get_tool_schemas(self) -> list[Dict[str, Any]]:
        """
        Returns the OpenAI-compatible function schema for the Docker interpreter.
        
        Returns:
            list[Dict[str, Any]]: Function schema in OpenAI format
        """
        schemas = [
            {
                "type": "function",
                "function": {
                    "name": "execute",
                    "description": "Execute code in a secure Docker container environment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The code to execute"
                            },
                            "language": {
                                "type": "string",
                                "description": "The programming language of the code (e.g., python, py, python3)",
                                "enum": list(self.CODE_TYPE_MAPPING.keys())
                            }
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_script",
                    "description": "Execute code from a script file in a secure Docker container environment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the script file to execute"
                            },
                            "language": {
                                "type": "string",
                                "description": "The programming language of the code. If not provided, will be determined from file extension.",
                                "enum": list(self.CODE_TYPE_MAPPING.keys())
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            }
        ]
        return schemas
        
    def get_tool_descriptions(self) -> List[str]:
        """
        Returns a brief description of the Docker interpreter tool.
        
        Returns:
            List[str]: Tool description
        """
        return [
            "Execute code in a secure Docker container environment.",
            "Execute code from script files in a secure Docker container environment.",
            "Run Python code directly in the container."
        ]
        
    def get_tools(self) -> List[callable]:
        """
        Returns a list of callable methods provided by this tool.
        
        Returns:
            List[callable]: List of callable methods
        """
        return [self.execute, self.execute_script, self.run]
