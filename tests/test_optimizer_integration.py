import pytest
from evoagentx.core.optimization_runner import run
from evoagentx.optimizers import Optimizer, _optimizers


class DummyOptimizer(Optimizer):
    def __init__(self, value=42):
        self.value = value

    def optimize(self, objective, **kwargs):
        return self.value


@pytest.fixture(autouse=True)
def patch_registry(monkeypatch):
    monkeypatch.setitem(_optimizers, "textgrad", DummyOptimizer)
    monkeypatch.setitem(_optimizers, "sew", DummyOptimizer)
    yield
    _optimizers.pop("textgrad", None)
    _optimizers.pop("sew", None)


@pytest.mark.parametrize("name,expected", [
    ("textgrad", 42),
    ("sew", 42),
    ("random_search", 0.5),
])
def test_optimizer_integration(name, expected):
    if name == "random_search":
        result = run(lambda x: x**2, optimizer=name, iterations=1, sampler=lambda: 0.5)
    else:
        result = run(lambda x: x**2, optimizer=name, value=42)
    assert result == expected
