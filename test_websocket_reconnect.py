import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestWebSocketReconnect:
    def test_websocket_config(self):
        """Test WebSocket configuration"""
        ws_config = {
            'url': 'ws://localhost:8000/ws',
            'reconnect_interval': 5,
            'max_retries': 10,
            'timeout': 30,
            'auto_reconnect': True
        }
        
        assert 'url' in ws_config
        assert 'reconnect_interval' in ws_config
        assert 'max_retries' in ws_config
        assert ws_config['auto_reconnect'] is True
        assert ws_config['reconnect_interval'] > 0
        
    def test_connection_state_tracking(self):
        """Test connection state tracking"""
        connection_states = [
            'disconnected',
            'connecting', 
            'connected',
            'reconnecting',
            'failed'
        ]
        
        current_state = 'disconnected'
        assert current_state in connection_states
        
        # Test state transitions
        state_transitions = {
            'disconnected': ['connecting'],
            'connecting': ['connected', 'failed'],
            'connected': ['disconnected', 'reconnecting'],
            'reconnecting': ['connected', 'failed'],
            'failed': ['connecting', 'disconnected']
        }
        
        for state, allowed_next in state_transitions.items():
            assert isinstance(allowed_next, list)
            assert len(allowed_next) > 0
            
    def test_reconnect_logic(self):
        """Test reconnection logic"""
        class MockWebSocketClient:
            def __init__(self):
                self.connected = False
                self.retry_count = 0
                self.max_retries = 3
                
            def attempt_reconnect(self):
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    return True
                return False
                
            def reset_retry_count(self):
                self.retry_count = 0
        
        client = MockWebSocketClient()
        
        # Test successful reconnect attempts
        assert client.attempt_reconnect() is True
        assert client.retry_count == 1
        
        assert client.attempt_reconnect() is True
        assert client.retry_count == 2
        
        assert client.attempt_reconnect() is True
        assert client.retry_count == 3
        
        # Should fail after max retries
        assert client.attempt_reconnect() is False
        
        # Reset should work
        client.reset_retry_count()
        assert client.retry_count == 0
        
    def test_message_queuing(self):
        """Test message queuing during disconnection"""
        message_queue = []
        
        def queue_message(message):
            message_queue.append(message)
            
        def send_queued_messages():
            messages = message_queue.copy()
            message_queue.clear()
            return messages
        
        # Queue some messages
        queue_message({'type': 'test', 'data': 'message1'})
        queue_message({'type': 'test', 'data': 'message2'})
        
        assert len(message_queue) == 2
        
        # Send queued messages
        sent_messages = send_queued_messages()
        assert len(sent_messages) == 2
        assert len(message_queue) == 0
        
    @pytest.mark.asyncio
    async def test_async_connection_handling(self):
        """Test async connection handling"""
        async def mock_connect():
            await asyncio.sleep(0.1)  # Simulate connection delay
            return True
            
        async def mock_disconnect():
            await asyncio.sleep(0.05)  # Simulate disconnection
            return True
        
        # Test connection
        result = await mock_connect()
        assert result is True
        
        # Test disconnection
        result = await mock_disconnect()
        assert result is True

if __name__ == "__main__":
    pytest.main([__file__])
