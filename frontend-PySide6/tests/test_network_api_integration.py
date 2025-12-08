"""
Tests for Network Map API Integration (Milestone 4.7)
Tests for node data fetching, graph updates, and real-time status changes
"""
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from ui.pages.network_page import NetworkMapPage
from core.data_manager import DataManager
from core.api_client import APIClient


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def api_client():
    """Mock APIClient"""
    client = Mock(spec=APIClient)
    return client


@pytest.fixture
def data_manager(api_client):
    """Mock DataManager"""
    manager = Mock(spec=DataManager)
    return manager


@pytest.fixture
def network_page(qapp, data_manager):
    """NetworkMapPage fixture with mocked data manager"""
    page = NetworkMapPage()
    page.data_manager = data_manager
    return page


@pytest.fixture
def sample_nodes():
    """Sample node data from API"""
    return [
        {
            'id': 'node_0',
            'role': 'validator',
            'status': 'healthy',
            'response_time': 50,
            'trust_score': 95,
            'is_sybil': False,
            'is_byzantine': False
        },
        {
            'id': 'node_1',
            'role': 'validator',
            'status': 'healthy',
            'response_time': 48,
            'trust_score': 88,
            'is_sybil': False,
            'is_byzantine': False
        },
        {
            'id': 'node_2',
            'role': 'regular',
            'status': 'healthy',
            'response_time': 55,
            'is_sybil': False,
            'is_byzantine': False
        },
        {
            'id': 'node_3',
            'role': 'regular',
            'status': 'under_attack',
            'response_time': 250,
            'is_sybil': False,
            'is_byzantine': False
        },
    ]


class TestNetworkPageDataManagerIntegration:
    """Test suite for NetworkPage and DataManager integration"""
    
    def test_page_has_data_manager_attribute(self, network_page):
        """Test that page can store data_manager reference"""
        assert hasattr(network_page, 'data_manager')
    
    def test_page_can_set_data_manager(self, network_page, data_manager):
        """Test setting data_manager on page"""
        network_page.set_data_manager(data_manager)
        assert network_page.data_manager == data_manager
    
    def test_set_data_manager_method_exists(self, network_page):
        """Test set_data_manager method exists"""
        assert hasattr(network_page, 'set_data_manager')
        assert callable(network_page.set_data_manager)
    
    def test_set_data_manager_connects_signals(self, network_page, data_manager, qapp):
        """Test that setting data_manager connects to nodes_updated signal"""
        # Create real data manager to test signal connection
        api_client = Mock(spec=APIClient)
        dm = DataManager(api_client)
        network_page.set_data_manager(dm)
        
        # Test signal connection by emitting
        sample_nodes = [{'id': 'node_0', 'role': 'validator', 'status': 'healthy'}]
        dm.nodes_updated.emit(sample_nodes)
        QApplication.processEvents()
        
        # If signal is connected, graph should be updated
        assert len(network_page.graph_widget.node_items) == 1


class TestNetworkGraphUpdates:
    """Test suite for network graph updates from API data"""
    
    def test_update_network_method_exists(self, network_page):
        """Test update_network method exists"""
        assert hasattr(network_page, 'update_network')
        assert callable(network_page.update_network)
    
    def test_update_network_accepts_node_list(self, network_page, sample_nodes):
        """Test update_network accepts node list"""
        # Should not raise exception
        network_page.update_network(sample_nodes)
    
    def test_update_network_calls_graph_widget_update(self, network_page, sample_nodes):
        """Test update_network calls graph widget's update_graph"""
        network_page.update_network(sample_nodes)
        
        # Check graph widget has been updated
        assert len(network_page.graph_widget.node_items) == len(sample_nodes)
    
    def test_update_network_with_empty_list(self, network_page):
        """Test update_network handles empty node list"""
        network_page.update_network([])
        
        # Graph should be cleared
        assert len(network_page.graph_widget.node_items) == 0
    
    def test_update_network_with_none(self, network_page):
        """Test update_network handles None gracefully"""
        # Should not crash
        network_page.update_network(None)
        assert len(network_page.graph_widget.node_items) == 0
    
    def test_update_network_preserves_node_data(self, network_page, sample_nodes):
        """Test that update_network preserves all node data"""
        network_page.update_network(sample_nodes)
        
        # Check first node data is preserved
        node_item = network_page.graph_widget.node_items['node_0']
        assert node_item.node_data['role'] == 'validator'
        assert node_item.node_data['status'] == 'healthy'
        assert node_item.node_data['response_time'] == 50


