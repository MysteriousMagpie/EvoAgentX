import argparse
import sys
from evoagentx.tools.interpreter_docker import (
    DockerInterpreter,
    DockerLimits,
    ALLOWED_RUNTIMES,
)


def _run_code(code: str, runtime: str, limits: DockerLimits):
    if runtime not in ALLOWED_RUNTIMES:
        raise ValueError(f"Invalid runtime: {runtime}")
    interp = DockerInterpreter(runtime=runtime, limits=limits, print_stdout=False, print_stderr=False)
    lang = "node" if runtime.startswith("node") else "python"
    res = interp.execute_verbose(code, lang)
    print(res.stdout, end="")
    if res.stderr:
        print(res.stderr, file=sys.stderr, end="")
    return res.exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(prog="evoagentx.cli")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Execute code in Docker")
    run_p.add_argument("-c", "--code", required=True, help="Code snippet to run")
    run_p.add_argument("--runtime", default="python:3.11", help="Runtime to use")
    run_p.add_argument("--memory", default="512m")
    run_p.add_argument("--cpus", default="1.0")
    run_p.add_argument("--pids", type=int, default=64)
    run_p.add_argument("--timeout", type=int, default=20)

    args = parser.parse_args(argv)

    if args.command == "run":
        limits = DockerLimits(memory=args.memory, cpus=args.cpus, pids=args.pids, timeout=args.timeout)
        return _run_code(args.code, args.runtime, limits)
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation
    sys.exit(main())
