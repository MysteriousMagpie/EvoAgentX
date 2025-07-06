#!/usr/bin/env python3
"""
Enhanced EvoAgentX Server Startup Script with Dev-Pipe Integration

This script initializes the dev-pipe communication framework and starts the
EvoAgentX server with full VaultPilot integration and enhanced features.
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from server.services.devpipe_integration import dev_pipe

def setup_dev_pipe():
    """Initialize the dev-pipe communication framework"""
    print("🔧 Setting up Dev-Pipe Communication Framework...")
    
    # Create all necessary directories
    directories = [
        dev_pipe.queues_dir,
        dev_pipe.tasks_dir,
        dev_pipe.status_dir,
        dev_pipe.logs_dir,
        dev_pipe.devpipe_root / "config"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for queues and tasks
        if dir_path.name == "queues":
            for subdir in ["incoming", "outgoing", "processing", "archive"]:
                (dir_path / subdir).mkdir(exist_ok=True)
        elif dir_path.name == "tasks":
            for subdir in ["active", "pending", "completed", "failed"]:
                (dir_path / subdir).mkdir(exist_ok=True)
        elif dir_path.name == "logs":
            for subdir in ["debug", "info", "error"]:
                (dir_path / subdir).mkdir(exist_ok=True)
    
    # Create initial configuration files
    create_dev_pipe_config()
    
    print("✅ Dev-Pipe framework initialized successfully")

def create_dev_pipe_config():
    """Create initial dev-pipe configuration files"""
    config_dir = dev_pipe.devpipe_root / "config"
    
    # Create settings.json
    settings = {
        "version": "1.0.0",
        "framework": {
            "name": "VaultPilot Dev-Pipe Communication Framework",
            "description": "Structured communication between AI agents and backend systems",
            "created": datetime.now().isoformat()
        },
        "communication": {
            "protocol_version": "1.0.0",
            "message_timeout": 30,
            "retry_attempts": 3,
            "queue_processing_interval": 1
        },
        "vault_management": {
            "enabled": True,
            "progress_tracking": True,
            "error_handling": True,
            "performance_monitoring": True
        },
        "enhanced_workflows": {
            "enabled": True,
            "streaming_support": True,
            "background_processing": True,
            "cancellation_support": True
        }
    }
    
    with open(config_dir / "settings.json", 'w') as f:
        import json
        json.dump(settings, f, indent=2)
    
    # Create permissions.json
    permissions = {
        "vault_operations": {
            "read": True,
            "write": True,
            "delete": True,
            "batch_operations": True
        },
        "workflow_execution": {
            "create": True,
            "execute": True,
            "cancel": True,
            "monitor": True
        },
        "system_access": {
            "status_monitoring": True,
            "error_reporting": True,
            "performance_metrics": True
        }
    }
    
    with open(config_dir / "permissions.json", 'w') as f:
        import json
        json.dump(permissions, f, indent=2)
    
    print("📝 Dev-Pipe configuration files created")

async def initialize_system_status():
    """Initialize system status in dev-pipe"""
    print("📊 Initializing system status...")
    
    # Initialize core components status
    components = [
        ("evoagentx-server", {
            "status": "starting",
            "version": "1.0.0",
            "dev_pipe_integration": "active",
            "startup_time": datetime.now().isoformat()
        }),
        ("vault-management", {
            "status": "initializing",
            "endpoints": [
                "structure", "file/operation", "file/batch", 
                "search", "organize", "backup", "context"
            ],
            "dev_pipe_enabled": True
        }),
        ("enhanced-workflows", {
            "status": "initializing",
            "templates": [
                "research_synthesis", "content_optimization",
                "vault_organization", "knowledge_mapping"
            ],
            "streaming_support": True
        }),
        ("obsidian-api", {
            "status": "initializing",
            "endpoints": ["chat", "copilot", "agents", "memory"],
            "websocket_support": True
        })
    ]
    
    for component, status in components:
        await dev_pipe.update_system_status(component, status)
    
    # Log successful initialization
    await dev_pipe.log_message("info", "System initialization complete", {
        "components_initialized": len(components),
        "dev_pipe_framework": "active"
    })
    
    print("✅ System status initialized")

def check_dependencies():
    """Check that all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "aiofiles",
        "websockets"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies satisfied")
    return True

def run_server(host="127.0.0.1", port=8000, dev_mode=False):
    """Start the EvoAgentX server with dev-pipe integration"""
    
    # Set environment variables for development
    if dev_mode:
        os.environ["EVOAGENTX_DEV_MODE"] = "true"
        os.environ["FASTAPI_RELOAD"] = "true"
    
    print(f"🚀 Starting EvoAgentX Server with VaultPilot Integration")
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔌 VaultPilot WebSocket: ws://{host}:{port}/ws/obsidian")
    print(f"🎯 Dev-Pipe Integration: Active")
    print(f"📊 System Status: http://{host}:{port}/dev-pipe/status")
    
    # Prepare uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "server.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if dev_mode:
        cmd.extend(["--reload", "--reload-dir", str(project_root)])
    
    try:
        # Start the server
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        print("📝 Logging shutdown to dev-pipe...")
        
        # Log shutdown (note: this won't work if server is already down)
        # but it's good practice to attempt it
        try:
            asyncio.run(dev_pipe.log_message("info", "Server shutdown initiated"))
        except:
            pass
        
        print("✅ Server stopped")

async def test_dev_pipe_integration():
    """Test dev-pipe integration"""
    print("🧪 Testing dev-pipe integration...")
    
    try:
        # Test task creation
        task_id = await dev_pipe.create_task(
            task_type="system_test",
            operation="integration_test",
            parameters={"test": True}
        )
        
        # Test progress notification
        await dev_pipe.notify_progress(task_id, "integration_test", 50, 
                                     details={"stage": "testing"})
        
        # Test completion
        await dev_pipe.send_completion_notification(
            task_id, "integration_test", {"test_result": "success"}
        )
        
        print("✅ Dev-pipe integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Dev-pipe integration test failed: {e}")
        return False

async def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Start EvoAgentX Server with VaultPilot Integration")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--dev", action="store_true", help="Enable development mode with auto-reload")
    parser.add_argument("--test", action="store_true", help="Run integration tests only")
    parser.add_argument("--setup-only", action="store_true", help="Setup dev-pipe and exit")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎯 EvoAgentX Server with VaultPilot Dev-Pipe Integration")
    print("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup dev-pipe
    setup_dev_pipe()
    
    # Initialize system status
    await initialize_system_status()
    
    if args.setup_only:
        print("✅ Dev-pipe setup complete. Exiting as requested.")
        return
    
    # Test integration
    if args.test:
        success = await test_dev_pipe_integration()
        sys.exit(0 if success else 1)
    
    # Start server
    print("\n" + "=" * 70)
    run_server(args.host, args.port, args.dev)

if __name__ == "__main__":
    asyncio.run(main())
