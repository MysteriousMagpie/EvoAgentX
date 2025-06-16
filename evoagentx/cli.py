import argparse
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


if __name__ == "__main__":
    run()
