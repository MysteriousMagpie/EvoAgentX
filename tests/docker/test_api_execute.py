import os
import pytest
from fastapi.testclient import TestClient
from evoagentx.api import app

pytestmark = pytest.mark.skipif(os.environ.get("RUN_DOCKER_TESTS") != "true", reason="Docker tests disabled")

client = TestClient(app)

def test_execute_python():
    res = client.post("/execute", json={"code": "print('hi')"})
    assert res.status_code == 200
    assert "hi" in res.json()["stdout"]


def test_execute_invalid_runtime():
    res = client.post("/execute", json={"code": "print('hi')", "runtime": "bad"})
    assert res.status_code == 400
