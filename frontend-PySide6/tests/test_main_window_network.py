"""
Tests for MainWindow Network Page Integration
"""
import pytest
import sys
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_api_client():
    """Create mock API client"""
    client = Mock()
    client.is_connected = Mock(return_value=True)
    client.start_simulator = Mock(return_value={'status': 'started'})
    client.stop_simulator = Mock(return_value={'status': 'stopped'})
    client.reset_simulator = Mock(return_value={'status': 'reset'})
    client.trigger_attack = Mock(return_value={'attack_id': 'test_attack'})
    client.stop_attack = Mock(return_value={'status': 'stopped'})
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager"""
    from PySide6.QtCore import QObject, Signal
    
    class MockDataManager(QObject):
        nodes_updated = Signal(list)
        status_updated = Signal(dict)
        blockchain_updated = Signal(dict)
        pbft_updated = Signal(dict)
        metrics_updated = Signal(dict)
        attacks_updated = Signal(dict)
        messages_updated = Signal(list)
        connection_error = Signal(str)
        api_error = Signal(str)
        
        def __init__(self):
            super().__init__()
            self.clear_cache = Mock()
    
    return MockDataManager()


@pytest.fixture
def mock_updater():
    """Create mock updater"""
    from PySide6.QtCore import QObject, Signal
    
    class MockUpdater(QObject):
        update_completed = Signal()
        
        def __init__(self):
            super().__init__()
            self.start_updating = Mock()
            self.stop_updating = Mock()
    
    return MockUpdater()


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """Create main window fixture"""
    window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
    return window


@pytest.fixture
def sample_nodes():
    """Sample node data"""
    return [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
    ]


class TestNetworkPageIntegration:
    """Test suite for network page integration"""
    
    def test_network_page_exists(self, main_window):
        """Test network page tab exists"""
        assert hasattr(main_window, 'network_page')
        assert main_window.network_page is not None
    
    def test_network_page_tab_added(self, main_window):
        """Test network page added to tabs"""
        assert main_window.tabs.count() == 3
        assert main_window.tabs.tabText(2) == "🗺️ Network Map"
    
    def test_nodes_updated_signal_connected(self, main_window, sample_nodes):
        """Test nodes_updated signal updates network page"""
        main_window.data_manager.nodes_updated.emit(sample_nodes)
        assert len(main_window.network_page.graph_widget.node_items) == len(sample_nodes)
    
    def test_reset_clears_network(self, main_window, sample_nodes):
        """Test reset clears network page"""
        # Add nodes
        main_window.data_manager.nodes_updated.emit(sample_nodes)
        assert len(main_window.network_page.graph_widget.node_items) > 0
        
        # Reset
        main_window.btn_reset.click()
        assert len(main_window.network_page.graph_widget.node_items) == 0
    
    def test_network_page_tab_accessible(self, main_window):
        """Test can switch to network page tab"""
        main_window.tabs.setCurrentIndex(2)
        assert main_window.tabs.currentIndex() == 2
        assert main_window.tabs.currentWidget() == main_window.network_page


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
