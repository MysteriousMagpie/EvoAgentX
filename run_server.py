#!/usr/bin/env python3
"""
EvoAgentX Server with VaultPilot Integration

This script starts the EvoAgentX server with VaultPilot integration enabled.
Run this script to start the server that VaultPilot can connect to.

Usage:
    python run_server.py [--host HOST] [--port PORT] [--dev]

Examples:
    python run_server.py                    # Default: localhost:8000
    python run_server.py --port 8080        # Custom port
    python run_server.py --host 0.0.0.0     # Listen on all interfaces
    python run_server.py --dev              # Development mode with hot reload
"""

import argparse
import uvicorn
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def main():
    parser = argparse.ArgumentParser(description="EvoAgentX Server with VaultPilot Integration")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--dev", action="store_true", help="Enable development mode with hot reload")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], 
                       help="Log level (default: info)")
    
    args = parser.parse_args()
    
    print("🚀 Starting EvoAgentX Server with VaultPilot Integration")
    print(f"📍 Server URL: http://{args.host}:{args.port}")
    print(f"🔌 VaultPilot WebSocket: ws://{args.host}:{args.port}/ws/obsidian")
    print("=" * 60)
    
    # Configuration for VaultPilot integration
    config = {
        "app": "evoagentx.api:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "access_log": True,
    }
    
    if args.dev:
        config["reload"] = True
        config["reload_dirs"] = [project_root]
        print("🔧 Development mode enabled - auto-reload on file changes")
    
    print("💡 Configure VaultPilot with this URL in your Obsidian plugin settings")
    print()
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n👋 EvoAgentX Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
