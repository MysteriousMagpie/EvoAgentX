import os
import pytest
from evoagentx.tools.interpreter_docker import DockerInterpreter, DockerLimits

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")

def test_memory_limit():
    limits = DockerLimits(memory="50m", timeout=10)
    interpreter = DockerInterpreter(runtime="python:3.11", limits=limits, print_stdout=False, print_stderr=False)
    with pytest.raises(RuntimeError):
        interpreter.execute("a=[0]*10_000_000", "python")

