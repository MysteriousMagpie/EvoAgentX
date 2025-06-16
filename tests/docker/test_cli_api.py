import os
import pytest
from fastapi.testclient import TestClient
from server.main import app
from evoagentx import cli
from evoagentx.tools.interpreter_docker import DockerLimits

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")


def test_cli_run_node():
    out = cli.run("console.log(42)", runtime="node:20", timeout=10)
    assert "42" in out


def test_execute_endpoint():
    client = TestClient(app)
    resp = client.post("/execute", json={"code": "print('hi')", "runtime": "python:3.11"})
    assert resp.status_code == 200
    assert resp.json()["stdout"].strip() == "hi"
    assert resp.json()["exit_code"] == 0


def test_invalid_runtime():
    client = TestClient(app)
    resp = client.post("/execute", json={"code": "print(1)", "runtime": "ruby:3"})
    assert resp.status_code == 400
