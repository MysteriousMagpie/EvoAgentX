from evoagentx.tools.fs_tools import FileTools
from evoagentx.tools.shell_tools import run as shell_run
from evoagentx.agents.agent_manager import AgentManager

# Register file and shell tools for agent use
AgentManager.add_tool("file.read", FileTools.read)
AgentManager.add_tool("file.write", FileTools.write)
AgentManager.add_tool("file.append", FileTools.append)
AgentManager.add_tool("shell.run", shell_run)
