# Development Guide

This page explains the layout of the repository and how to set up a local development environment.

## Repository Structure

- **`evoagentx/`** – Core Python library containing agents, tools, models and workflow logic.
- **`examples/`** – Sample scripts and workflows demonstrating how to use EvoAgentX.
- **`server/`** – FastAPI backend for running workflows and serving a REST API.
- **`client/`** – Vite + React front‑end for interacting with the backend.
- **`intelligence-parser/`** – Stand‑alone TypeScript utility package.
- **`tests/`** – Unit tests for the Python modules and components.
- **`docs/`** – MkDocs documentation source files.
- **`run_evoagentx.py`** – Simple script to generate and run a workflow from a goal.

## Local Setup

Install the Python dependencies in development mode:

```bash
pip install -e .[dev]
# or
pip install -r requirements.txt
```

Install the Node dependencies for the intelligence-parser package:
```bash
cd intelligence-parser
npm install
```

Set your `OPENAI_API_KEY` as described in the [Quickstart Guide](quickstart.md#api-key--llm-setup).

## Database Dependencies

- If you use the PostgreSQL backend, install the driver:

```bash
pip install psycopg2-binary
```

- Ensure you have access to a running PostgreSQL server and configure your connection as needed.

## Running Tests

Execute the unit tests before submitting changes:

```bash
pytest -q
```

## Building the Documentation

The documentation site is built with MkDocs. You can preview it locally with:

```bash
mkdocs serve
```

The site configuration is defined in `mkdocs.yml`.

## Full‑Stack Example

The repository also includes a small FastAPI server and React client. To try them:

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
uvicorn server.main:app --reload
```

```bash
# Frontend
cd client
pnpm install
pnpm dev
```

See the [README](../README.md#quick-start-full-stack) for details.
