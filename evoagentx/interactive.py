import asyncio
from rich.console import Console
from rich.markdown import Markdown
from evoagentx.self_improve import generate_self_improve_workflow
from evoagentx.agents.meta_agents import (
    CodeSearchAgent, RefactorAgent, TestAgent, CriticAgent, PRAgent
)

console = Console()

class InteractiveSelfImprove:
    def __init__(self, llm, max_cycles=5):
        self.llm = llm
        self.max_cycles = max_cycles
        self.agents = [
            CodeSearchAgent(),
            RefactorAgent(),
            TestAgent(),
            CriticAgent(),
            PRAgent(),
        ]

    async def run(self):
        console.print("[bold green]Welcome to EvoAgentX interactive self-improve![/]\n")
        goal = console.input("[bold]What would you like to improve today?[/] ")
        console.print(f"\n[italic]OK, goal:[/] {goal}\n")
        wf = generate_self_improve_workflow(goal, self.llm)
        console.print(Markdown("### Workflow:"))
        console.print(Markdown(f"```\n{wf.get_workflow_description()}\n```"))

        decision = "retry"
        cycle = 0
        while cycle < self.max_cycles and decision == "retry":
            cycle += 1
            console.rule(f"Cycle {cycle}")
            # 1) Code search
            console.print("[yellow]Searching code...[/]")
            result = self.agents[0].act(goal)
            console.print(Markdown(f"**Search result**\n```\n{result}\n```"))
            if console.input("→ [bold]Proceed with this search? (y/n)[/] ") != "y":
                goal = console.input("Okay, refine your search goal: ")
                continue
            # 2) Refactor
            console.print("[yellow]Refactoring...[/]")
            patch = self.agents[1].act("code.py", result)
            console.print(Markdown(f"**Proposed patch**\n```diff\n{patch}\n```"))
            if console.input("→ [bold]Apply this patch? (y/n)[/] ") != "y":
                console.print("Skipping refactor this cycle.")
                continue
            # 3) Test
            console.print("[yellow]Running tests...[/]")
            test_out = self.agents[2].act()
            console.print(Markdown(f"**Test output**\n```\n{test_out}\n```"))
            # 4) Critic
            console.print("[yellow]Critiquing...[/]")
            critique = self.agents[3].act("diff", test_out)
            console.print(Markdown(f"**Critic feedback**\n```\n{critique}\n```"))
            try:
                import json
                decision = json.loads(critique).get("decision", "retry")
            except:
                decision = "retry"
            console.print(f"Decision: [bold]{decision}[/]\n")
        # 5) Publish
        if decision == "accept":
            console.print("[green]Publishing final branch…[/]")
            self.agents[4].act("self-improve-branch-id")
        console.print(f"[bold]Done.[/] Final decision: {decision}")

if __name__ == "__main__":
    # Replace with your LLM client as needed
    llm = None
    asyncio.run(InteractiveSelfImprove(llm).run())
