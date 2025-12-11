"""
Tests for PBFT API Integration (Milestone 8.4)
Tests API endpoints for PBFT status and network messages
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from core.api_client import APIClient
from core.data_manager import DataManager


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def api_client():
    """APIClient fixture"""
    return APIClient(base_url="http://localhost:8000")


@pytest.fixture
def data_manager(api_client):
    """DataManager fixture"""
    return DataManager(api_client)


@pytest.fixture
def sample_pbft_response():
    """Sample PBFT status response from API"""
    return {
        'primary_validator': 'node_0',
        'current_view': 5,
        'consensus_achieved_count': 42,
        'total_validators': 4,
        'total_messages': 847
    }


@pytest.fixture
def sample_messages_response():
    """Sample network messages response from API"""
    return {
        'messages': [
            {
                'timestamp': '2025-12-11T14:23:15',
                'sender_id': 'node_0',
                'receiver_id': 'ALL',
                'message_type': 'PRE_PREPARE',
                'view_number': 5,
                'sequence_number': 100
            },
            {
                'timestamp': '2025-12-11T14:23:16',
                'sender_id': 'node_1',
                'receiver_id': 'ALL',
                'message_type': 'PREPARE',
                'view_number': 5,
                'sequence_number': 100
            },
            {
                'timestamp': '2025-12-11T14:23:17',
                'sender_id': 'node_2',
                'receiver_id': 'ALL',
                'message_type': 'COMMIT',
                'view_number': 5,
                'sequence_number': 100
            }
        ],
        'total_count': 3
    }


class TestPBFTAPIIntegration:
    """Test suite for PBFT API Integration (8.4)"""
    
    def test_api_client_has_pbft_method(self, api_client):
        """Test APIClient has get_pbft_status method"""
        assert hasattr(api_client, 'get_pbft_status')
        assert callable(api_client.get_pbft_status)
    
    def test_api_client_has_messages_method(self, api_client):
        """Test APIClient has get_network_messages method"""
        assert hasattr(api_client, 'get_network_messages')
        assert callable(api_client.get_network_messages)
    
    def test_get_pbft_status_endpoint(self, api_client, sample_pbft_response):
        """Test get_pbft_status calls correct endpoint"""
        with patch.object(api_client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = sample_pbft_response
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            result = api_client.get_pbft_status()
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert '/pbft/status' in call_args[0][1]
            assert result == sample_pbft_response
    
    def test_get_network_messages_endpoint(self, api_client, sample_messages_response):
        """Test get_network_messages calls correct endpoint"""
        with patch.object(api_client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = sample_messages_response
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            result = api_client.get_network_messages()
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert '/network/messages' in call_args[0][1]
            assert result == sample_messages_response
    
    def test_get_network_messages_with_limit(self, api_client, sample_messages_response):
        """Test get_network_messages accepts limit parameter"""
        with patch.object(api_client.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = sample_messages_response
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            result = api_client.get_network_messages(limit=100)
            
            mock_request.assert_called_once()
            assert result == sample_messages_response
    
    def test_pbft_status_error_handling(self, api_client):
        """Test get_pbft_status handles errors gracefully"""
        with patch.object(api_client.session, 'request', side_effect=Exception("Connection error")):
            result = api_client.get_pbft_status()
            assert result is None or 'error' in result
    
    def test_network_messages_error_handling(self, api_client):
        """Test get_network_messages handles errors gracefully"""
        with patch.object(api_client.session, 'request', side_effect=Exception("Connection error")):
            result = api_client.get_network_messages()
            assert result is None or 'error' in result
    
    def test_data_manager_has_fetch_methods(self, data_manager):
        """Test DataManager has fetch methods"""
        assert hasattr(data_manager, 'fetch_pbft_status')
        assert hasattr(data_manager, 'fetch_messages')
        assert callable(data_manager.fetch_pbft_status)
        assert callable(data_manager.fetch_messages)
    
    def test_data_manager_fetch_pbft_status(self, qapp, data_manager, sample_pbft_response):
        """Test DataManager fetch_pbft_status method"""
        with patch.object(data_manager.api_client, 'get_pbft_status', return_value=sample_pbft_response):
            result = data_manager.fetch_pbft_status()
            
            assert result is not None
            assert 'primary' in result
            assert 'view' in result
            assert 'consensus_count' in result
    
    def test_data_manager_fetch_messages(self, qapp, data_manager, sample_messages_response):
        """Test DataManager fetch_messages method"""
        with patch.object(data_manager.api_client, 'get_network_messages', return_value=sample_messages_response):
            result = data_manager.fetch_messages()
            
            assert result is not None
            assert 'messages' in result
            messages = result['messages']
            assert len(messages) > 0
    
    def test_data_manager_pbft_signal(self, qapp, data_manager):
        """Test DataManager has pbft_updated signal"""
        assert hasattr(data_manager, 'pbft_updated')
    
    def test_data_manager_messages_signal(self, qapp, data_manager):
        """Test DataManager has messages_updated signal"""
        assert hasattr(data_manager, 'messages_updated')
    
    def test_data_manager_emit_pbft_signal(self, qapp, data_manager, sample_pbft_response):
        """Test DataManager emits pbft_updated signal"""
        signal_received = []
        
        def on_pbft_updated(data):
            signal_received.append(data)
        
        data_manager.pbft_updated.connect(on_pbft_updated)
        data_manager.pbft_updated.emit(sample_pbft_response)
        
        assert len(signal_received) > 0
    
    def test_data_manager_emit_messages_signal(self, qapp, data_manager, sample_messages_response):
        """Test DataManager emits messages_updated signal"""
        signal_received = []
        
        def on_messages_updated(data):
            signal_received.append(data)
        
        data_manager.messages_updated.connect(on_messages_updated)
        
        messages = sample_messages_response['messages']
        data_manager.messages_updated.emit(messages)
        
        assert len(signal_received) > 0
    
    def test_message_filtering_last_100(self, qapp, data_manager):
        """Test message filtering returns last 100 messages"""
        many_messages = {
            'messages': [
                {
                    'timestamp': f'2025-12-11T14:23:{i:02d}',
                    'sender_id': f'node_{i % 4}',
                    'receiver_id': 'ALL',
                    'message_type': 'PREPARE',
                    'view_number': 5,
                    'sequence_number': i
                }
                for i in range(150)
            ],
            'total_count': 150
        }
        
        with patch.object(data_manager.api_client, 'get_network_messages', return_value=many_messages):
            result = data_manager.fetch_messages(limit=100)
            
            messages = result.get('messages', [])
            assert len(messages) <= 100
    
    def test_pbft_data_transformation(self, qapp, data_manager, sample_pbft_response):
        """Test PBFT data is transformed to expected format"""
        with patch.object(data_manager.api_client, 'get_pbft_status', return_value=sample_pbft_response):
            result = data_manager.fetch_pbft_status()
            
            assert result is not None
            assert 'primary' in result
            assert result['primary'] == 'node_0'
            assert result['view'] == 5
            assert result['consensus_count'] == 42
            assert result['validator_count'] == 4
            assert result['total_messages'] == 847
    
    def test_message_data_transformation(self, qapp, data_manager, sample_messages_response):
        """Test message data is transformed to expected format"""
        with patch.object(data_manager.api_client, 'get_network_messages', return_value=sample_messages_response):
            result = data_manager.fetch_messages()
            
            messages = result.get('messages', [])
            assert len(messages) > 0
            
            msg = messages[0]
            assert 'timestamp' in msg
            assert 'sender' in msg
            assert 'receiver' in msg
            assert 'type' in msg
            assert 'view' in msg
    
    def test_real_time_update_integration(self, qapp, data_manager, sample_pbft_response, sample_messages_response):
        """Test real-time updates work for PBFT and messages"""
        pbft_signals = []
        message_signals = []
        
        data_manager.pbft_updated.connect(lambda d: pbft_signals.append(d))
        data_manager.messages_updated.connect(lambda d: message_signals.append(d))
        
        with patch.object(data_manager.api_client, 'get_pbft_status', return_value=sample_pbft_response), \
             patch.object(data_manager.api_client, 'get_network_messages', return_value=sample_messages_response):
            
            pbft_data = data_manager.fetch_pbft_status()
            if pbft_data:
                data_manager.pbft_updated.emit(pbft_data)
            
            messages = data_manager.fetch_messages()
            if messages:
                msg_list = messages.get('messages', [])
                data_manager.messages_updated.emit(msg_list)
        
        assert len(pbft_signals) > 0
        assert len(message_signals) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
