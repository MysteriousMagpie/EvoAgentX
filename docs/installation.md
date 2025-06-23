# Installation Guide for EvoAgentX

This guide will walk you through the process of installing EvoAgentX on your system, setting up the required dependencies, and configuring the framework for your projects.

## Prerequisites

Before installing EvoAgentX, make sure you have the following prerequisites:

- Python 3.10 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- Conda (recommended for environment management, but optional)

## Installation Methods

There are several ways to install EvoAgentX. Choose the method that best suits your needs.

### Method 1: Using pip (Recommended)

The simplest way to install EvoAgentX is using pip:

```bash
pip install git+https://github.com/EvoAgentX/EvoAgentX.git
```

### Method 2: From Source (For Development)

If you want to contribute to EvoAgentX or need the latest development version, you can install it directly from the source:

```bash
# Clone the repository
git clone https://github.com/EvoAgentX/EvoAgentX/

# Navigate to the project directory
cd EvoAgentX

# Install the package in development mode
pip install -e .
```

### Method 3: Using Conda Environment (Recommended for Isolation)

If you prefer to use Conda for managing your Python environments, follow these steps:

```bash hl_lines="4-5"
# Create a new conda environment
conda create -n evoagentx python=3.10

# Activate the environment
conda activate evoagentx

# Install the package
pip install -r requirements.txt
# OR install in development mode
pip install -e .
```

## Verifying Installation

To verify that EvoAgentX has been installed correctly, run the following Python code:

```python
import evoagentx

# Print the version
print(evoagentx.__version__)
```

You should see the current version of EvoAgentX printed to the console.

## Database Backends

If you plan to use the PostgreSQL storage backend, you must also install the PostgreSQL driver:

```bash
pip install psycopg2-binary
```

You will also need a running PostgreSQL server. Configure your connection settings as needed in your application.

## Running the Backend and Frontend (Full Stack)

To run both the FastAPI backend (with Socket.IO support) and the React frontend:

1. **Start the backend with Socket.IO:**

```bash
uvicorn server.main:sio_app --host 0.0.0.0 --reload
```

- This exposes both REST API and Socket.IO endpoints on `http://localhost:8000` 
  and makes the backend reachable from other devices on your network.

2. **Start the frontend (Vite):**

```bash
cd client
npm install # or pnpm install
npm run dev -- --host 0.0.0.0
```

- The frontend will be available at `http://localhost:5173` by default (see `vite.config.ts`).

3. **(Optional) Use the provided script:**

You can use the `start-dev.sh` script to launch both servers:

```bash
bash start-dev.sh
```

---

**Note:**
- The frontend (`localhost:5173`) proxies API and Socket.IO requests to the backend (`localhost:8000`).
- Make sure you always run the backend as `sio_app` for Socket.IO support.

