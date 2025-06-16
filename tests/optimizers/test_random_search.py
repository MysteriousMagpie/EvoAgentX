import math
from evoagentx.optimizers.random_search import RandomSearchOptimizer


def test_random_search_finds_near_optimum():
    optimizer = RandomSearchOptimizer(bounds=(0, 10), iterations=500, rng=None)
    result = optimizer.optimize(lambda x: -(x - 3) ** 2)
    assert math.isclose(result, 3, abs_tol=0.5)
