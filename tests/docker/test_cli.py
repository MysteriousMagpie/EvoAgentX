import os
import pytest
from evoagentx import cli

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")

def test_cli_run_python(capsys):
    out = cli.run(["run", "-c", "print('hi')"])
    assert "hi" in out

def test_cli_run_node(capsys):
    out = cli.run(["run", "--runtime", "node:20", "-c", "console.log(42)"])
    assert "42" in out
