import os
import pytest
from evoagentx.tools.interpreter_docker import DockerInterpreter, DockerLimits

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")

def test_runtime_choice_node():
    interpreter = DockerInterpreter(runtime="node:20", limits=DockerLimits(timeout=10), print_stdout=False, print_stderr=False)
    output = interpreter.execute('console.log(42)', 'node')
    assert '42' in output

