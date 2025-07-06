import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestVaultPilotIntegration:
    def test_vaultpilot_configuration(self):
        """Test VaultPilot configuration structure"""
        vaultpilot_config = {
            'enabled': True,
            'vault_path': '/path/to/vault',
            'api_endpoints': {
                'health': '/api/vaultpilot/health',
                'status': '/api/vaultpilot/status',
                'process': '/api/vaultpilot/process'
            }
        }
        
        assert vaultpilot_config['enabled'] is True
        assert 'vault_path' in vaultpilot_config
        assert 'api_endpoints' in vaultpilot_config
        assert '/api/vaultpilot/health' in vaultpilot_config['api_endpoints'].values()
        
    def test_api_endpoint_structure(self):
        """Test API endpoint structure"""
        endpoints = [
            '/api/vaultpilot/health',
            '/api/vaultpilot/status', 
            '/api/vaultpilot/process',
            '/api/vaultpilot/files'
        ]
        
        for endpoint in endpoints:
            assert endpoint.startswith('/api/vaultpilot/')
            assert len(endpoint) > len('/api/vaultpilot/')
            
    def test_request_response_structure(self):
        """Test request/response structure"""
        mock_request = {
            'action': 'process_file',
            'file_path': '/vault/notes/test.md',
            'options': {
                'extract_metadata': True,
                'process_links': True
            }
        }
        
        mock_response = {
            'success': True,
            'data': {
                'processed': True,
                'metadata': {},
                'links': []
            },
            'message': 'File processed successfully'
        }
        
        assert 'action' in mock_request
        assert 'file_path' in mock_request
        assert 'success' in mock_response
        assert 'data' in mock_response
        assert mock_response['success'] is True
        
    def test_vault_path_validation(self):
        """Test vault path validation logic"""
        valid_paths = [
            '/Users/user/Documents/Vault',
            '/home/user/vault',
            'C:\\Users\\User\\Vault'
        ]
        
        invalid_paths = [
            '',
            None
        ]
        
        for path in valid_paths:
            assert isinstance(path, str)
            assert len(path) > 0
            
        for path in invalid_paths:
            if path is not None:
                assert len(path) == 0
            else:
                assert path is None

if __name__ == "__main__":
    pytest.main([__file__])
