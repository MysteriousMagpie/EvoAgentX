import argparse
from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES


def run(code: str, runtime: str = "python:3.11", memory: str | None = None,
        cpus: str | None = None, pids: int | None = None, timeout: int | None = None) -> str:
    limits = DockerLimits(
        memory=memory or DockerLimits.memory,
        cpus=cpus or DockerLimits.cpus,
        pids=pids if pids is not None else DockerLimits.pids,
        timeout=timeout if timeout is not None else DockerLimits.timeout,
    )
    interpreter = DockerInterpreter(runtime=runtime, limits=limits, print_stdout=False, print_stderr=False)
    language = "node" if runtime.startswith("node") else "python"
    return interpreter.execute(code, language)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="evoagentx.cli")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Execute code in Docker")
    run_p.add_argument("-c", "--code", required=True)
    run_p.add_argument("--runtime", default="python:3.11", choices=list(ALLOWED_RUNTIMES.keys()))
    run_p.add_argument("--memory")
    run_p.add_argument("--cpus")
    run_p.add_argument("--pids", type=int)
    run_p.add_argument("--timeout", type=int)

    args = parser.parse_args(argv)

    if args.command == "run":
        output = run(args.code, args.runtime, args.memory, args.cpus, args.pids, args.timeout)
        print(output)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
