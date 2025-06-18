import argparse
import sys
from .self_improve import self_improve
from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES


def run(argv=None):
    parser = argparse.ArgumentParser(prog="evoagentx.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute code in a Docker container")
    run_parser.add_argument("-c", "--code", required=True, help="Code to execute")
    run_parser.add_argument("--runtime", default="python:3.11", help="Execution runtime")
    run_parser.add_argument("--memory", default="512m", help="Memory limit")
    run_parser.add_argument("--cpus", default="1.0", help="CPU limit")
    run_parser.add_argument("--pids", default=64, type=int, help="PID limit")
    run_parser.add_argument("--timeout", default=20, type=int, help="Execution timeout")

    # Interactive self-improvement command
    improv_parser = subparsers.add_parser(
        "self-improve", help="Interactive self-improvement workflow"
    )
    improv_parser.add_argument(
        "--goal", help="Text goal for improvement (will prompt if omitted)"
    )
    improv_parser.add_argument(
        "--max-cycles", type=int, default=3, help="Max improvement iterations"
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        if args.runtime not in ALLOWED_RUNTIMES:
            raise ValueError(f"Invalid runtime '{args.runtime}'. Allowed: {list(ALLOWED_RUNTIMES)}")
        limits = DockerLimits(memory=args.memory, cpus=args.cpus, pids=args.pids, timeout=args.timeout)
        interpreter = DockerInterpreter(runtime=args.runtime, limits=limits, print_stdout=False, print_stderr=False)
        language = "node" if args.runtime.startswith("node") else "python"
        output = interpreter.execute(args.code, language)
        print(output)
        return output
    elif args.command == "self-improve":
        # Prompt for goal if not provided
        goal = args.goal or input("What would you like to improve? ")
        print(f"Starting self-improvement with goal: '{goal}'")
        # Run workflow interactively with simple updates
        decision = self_improve(goal, llm=None, max_cycles=args.max_cycles)
        print(f"Final decision: {decision}")
        sys.exit(0)


if __name__ == "__main__":
    run()
