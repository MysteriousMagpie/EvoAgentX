import argparse
import sys
from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES


def _determine_language(runtime: str) -> str:
    if runtime.startswith("node"):
        return "node"
    return "python"


def run_command(args: argparse.Namespace) -> None:
    limits = DockerLimits(memory=args.memory, cpus=args.cpus, pids=args.pids, timeout=args.timeout)
    interpreter = DockerInterpreter(runtime=args.runtime, limits=limits, print_stdout=False, print_stderr=False)
    lang = _determine_language(args.runtime)
    result = interpreter.execute_details(args.code, lang)
    sys.stdout.write(result["stdout"])
    sys.stderr.write(result["stderr"])


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="evoagentx")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Execute code in Docker")
    run_p.add_argument("-c", "--code", required=True, help="Code snippet to execute")
    run_p.add_argument("--runtime", default="python:3.11", choices=list(ALLOWED_RUNTIMES.keys()), help="Runtime image")
    run_p.add_argument("--memory", default="512m")
    run_p.add_argument("--cpus", default="1.0")
    run_p.add_argument("--pids", type=int, default=64)
    run_p.add_argument("--timeout", type=int, default=20)
    run_p.set_defaults(func=run_command)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
