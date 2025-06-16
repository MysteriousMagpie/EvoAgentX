import argparse
from typing import Callable, Any
from .logging import logger
from ..optimizers import get_optimizer, list_optimizers


def run(objective: Callable[[Any], float], optimizer: str = "textgrad", **optimizer_params):
    """Run optimization with the requested optimizer."""
    try:
        opt = get_optimizer(optimizer, **optimizer_params)
    except ValueError:
        print(f"Unknown optimizer '{optimizer}'. Valid options: {list_optimizers()}")
        raise
    return opt.optimize(objective)


def main():
    parser = argparse.ArgumentParser(description="Run optimization with a selected optimizer")
    parser.add_argument("--optimizer", default="textgrad", help="Optimizer name")
    args = parser.parse_args()

    def objective(x):
        return x ** 2

    result = run(objective, optimizer=args.optimizer)
    logger.info(f"Optimization result: {result}")


if __name__ == "__main__":
    main()
