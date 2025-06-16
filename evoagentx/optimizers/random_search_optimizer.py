import random
from . import register_optimizer, Optimizer


@register_optimizer("random_search")
class RandomSearchOptimizer(Optimizer):
    def __init__(self, iterations: int = 100, sampler=None):
        self.iterations = iterations
        self.sampler = sampler or (lambda: random.random())

    def optimize(self, objective, **kwargs):
        best = None
        best_score = float("inf")
        for _ in range(self.iterations):
            candidate = self.sampler()
            score = objective(candidate)
            if score < best_score:
                best_score, best = score, candidate
        return best
