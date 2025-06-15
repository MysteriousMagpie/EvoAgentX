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
- Execute tests using `pytest -q`.
