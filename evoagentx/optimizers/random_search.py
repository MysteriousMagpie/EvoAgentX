import random
from typing import Callable, Tuple

from . import register_optimizer, Optimizer as BaseOptimizer


@register_optimizer("random_search")
class RandomSearchOptimizer(BaseOptimizer):
    """Simple random search optimizer for continuous bounds."""

    def __init__(self, bounds: Tuple[float, float], iterations: int = 100, rng: random.Random | None = None):
        self.bounds = bounds
        self.iterations = iterations
        self.rng = rng or random.Random()

    def optimize(self, objective: Callable[[float], float], **kwargs) -> float:
        """Return the best candidate found by random search."""
        low, high = self.bounds
        best_x = None
        best_score = float("-inf")
        for _ in range(self.iterations):
            x = self.rng.uniform(low, high)
            score = objective(x)
            if score > best_score:
                best_score = score
                best_x = x
        return best_x
