#!/bin/bash

# EvoAgentX Obsidian Integration Quick Start Script
# This script sets up the backend server for Obsidian integration

set -e

echo "🚀 EvoAgentX Obsidian Integration Setup"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "server/main.py" ]; then
    echo "❌ Error: Please run this script from the EvoAgentX root directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please add your OPENAI_API_KEY!"
    else
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo "✅ Created basic .env file. Please add your OPENAI_API_KEY!"
    fi
    echo ""
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not found in environment"
    echo "   Make sure to set it in .env file for full functionality"
    echo ""
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e .[dev] || pip install -r requirements.txt

# Install server dependencies
echo "📦 Installing server dependencies..."
cd server
pip install -r requirements.txt
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Set your OPENAI_API_KEY in the .env file"
echo "2. Start the server: ./start-obsidian-server.sh"
echo "3. Install the Obsidian plugin from examples/obsidian-plugin/"
echo "4. Configure the plugin settings in Obsidian"
echo ""
echo "📖 Documentation:"
echo "   - Full guide: docs/obsidian-integration.md"
echo "   - Plugin example: examples/obsidian-plugin/"
echo "   - API docs: http://localhost:8000/docs (after starting server)"
echo ""
echo "🧪 Test the API:"
echo "   python test_obsidian_api.py (after starting server)"
