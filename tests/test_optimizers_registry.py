from evoagentx.optimizers import get_optimizer, list_optimizers


def test_registry_lists_and_loads():
    names = set(list_optimizers())
    assert {"textgrad", "sew", "random_search"}.issubset(names)

    class ConstantRandom:
        def __init__(self, value: float):
            self.value = value

        def uniform(self, _a: float, _b: float) -> float:  # pragma: no cover - simple stub
            return self.value

    opt = get_optimizer("random_search", bounds=(0, 1), iterations=10, rng=ConstantRandom(0.5))
    result = opt.optimize(lambda x: x**2)
    assert result == 0.5
