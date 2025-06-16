from abc import ABC
from typing import Callable, Any, Dict, Type

_optimizers: Dict[str, Type["Optimizer"]] = {}


def register_optimizer(name: str):
    """Decorator to register an Optimizer subclass under a given name."""

    def decorator(cls: Type["Optimizer"]):
        _optimizers[name] = cls
        return cls

    return decorator


def get_optimizer(name: str, **kwargs) -> "Optimizer":
    """Instantiate the optimizer registered under `name`."""
    if name not in _optimizers:
        raise ValueError(f"No optimizer registered under '{name}'")
    return _optimizers[name](**kwargs)


def list_optimizers() -> list[str]:
    """List all registered optimizer names."""
    return list(_optimizers.keys())


class Optimizer(ABC):
    """Base class for all optimizers."""

    def optimize(self, objective: Callable[[Any], float], **kwargs) -> Any:
        raise NotImplementedError


# Import optimizers to ensure they are registered on package import
try:
    from .textgrad_optimizer import TextGradOptimizer
except Exception:  # pragma: no cover - optional dependency
    @register_optimizer("textgrad")
    class TextGradOptimizer(Optimizer):
        def optimize(self, *args, **kwargs):  # pragma: no cover - stub
            raise ImportError("TextGradOptimizer dependencies are missing")

try:
    from .sew_optimizer import SEWOptimizer
except Exception:  # pragma: no cover - optional dependency
    @register_optimizer("sew")
    class SEWOptimizer(Optimizer):
        def optimize(self, *args, **kwargs):  # pragma: no cover - stub
            raise ImportError("SEWOptimizer dependencies are missing")

from .random_search_optimizer import RandomSearchOptimizer

__all__ = [
    "SEWOptimizer",
    "TextGradOptimizer",
    "RandomSearchOptimizer",
    "register_optimizer",
    "get_optimizer",
    "list_optimizers",
    "Optimizer",
]
