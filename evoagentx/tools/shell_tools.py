import subprocess, shlex, os, textwrap, json, tempfile, pathlib

SAFE_CMDS = {"pytest", "ruff", "npm", "pnpm", "git", "echo"}

def run(cmd: str, timeout: int = 60) -> str:
    """Run shell commands *inside* repo, allow-listed only."""
    head = shlex.split(cmd)[0]
    if head not in SAFE_CMDS:
        raise ValueError(f"Command {head} not allowed")
    proc = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return textwrap.dedent(f"""
        exit_code: {proc.returncode}
        stdout:
        {proc.stdout}
        stderr:
        {proc.stderr}
    """)
