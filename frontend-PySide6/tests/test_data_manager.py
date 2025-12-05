"""Tests for Data Manager."""
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_manager import DataManager


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.is_connected.return_value = True
    client.get_status.return_value = {"running": True, "nodes": 10}
    client.get_nodes.return_value = [
        {"id": "node_0", "role": "validator"},
        {"id": "node_1", "role": "regular"}
    ]
    client.get_blockchain.return_value = {"chain_length": 5}
    client.get_pbft_status.return_value = {"primary": "node_0"}
    client.get_metrics.return_value = {"avg_response": 50}
    client.get_attack_status.return_value = {"active": []}
    client.get_network_messages.return_value = {"messages": []}
    client.get_fork_status.return_value = {"fork_detected": False}
    return client


@pytest.fixture
def data_manager(mock_api_client):
    """Create data manager instance."""
    return DataManager(mock_api_client)


class TestDataManager:
    """Test DataManager class."""
    
    def test_init(self, data_manager):
        """Test initialization."""
        assert data_manager.api_client is not None
        assert data_manager._cache['nodes'] == []
        assert data_manager._cache['status'] is None
    
    def test_signals_exist(self, data_manager):
        """Test all signals are defined."""
        assert hasattr(data_manager, 'status_updated')
        assert hasattr(data_manager, 'nodes_updated')
        assert hasattr(data_manager, 'blockchain_updated')
        assert hasattr(data_manager, 'pbft_updated')
        assert hasattr(data_manager, 'connection_error')
    
    def test_update_all_data_success(self, data_manager):
        """Test successful data update."""
        # Track signal emissions
        status_emitted = []
        nodes_emitted = []
        
        data_manager.status_updated.connect(lambda x: status_emitted.append(x))
        data_manager.nodes_updated.connect(lambda x: nodes_emitted.append(x))
        
        data_manager.update_all_data()
        
        # Check cache updated
        assert data_manager.get_cached_status()['running'] is True
        assert len(data_manager.get_cached_nodes()) == 2
        
        # Check signals emitted
        assert len(status_emitted) == 1
        assert len(nodes_emitted) == 1
    
    def test_update_all_data_connection_error(self, data_manager, mock_api_client):
        """Test connection error handling."""
        mock_api_client.is_connected.return_value = False
        
        error_emitted = []
        data_manager.connection_error.connect(lambda x: error_emitted.append(x))
        
        data_manager.update_all_data()
        
        assert len(error_emitted) == 1
    
    def test_get_node_by_id(self, data_manager):
        """Test getting node by ID."""
        data_manager._cache['nodes'] = [
            {"id": "node_0", "role": "validator"},
            {"id": "node_1", "role": "regular"}
        ]
        
        node = data_manager.get_node_by_id("node_0")
        assert node is not None
        assert node['role'] == "validator"
        
        node = data_manager.get_node_by_id("non_existent")
        assert node is None
    
    def test_clear_cache(self, data_manager):
        """Test cache clearing."""
        data_manager._cache['nodes'] = [{"id": "node_0"}]
        data_manager._cache['status'] = {"running": True}
        
        data_manager.clear_cache()
        
        assert data_manager.get_cached_nodes() == []
        assert data_manager.get_cached_status() is None
    
    def test_cached_getters(self, data_manager):
        """Test all cache getter methods."""
        data_manager._cache = {
            'status': {"test": 1},
            'nodes': [{"id": "node_0"}],
            'blockchain': {"chain": []},
            'pbft': {"view": 0},
            'metrics': {"avg": 50},
            'attacks': {"active": []},
            'messages': [{"type": "test"}],
            'fork_status': {"fork": False}
        }
        
        assert data_manager.get_cached_status()['test'] == 1
        assert len(data_manager.get_cached_nodes()) == 1
        assert data_manager.get_cached_blockchain()['chain'] == []
        assert data_manager.get_cached_pbft()['view'] == 0
        assert data_manager.get_cached_metrics()['avg'] == 50
        assert len(data_manager.get_cached_messages()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
