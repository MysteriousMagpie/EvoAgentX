import os
import pytest
from evoagentx.tools.interpreter_docker import DockerInterpreter, DockerLimits

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")

def test_memory_limit():
    limits = DockerLimits(memory="128m", timeout=10)
    code = "a=[0]*25_000_000"  # ~200 MB in CPython
    with pytest.raises(RuntimeError, match="OOM"):
        DockerInterpreter(limits=limits, runtime="python:3.11", print_stdout=False, print_stderr=False).run(code)

