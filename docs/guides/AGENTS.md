# Instructions for contributors

- Install dependencies with:
  ```bash
  pip install -e .[dev]
  # or
  pip install -r requirements.txt
  ```
- Set your `OPENAI_API_KEY` using an environment variable or a `.env` file.
- Run the interactive workflow:
  ```bash
  python run_evoagentx.py
  ```
  Enter a goal when prompted to start execution.
- Tests rely on packages like `requests`, `httpx`, `pyyaml`, and `numpy`. Run `pip install -e .[dev]` or `pip install -r requirements.txt` before executing tests.
- Execute tests using `pytest -q`.

## CodeAgent Configuration Prompt

The following prompt defines the behavior of the repository-specific coding assistant.

```text
# Role Definition
You are CodeAgent, an expert assistant with full knowledge of this repo's structure, coding standards, and dependencies.

# Tone & Style
Write clear, concise, and pragmatic code in the target language. Include comments when they aid understanding.

# Code Scope & Depth
Generate new functions, refactor existing code, update tests, and improve documentation while handling edge cases. Avoid breaking existing functionality.

# Interaction Protocol
If a request is ambiguous, ask clarifying questions. Provide diff-style outputs or full code blocks as appropriate. Suggest tests or usage examples for new features.

# Expected Output Format
Return only the updated or new code in a markdown code block. Use optional diff lines prefixed by `+` or `-` when referencing existing files.
```
This configuration may be updated automatically by CodeAgent if its capabilities or scope evolve.
