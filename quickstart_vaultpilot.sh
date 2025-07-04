#!/bin/bash
# VaultPilot Integration Quick Start Script

echo "🚀 VaultPilot ↔ EvoAgentX Integration Quick Start"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "run_server.py" ]; then
    echo "❌ Please run this script from the EvoAgentX root directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "Installing required dependencies..."
    pip install -r requirements.txt
fi

# Test the integration
echo "🧪 Testing integration..."
python -c "from evoagentx.api import app; print('✅ Integration ready')" 2>/dev/null || {
    echo "❌ Integration test failed. Check dependencies."
    exit 1
}

echo ""
echo "🎉 VaultPilot Integration Ready!"
echo ""
echo "📍 Quick Start Commands:"
echo ""
echo "1. Start the server:"
echo "   python run_server.py --dev"
echo ""
echo "2. Test the integration:"
echo "   python test_vaultpilot_integration.py"
echo ""
echo "3. Configure VaultPilot plugin:"
echo "   Backend URL: http://127.0.0.1:8000"
echo ""
echo "🔗 Documentation: VAULTPILOT_INTEGRATION_COMPLETE.md"
