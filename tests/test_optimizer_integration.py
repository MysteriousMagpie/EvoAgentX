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
        class ConstantRandom:
            def uniform(self, _a: float, _b: float) -> float:  # pragma: no cover - simple stub
                return 0.5

        result = run(lambda x: x**2, optimizer=name, bounds=(0, 1), iterations=1, rng=ConstantRandom())
    else:
        result = run(lambda x: x**2, optimizer=name, value=42)
    assert result == expected