class TestRealTimeStatusUpdates:
    """Test suite for real-time node status updates"""
    
    def test_status_change_updates_node_color(self, network_page, sample_nodes):
        """Test that status change updates node color"""
        # Initial update
        network_page.update_network(sample_nodes)
        node_item = network_page.graph_widget.node_items['node_2']
        initial_color = node_item.brush().color().name()
        
        # Update status to under_attack
        updated_nodes = sample_nodes.copy()
        updated_nodes[2]['status'] = 'under_attack'
        network_page.update_network(updated_nodes)
        
        # Get new node item reference after update
        node_item = network_page.graph_widget.node_items['node_2']
        new_color = node_item.brush().color().name()
        assert new_color != initial_color
        assert new_color == '#ffc107'  # Yellow for under_attack
    
    def test_role_change_updates_node_color(self, network_page, sample_nodes):
        """Test that role change updates node color"""
        network_page.update_network(sample_nodes)
        
        # Change regular node to validator
        updated_nodes = sample_nodes.copy()
        updated_nodes[2]['role'] = 'validator'
        network_page.update_network(updated_nodes)
        
        node_item = network_page.graph_widget.node_items['node_2']
        # Should be blue for validator
        assert node_item.brush().color().name() == '#2196f3'
    
    def test_sybil_flag_updates_node_color(self, network_page, sample_nodes):
        """Test that setting is_sybil flag changes node color"""
        network_page.update_network(sample_nodes)
        
        # Mark node as sybil
        updated_nodes = sample_nodes.copy()
        updated_nodes[2]['is_sybil'] = True
        network_page.update_network(updated_nodes)
        
        node_item = network_page.graph_widget.node_items['node_2']
        # Should be red for sybil
        assert node_item.brush().color().name() == '#f44336'
    
    def test_byzantine_flag_updates_node_color(self, network_page, sample_nodes):
        """Test that setting is_byzantine flag changes node color"""
        network_page.update_network(sample_nodes)
        
        # Mark validator as byzantine
        updated_nodes = sample_nodes.copy()
        updated_nodes[0]['is_byzantine'] = True
        network_page.update_network(updated_nodes)
        
        node_item = network_page.graph_widget.node_items['node_0']
        # Should be orange for byzantine
        assert node_item.brush().color().name() == '#ff9800'
    
    def test_multiple_status_changes(self, network_page, sample_nodes):
        """Test multiple sequential status changes"""
        network_page.update_network(sample_nodes)
        
        # Change 1: under_attack
        updated_nodes = sample_nodes.copy()
        updated_nodes[2]['status'] = 'under_attack'
        network_page.update_network(updated_nodes)
        node_item = network_page.graph_widget.node_items['node_2']
        assert node_item.brush().color().name() == '#ffc107'
        
        # Change 2: back to healthy
        updated_nodes[2]['status'] = 'healthy'
        network_page.update_network(updated_nodes)
        # Get new reference after second update
        node_item = network_page.graph_widget.node_items['node_2']
        assert node_item.brush().color().name() == '#4caf50'
    
    def test_new_node_addition(self, network_page, sample_nodes):
        """Test that new nodes can be added dynamically"""
        network_page.update_network(sample_nodes)
        initial_count = len(network_page.graph_widget.node_items)
        
        # Add new node
        new_node = {
            'id': 'node_4',
            'role': 'regular',
            'status': 'healthy',
            'response_time': 60,
            'is_sybil': False,
            'is_byzantine': False
        }
        updated_nodes = sample_nodes + [new_node]
        network_page.update_network(updated_nodes)
        
        # Should have one more node
        assert len(network_page.graph_widget.node_items) == initial_count + 1
        assert 'node_4' in network_page.graph_widget.node_items
    
    def test_node_removal(self, network_page, sample_nodes):
        """Test that nodes can be removed dynamically"""
        network_page.update_network(sample_nodes)
        initial_count = len(network_page.graph_widget.node_items)
        
        # Remove a node
        updated_nodes = sample_nodes[:-1]  # Remove last node
        network_page.update_network(updated_nodes)
        
        # Should have one less node
        assert len(network_page.graph_widget.node_items) == initial_count - 1
        assert 'node_3' not in network_page.graph_widget.node_items


