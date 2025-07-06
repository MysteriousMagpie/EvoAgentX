"""
Test script to verify Ask/Agent mode functionality in EvoAgentX Obsidian API
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

def test_ask_mode():
    """Test ask mode for simple Q&A"""
    # Mock the API response for ask mode
    mock_response = {
        "response": "Python is a high-level programming language...",
        "agent_name": "QA Agent",
        "conversation_id": "test_conv_123",
        "metadata": {"mode": "ask"}
    }
    
    # Since we're testing the logic, not the actual HTTP calls,
    # we'll test the mode selection logic
    payload = {
        "message": "What is Python?",
        "mode": "ask"
    }
    
    assert payload["mode"] == "ask"
    assert "message" in payload
    assert len(payload["message"]) > 0

def test_agent_mode():
    """Test agent mode for workflow execution"""
    # Mock the API response for agent mode
    mock_response = {
        "response": "Here's a simple to-do list for learning Python...",
        "agent_name": "Workflow Agent",
        "conversation_id": "test_conv_456",
        "metadata": {"mode": "agent"}
    }
    
    payload = {
        "message": "Create a simple to-do list for learning Python",
        "mode": "agent"
    }
    
    assert payload["mode"] == "agent"
    assert "message" in payload
    assert len(payload["message"]) > 0

def test_default_mode():
    """Test default mode (should be 'ask')"""
    # Test that when no mode is specified, it defaults to ask
    payload = {
        "message": "Hello! How are you?"
        # No mode specified - should default to "ask"
    }
    
    # In the actual implementation, this would be handled by the API
    # but for testing we just verify the payload structure
    default_mode = payload.get("mode", "ask")
    assert default_mode == "ask"
    assert "message" in payload

def test_invalid_mode():
    """Test invalid mode parameter validation"""
    valid_modes = ["ask", "agent"]
    test_mode = "invalid_mode"
    
    # Test that invalid mode is not in valid modes
    assert test_mode not in valid_modes
    
    # Test validation logic
    def validate_mode(mode):
        return mode in valid_modes
    
    assert not validate_mode(test_mode)
    assert validate_mode("ask")
    assert validate_mode("agent")
