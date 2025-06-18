from evoagentx.agents.agent import Agent
from evoagentx.agents.agent_manager import AgentManager

# Meta-Agents for self-improvement workflow

class CodeSearchAgent(Agent):
    name: str = "CodeSearchAgent"
    description: str = "Given a regex or string, list files & line numbers."
    def act(self, query: str) -> str:
        return AgentManager.toolbox["shell.run"](f"grep -Rn {query} .")

class RefactorAgent(Agent):
    name: str = "RefactorAgent"
    description: str = "Edit these files to satisfy the task."
    def act(self, path: str, content: str) -> str:
        AgentManager.toolbox["file.write"](path, content)
        return f"Refactored {path}"

class TestAgent(Agent):
    name: str = "TestAgent"
    description: str = "Run tests & linters, return summary."
    def act(self) -> str:
        return AgentManager.toolbox["shell.run"]("pytest -q && ruff check .")

class CriticAgent(Agent):
    name: str = "CriticAgent"
    description: str = "Read diff + test output. Decide: accept / retry."
    def act(self, diff: str, test_output: str) -> str:
        """Score the result and decide accept/retry per heuristic."""
        score = 0
        feedback = []
        # 1. All tests & linters pass → +5
        if "exit_code: 0" in test_output and "failed" not in test_output.lower():
            score += 5
        else:
            feedback.append("Tests or linters failed.")
        # 2. Diff is non-empty & relevant → +3
        if diff.strip() and "diff" not in diff.lower():
            score += 3
        else:
            feedback.append("Diff is empty or not relevant.")
        # 3. No new TODO / FIXME → +2
        if "TODO" not in diff and "FIXME" not in diff:
            score += 2
        else:
            feedback.append("New TODO or FIXME found.")
        if score >= 8:
            return '{"decision": "accept"}'
        else:
            return '{"decision": "retry", "feedback": "%s"}' % " ".join(feedback)

class PRAgent(Agent):
    name: str = "PRAgent"
    description: str = "Commit & push branch 'self-improve-{hash}'."
    def act(self, branch: str) -> str:
        return AgentManager.toolbox["shell.run"](f"git add . && git commit -m 'self-improve' && git push origin {branch}")