class TestSignalSlotConnections:
    """Test suite for signal-slot connections"""
    
    def test_nodes_updated_signal_triggers_update(self, qapp):
        """Test that nodes_updated signal triggers graph update"""
        # Create real objects with signal-slot
        api_client = Mock(spec=APIClient)
        data_manager = DataManager(api_client)
        network_page = NetworkMapPage()
        network_page.set_data_manager(data_manager)
        
        sample_nodes = [
            {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
        ]
        
        # Emit signal
        data_manager.nodes_updated.emit(sample_nodes)
        
        # Process events to ensure signal is handled
        QApplication.processEvents()
        
        # Graph should be updated
        assert len(network_page.graph_widget.node_items) == 2
    
    def test_multiple_signal_emissions(self, qapp):
        """Test multiple signal emissions update correctly"""
        api_client = Mock(spec=APIClient)
        data_manager = DataManager(api_client)
        network_page = NetworkMapPage()
        network_page.set_data_manager(data_manager)
        
        # First emission
        nodes1 = [{'id': 'node_0', 'role': 'validator', 'status': 'healthy'}]
        data_manager.nodes_updated.emit(nodes1)
        QApplication.processEvents()
        assert len(network_page.graph_widget.node_items) == 1
        
        # Second emission with more nodes
        nodes2 = [
            {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
        ]
        data_manager.nodes_updated.emit(nodes2)
        QApplication.processEvents()
        assert len(network_page.graph_widget.node_items) == 2


class TestErrorHandling:
    """Test suite for error handling in API integration"""
    
    def test_update_with_malformed_node_data(self, network_page):
        """Test handling of malformed node data"""
        malformed_nodes = [
            {'id': 'node_0'},  # Missing required fields
            {'role': 'validator'},  # Missing id
        ]
        
        # Should not crash
        try:
            network_page.update_network(malformed_nodes)
        except Exception as e:
            pytest.fail(f"update_network crashed with malformed data: {e}")
    
    def test_update_with_invalid_role(self, network_page):
        """Test handling of invalid role value"""
        invalid_nodes = [
            {
                'id': 'node_0',
                'role': 'invalid_role',  # Invalid role
                'status': 'healthy'
            }
        ]
        
        # Should not crash, default to regular
        network_page.update_network(invalid_nodes)
        assert len(network_page.graph_widget.node_items) == 1
    
    def test_update_with_missing_optional_fields(self, network_page):
        """Test handling of missing optional fields"""
        minimal_nodes = [
            {
                'id': 'node_0',
                'role': 'validator',
                'status': 'healthy'
                # Missing: response_time, trust_score, is_sybil, is_byzantine
            }
        ]
        
        # Should work with minimal data
        network_page.update_network(minimal_nodes)
        assert len(network_page.graph_widget.node_items) == 1
        
        node_item = network_page.graph_widget.node_items['node_0']
        # Should have defaults
        assert not node_item.node_data.get('is_sybil', False)
        assert not node_item.node_data.get('is_byzantine', False)


class TestPerformance:
    """Test suite for performance considerations"""
    
    def test_large_node_update_performance(self, network_page):
        """Test updating with large number of nodes"""
        # Create 100 nodes
        large_node_list = [
            {
                'id': f'node_{i}',
                'role': 'validator' if i < 20 else 'regular',
                'status': 'healthy',
                'response_time': 50 + i,
                'is_sybil': False,
                'is_byzantine': False
            }
            for i in range(100)
        ]
        
        # Should complete without significant delay
        import time
        start = time.time()
        network_page.update_network(large_node_list)
        elapsed = time.time() - start
        
        # Should be fast (< 2 seconds for 100 nodes)
        assert elapsed < 2.0
        assert len(network_page.graph_widget.node_items) == 100
    
    def test_frequent_updates_no_memory_leak(self, network_page, sample_nodes):
        """Test that frequent updates don't cause memory issues"""
        # Update many times
        for _ in range(50):
            network_page.update_network(sample_nodes)
        
        # Should still work correctly
        assert len(network_page.graph_widget.node_items) == len(sample_nodes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
