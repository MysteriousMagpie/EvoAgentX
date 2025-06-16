import os
import pytest
from evoagentx import cli
from evoagentx.api import app
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")


def test_cli_python(capsys):
    cli.main(["run", "-c", "print('hi')"])
    captured = capsys.readouterr()
    assert "hi" in captured.out


def test_cli_node(capsys):
    cli.main(["run", "--runtime", "node:20", "-c", "console.log(42)"])
    captured = capsys.readouterr()
    assert "42" in captured.out


def test_api_execute():
    client = TestClient(app)
    resp = client.post("/execute", json={"code": "print('hi')"})
    assert resp.status_code == 200
    assert "hi" in resp.json()["stdout"]


def test_api_invalid_runtime():
    client = TestClient(app)
    resp = client.post("/execute", json={"code": "print('hi')", "runtime": "ruby"})
    assert resp.status_code == 400

