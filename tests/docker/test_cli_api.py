import os
import pytest
from fastapi.testclient import TestClient

from evoagentx import cli
from evoagentx.api import app
from evoagentx.tools.interpreter_docker import DockerLimits

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")


def test_cli_node(capsys):
    exit_code = cli.main(["run", "--runtime", "node:20", "--timeout", "10", "-c", "console.log(42)"])
    captured = capsys.readouterr()
    assert "42" in captured.out
    assert exit_code == 0


def test_api_execute():
    client = TestClient(app)
    resp = client.post("/execute", json={"code": "print('hi')"})
    assert resp.status_code == 200
    assert resp.json()["stdout"].strip() == "hi"
