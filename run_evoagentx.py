from evoagentx.core.runner import run_workflow_async as run_workflow


def main():
    """Generate and execute a workflow based on a user provided goal."""
    goal = input("Enter the goal for EvoAgentX: ").strip()
    output = run_workflow(goal)
    print(output)


if __name__ == "__main__":
    main()
