import pytest
from evoagentx.optimizers import get_optimizer, list_optimizers


def test_registry_lists_and_loads():
    names = set(list_optimizers())
    assert {"textgrad", "sew", "random_search"}.issubset(names)

    opt = get_optimizer("random_search", iterations=10, sampler=lambda: 0.5)
    result = opt.optimize(lambda x: x**2)
    assert result == 0.5
