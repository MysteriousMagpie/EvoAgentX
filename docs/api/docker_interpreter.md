# DockerInterpreter

`DockerInterpreter` executes user code inside Docker containers with resource limits.

## Usage
```python
from evoagentx.tools.interpreter_docker import DockerInterpreter, DockerLimits

limits = DockerLimits(memory="256m", cpus="0.5", timeout=10)
interpreter = DockerInterpreter(runtime="python:3.11", limits=limits)
print(interpreter.execute("print('hello')", "python"))
```

## Limit Fields
- `memory`: Docker memory limit (default `512m`)
- `cpus`: CPU cores allowed (default `1.0`)
- `pids`: Maximum process count (default `64`)
- `timeout`: Host-side timeout in seconds (default `20`)

## Allowed Runtimes
- `python:3.11` → `python:3.11-slim`
- `node:20` → `node:20-slim`
- `python:3.11-gpu` → `nvidia/cuda:12.4.0-runtime-ubuntu22.04`

Use the `runtime` argument when creating the interpreter. Unsupported values raise `ValueError`.

GPU images require a Docker setup with GPU support.

When running on cgroup-v2 systems (e.g. GitHub Actions), Docker only enforces
`--memory` if `--memory-swap` is also set. The interpreter sets this value equal
to the memory limit to ensure an OOM kill when the cap is exceeded.

### CLI Example

Run a Node snippet with custom limits:

```bash
python -m evoagentx.cli run --runtime node:20 --memory 512m --cpus 1 --timeout 15 -c "console.log(42)"
```

### REST API

POST `/execute` accepts:

```json
{
  "code": "print('hi')",
  "runtime": "python:3.11",
  "limits": {"memory": "512m", "cpus": "1.0", "timeout": 20}
}
```

It returns `stdout`, `stderr`, `exit_code` and `runtime_seconds`.

