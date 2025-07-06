import argparse
import sys
from .self_improve import self_improve
from .tools.interpreter_docker import DockerInterpreter, DockerLimits, ALLOWED_RUNTIMES
from .tools.intelligent_interpreter_selector import execute_smart
from .tools.openai_code_interpreter import OpenAICodeInterpreter


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

    # Smart execution command
    smart_parser = subparsers.add_parser("run-smart", help="Execute code with intelligent interpreter selection")
    smart_parser.add_argument("-c", "--code", required=True, help="Code to execute")
    smart_parser.add_argument("--language", default="python", help="Programming language")
    smart_parser.add_argument("--interpreter", default="auto", choices=["auto", "python", "docker", "openai"], 
                             help="Interpreter to use (auto for intelligent selection)")
    smart_parser.add_argument("--security", default="medium", choices=["low", "medium", "high"],
                             help="Security level requirement")
    smart_parser.add_argument("--budget", type=float, help="Budget limit for cloud execution (USD)")
    smart_parser.add_argument("--files", nargs="*", help="Files to include in execution")
    smart_parser.add_argument("--viz", action="store_true", help="Code requires visualization")
    smart_parser.add_argument("--performance", action="store_true", help="Prioritize performance over features")

    # OpenAI Code Interpreter command
    openai_parser = subparsers.add_parser("run-openai", help="Execute code using OpenAI Code Interpreter")
    openai_parser.add_argument("-c", "--code", required=True, help="Code to execute")
    openai_parser.add_argument("--language", default="python", help="Programming language")
    openai_parser.add_argument("--files", nargs="*", help="Files to upload and use")
    openai_parser.add_argument("--model", default="gpt-4-1106-preview", help="OpenAI model to use")

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
    elif args.command == "run-smart":
        # Smart execution with intelligent interpreter selection
        try:
            result = execute_smart(
                code=args.code,
                language=args.language,
                security_level=args.security,
                budget_limit=args.budget,
                files=args.files,
                visualization_needed=args.viz,
                performance_priority=args.performance
            )
            
            print(f"Interpreter used: {result['interpreter_used']}")
            if result['estimated_cost'] > 0:
                print(f"Estimated cost: ${result['estimated_cost']:.4f}")
            print(f"Success: {result['success']}")
            if not result['success'] and result.get('error'):
                print(f"Error: {result['error']}")
            print("\nOutput:")
            print(result['output'])
            return result['output']
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
            
    elif args.command == "run-openai":
        # OpenAI Code Interpreter execution
        openai_interpreter = None
        try:
            openai_interpreter = OpenAICodeInterpreter(model=args.model)
            
            if args.files:
                # Execute with files
                result = openai_interpreter.execute_with_files(args.code, args.files, args.language)
                print("Output:")
                print(result.get('output', ''))
                if result.get('generated_files'):
                    print(f"\nGenerated files: {len(result['generated_files'])}")
                    for file_info in result['generated_files']:
                        print(f"  - {file_info}")
                if result.get('error'):
                    print(f"Error: {result['error']}")
                return result
            else:
                # Simple execution
                output = openai_interpreter.execute(args.code, args.language)
                print("Output:")
                print(output)
                return output
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            # Cleanup
            try:
                if openai_interpreter:
                    openai_interpreter.cleanup()
            except:
                pass
                
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
