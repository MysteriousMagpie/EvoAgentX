import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
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
        self.log = []  # Conversation log

    async def run(self):
        console.print(Panel("Welcome to [bold green]EvoAgentX interactive self-improve![/]", style="bold green"))
        goal = console.input("[bold cyan]What would you like to improve today?[/] ")
        self.log.append(("user", goal))
        console.print(f"\n[italic]OK, goal:[/] {goal}\n", style="cyan")
        wf = generate_self_improve_workflow(goal, self.llm)
        console.print(Markdown("### Workflow:"))
        console.print(Markdown(f"```\n{wf.get_workflow_description()}\n```"))

        decision = "retry"
        cycle = 0
        while cycle < self.max_cycles and decision == "retry":
            cycle += 1
            console.rule(f"[bold magenta]Cycle {cycle}")
            # 1) Code search
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[yellow]Searching code...", total=None)
                result = self.agents[0].act(goal)
            console.print(Panel(f"[bold yellow]Search result:[/]\n{result}", style="yellow"))
            self.log.append(("agent", f"Search result: {result}"))
            if console.input("→ [bold]Proceed with this search? (y/n)[/] ") != "y":
                goal = console.input("Okay, refine your search goal: ")
                self.log.append(("user", goal))
                continue
            # 2) Refactor
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[yellow]Refactoring...", total=None)
                patch = self.agents[1].act("code.py", result)
            console.print(Panel(f"[bold yellow]Proposed patch:[/]\n[white]{patch}", style="yellow"))
            self.log.append(("agent", f"Proposed patch: {patch}"))
            if console.input("→ [bold]Apply this patch? (y/n)[/] ") != "y":
                console.print("[red]Skipping refactor this cycle.[/]")
                continue
            # 3) Test
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[yellow]Running tests...", total=None)
                test_out = self.agents[2].act()
            table = Table(title="Test Output", show_header=False)
            table.add_row(test_out)
            console.print(table)
            self.log.append(("agent", f"Test output: {test_out}"))
            # 4) Critic
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[yellow]Critiquing...", total=None)
                critique = self.agents[3].act("diff", test_out)
            console.print(Panel(f"[bold yellow]Critic feedback:[/]\n[white]{critique}", style="yellow"))
            self.log.append(("agent", f"Critic feedback: {critique}"))
            try:
                import json
                decision = json.loads(critique).get("decision", "retry")
            except:
                decision = "retry"
            console.print(f"Decision: [bold]{decision}[/]\n", style="bold")
            # Show summary for this cycle
            console.print(Panel(f"[bold magenta]Cycle {cycle} Summary:[/]\nSearch → Refactor → Test → Critic complete.", style="magenta"))
        # 5) Publish
        if decision == "accept":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[green]Publishing final branch…", total=None)
                self.agents[4].act("self-improve-branch-id")
            console.print("[bold green]Done.[/] Final decision: accept")
        else:
            console.print("[bold red]Done.[/] Final decision: retry or max cycles reached.")
        # Show conversation log at end
        console.print(Panel("[bold blue]Conversation Log:[/]", style="blue"))
        for speaker, msg in self.log:
            if speaker == "user":
                console.print(f"[bold cyan]You:[/] {msg}")
            else:
                console.print(f"[bold yellow]Agent:[/] {msg}")

if __name__ == "__main__":
    # Replace with your LLM client as needed
    llm = None
    asyncio.run(InteractiveSelfImprove(llm).run())
