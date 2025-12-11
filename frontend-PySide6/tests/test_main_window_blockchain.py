"""Tests for Main Window - Blockchain Page Integration."""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication
import sys

from ui.main_window import MainWindow
from core.api_client import APIClient
from core.data_manager import DataManager
from core.updater import DataUpdater


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock(spec=APIClient)
    client.is_connected.return_value = True
    client.start_simulator.return_value = {'status': 'started'}
    client.stop_simulator.return_value = {'status': 'stopped'}
    client.reset_simulator.return_value = {'status': 'reset'}
    return client


@pytest.fixture
def data_manager(mock_api_client):
    """Create DataManager instance."""
    return DataManager(mock_api_client)


@pytest.fixture
def updater(mock_api_client, data_manager):
    """Create DataUpdater instance."""
    return DataUpdater(mock_api_client, data_manager)


@pytest.fixture
def main_window(qapp, mock_api_client, data_manager, updater):
    """Create MainWindow instance."""
    window = MainWindow(mock_api_client, data_manager, updater)
    yield window
    window.close()
    window.deleteLater()


class TestMainWindowBlockchainIntegration:
    """Test suite for blockchain page integration in main window."""
    
    def test_blockchain_page_exists(self, main_window):
        """Test blockchain page is created."""
        assert hasattr(main_window, 'blockchain_page')
        assert main_window.blockchain_page is not None
    
    def test_blockchain_tab_added(self, main_window):
        """Test blockchain tab is added to tabs."""
        assert main_window.tabs.count() == 4
        
        # Check tab names
        tab_names = []
        for i in range(main_window.tabs.count()):
            tab_names.append(main_window.tabs.tabText(i))
        
        assert "Blockchain" in " ".join(tab_names)
    
    def test_blockchain_page_accessible(self, main_window):
        """Test blockchain page can be switched to."""
        # Switch to blockchain tab (index 3)
        main_window.tabs.setCurrentIndex(3)
        assert main_window.tabs.currentWidget() == main_window.blockchain_page
    
    def test_blockchain_page_has_graph_widget(self, main_window):
        """Test blockchain page has graph widget."""
        assert hasattr(main_window.blockchain_page, 'graph_widget')
        assert main_window.blockchain_page.graph_widget is not None
    
    def test_blockchain_page_has_chain_drawer(self, main_window):
        """Test blockchain page has chain drawer."""
        assert hasattr(main_window.blockchain_page, 'chain_drawer')
        assert main_window.blockchain_page.chain_drawer is not None
    
    def test_reset_clears_blockchain_page(self, main_window, mock_api_client, qapp):
        """Test reset button clears blockchain page."""
        # Add some data to blockchain page
        blockchain_data = {
            'chain_length': 5,
            'pending_transactions': 3,
            'blocks': [
                {
                    'index': 0,
                    'hash': 'genesis',
                    'previous_hash': '0',
                    'miner_id': 'genesis',
                    'transaction_count': 0,
                    'is_orphan': False,
                    'is_malicious': False,
                    'transactions': []
                }
            ]
        }
        
        main_window.blockchain_page._render_blockchain(blockchain_data)
        assert len(main_window.blockchain_page.graph_widget.scene.items()) > 0
        
        # Reset
        main_window.btn_reset.click()
        qapp.processEvents()
        
        # Check blockchain page cleared
        assert len(main_window.blockchain_page.graph_widget.scene.items()) == 0
    
    def test_blockchain_page_receives_data_manager(self, main_window, data_manager):
        """Test blockchain page receives data manager."""
        assert main_window.blockchain_page.data_manager == data_manager
    
    def test_all_pages_present(self, main_window):
        """Test all 4 pages are present."""
        assert hasattr(main_window, 'dashboard_page')
        assert hasattr(main_window, 'nodes_page')
        assert hasattr(main_window, 'network_page')
        assert hasattr(main_window, 'blockchain_page')
    
    def test_blockchain_stats_labels_exist(self, main_window):
        """Test blockchain page stats labels exist."""
        assert hasattr(main_window.blockchain_page, 'lbl_total_blocks')
        assert hasattr(main_window.blockchain_page, 'lbl_forks')
        assert hasattr(main_window.blockchain_page, 'lbl_pending_tx')
        assert hasattr(main_window.blockchain_page, 'lbl_orphan_blocks')
    
    def test_blockchain_controls_exist(self, main_window):
        """Test blockchain page control buttons exist."""
        assert hasattr(main_window.blockchain_page, 'btn_zoom_in')
        assert hasattr(main_window.blockchain_page, 'btn_zoom_out')
        assert hasattr(main_window.blockchain_page, 'btn_fit_view')
    
    def test_blockchain_filters_exist(self, main_window):
        """Test blockchain page filter checkboxes exist."""
        assert hasattr(main_window.blockchain_page, 'chk_show_genesis')
        assert hasattr(main_window.blockchain_page, 'chk_show_normal')
        assert hasattr(main_window.blockchain_page, 'chk_show_malicious')
        assert hasattr(main_window.blockchain_page, 'chk_show_orphan')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
