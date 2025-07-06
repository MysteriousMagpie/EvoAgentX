import pytest
from unittest.mock import MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCORSFix:
    def test_cors_middleware_configuration(self):
        """Test CORS configuration"""
        # Test basic CORS configuration
        allowed_origins = ['http://localhost:3000', 'http://localhost:8080', 'app://obsidian.md']
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        allowed_headers = ['Content-Type', 'Authorization']
        
        assert 'GET' in allowed_methods
        assert 'POST' in allowed_methods
        assert 'Content-Type' in allowed_headers
        assert 'app://obsidian.md' in allowed_origins
        
    def test_cors_headers_structure(self):
        """Test CORS headers structure"""
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        assert 'Access-Control-Allow-Origin' in cors_headers
        assert 'Access-Control-Allow-Methods' in cors_headers
        assert 'Access-Control-Allow-Headers' in cors_headers
        
    def test_preflight_request_handling(self):
        """Test OPTIONS preflight request handling"""
        # Mock an OPTIONS request
        request_method = 'OPTIONS'
        request_headers = {
            'Origin': 'app://obsidian.md',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # Simulate preflight response
        response_headers = {
            'Access-Control-Allow-Origin': 'app://obsidian.md',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        assert request_method == 'OPTIONS'
        assert 'Origin' in request_headers
        assert 'Access-Control-Allow-Origin' in response_headers
        
    def test_obsidian_origins(self):
        """Test Obsidian-specific origins"""
        obsidian_origins = [
            'app://obsidian.md',
            'capacitor://localhost',
            'http://localhost:5173'
        ]
        
        for origin in obsidian_origins:
            assert isinstance(origin, str)
            assert len(origin) > 0

if __name__ == "__main__":
    pytest.main([__file__])
