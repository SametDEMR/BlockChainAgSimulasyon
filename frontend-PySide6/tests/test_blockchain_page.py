"""Tests for Blockchain Explorer Page."""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication
import sys

from ui.pages.blockchain_page import BlockchainExplorerPage
from core.data_manager import DataManager


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.is_connected.return_value = True
    client.get_blockchain.return_value = {
        'chain_length': 10,
        'pending_transactions': 5
    }
    client.get_fork_status.return_value = {
        'active_forks': 2,
        'orphan_blocks': 3
    }
    return client


@pytest.fixture
def data_manager(mock_api_client):
    """Create DataManager instance with mock API client."""
    return DataManager(mock_api_client)


@pytest.fixture
def blockchain_page(qapp, data_manager):
    """Create BlockchainExplorerPage instance."""
    page = BlockchainExplorerPage(data_manager)
    yield page
    page.deleteLater()


class TestBlockchainExplorerPage:
    """Test suite for BlockchainExplorerPage."""
    
    def test_initialization(self, blockchain_page):
        """Test that page initializes correctly."""
        assert blockchain_page is not None
        assert blockchain_page.data_manager is not None
        
        # Check that stats labels exist
        assert blockchain_page.lbl_total_blocks is not None
        assert blockchain_page.lbl_forks is not None
        assert blockchain_page.lbl_pending_tx is not None
        assert blockchain_page.lbl_orphan_blocks is not None
        
        # Check initial values
        assert "Total Blocks: 0" in blockchain_page.lbl_total_blocks.text()
        assert "Forks: 0" in blockchain_page.lbl_forks.text()
        assert "Pending TX: 0" in blockchain_page.lbl_pending_tx.text()
        assert "Orphan Blocks: 0" in blockchain_page.lbl_orphan_blocks.text()
    
    def test_control_buttons_exist(self, blockchain_page):
        """Test that control buttons are created."""
        assert blockchain_page.btn_zoom_in is not None
        assert blockchain_page.btn_zoom_out is not None
        assert blockchain_page.btn_fit_view is not None
    
    def test_filter_checkboxes_exist(self, blockchain_page):
        """Test that filter checkboxes are created."""
        assert blockchain_page.chk_show_genesis is not None
        assert blockchain_page.chk_show_normal is not None
        assert blockchain_page.chk_show_malicious is not None
        assert blockchain_page.chk_show_orphan is not None
        
        # Check that all are initially checked
        assert blockchain_page.chk_show_genesis.isChecked()
        assert blockchain_page.chk_show_normal.isChecked()
        assert blockchain_page.chk_show_malicious.isChecked()
        assert blockchain_page.chk_show_orphan.isChecked()
    
    def test_zoom_in_signal(self, blockchain_page, qapp):
        """Test zoom in button emits signal."""
        signal_emitted = [False]
        
        def on_signal():
            signal_emitted[0] = True
        
        blockchain_page.zoom_in_requested.connect(on_signal)
        blockchain_page.btn_zoom_in.click()
        qapp.processEvents()
        
        assert signal_emitted[0], "Zoom in signal not emitted"
    
    def test_zoom_out_signal(self, blockchain_page, qapp):
        """Test zoom out button emits signal."""
        signal_emitted = [False]
        
        def on_signal():
            signal_emitted[0] = True
        
        blockchain_page.zoom_out_requested.connect(on_signal)
        blockchain_page.btn_zoom_out.click()
        qapp.processEvents()
        
        assert signal_emitted[0], "Zoom out signal not emitted"
    
    def test_fit_view_signal(self, blockchain_page, qapp):
        """Test fit view button emits signal."""
        signal_emitted = [False]
        
        def on_signal():
            signal_emitted[0] = True
        
        blockchain_page.fit_view_requested.connect(on_signal)
        blockchain_page.btn_fit_view.click()
        qapp.processEvents()
        
        assert signal_emitted[0], "Fit view signal not emitted"
    
    def test_filter_changed_signal(self, blockchain_page, qapp):
        """Test filter checkbox emits signal."""
        signal_data = [None]
        
        def on_signal(filters):
            signal_data[0] = filters
        
        blockchain_page.filter_changed.connect(on_signal)
        blockchain_page.chk_show_genesis.setChecked(False)
        qapp.processEvents()
        
        assert signal_data[0] is not None, "Filter changed signal not emitted"
        assert signal_data[0]['show_genesis'] == False
        assert signal_data[0]['show_normal'] == True
    
    def test_update_stats(self, blockchain_page):
        """Test manual stats update."""
        blockchain_page.update_stats(
            total_blocks=100,
            forks=5,
            pending_tx=10,
            orphan_blocks=2
        )
        
        assert "100" in blockchain_page.lbl_total_blocks.text()
        assert "5" in blockchain_page.lbl_forks.text()
        assert "10" in blockchain_page.lbl_pending_tx.text()
        assert "2" in blockchain_page.lbl_orphan_blocks.text()
    
    def test_blockchain_updated_signal(self, blockchain_page, data_manager, qapp):
        """Test blockchain update signal handling."""
        blockchain_data = {
            'chain_length': 50,
            'pending_transactions': 15
        }
        
        data_manager.blockchain_updated.emit(blockchain_data)
        qapp.processEvents()
        
        assert "50" in blockchain_page.lbl_total_blocks.text()
        assert "15" in blockchain_page.lbl_pending_tx.text()
    
    def test_fork_status_updated_signal(self, blockchain_page, data_manager, qapp):
        """Test fork status update signal handling."""
        fork_status = {
            'active_forks': 3,
            'orphan_blocks': 7
        }
        
        data_manager.fork_status_updated.emit(fork_status)
        qapp.processEvents()
        
        assert "3" in blockchain_page.lbl_forks.text()
        assert "7" in blockchain_page.lbl_orphan_blocks.text()
    
    def test_clear_display(self, blockchain_page):
        """Test clear display functionality."""
        # First set some values
        blockchain_page.update_stats(100, 5, 10, 2)
        blockchain_page.chk_show_genesis.setChecked(False)
        
        # Clear
        blockchain_page.clear_display()
        
        # Check all reset to initial state
        assert "Total Blocks: 0" in blockchain_page.lbl_total_blocks.text()
        assert "Forks: 0" in blockchain_page.lbl_forks.text()
        assert "Pending TX: 0" in blockchain_page.lbl_pending_tx.text()
        assert "Orphan Blocks: 0" in blockchain_page.lbl_orphan_blocks.text()
        
        # Check filters reset
        assert blockchain_page.chk_show_genesis.isChecked()
        assert blockchain_page.chk_show_normal.isChecked()
        assert blockchain_page.chk_show_malicious.isChecked()
        assert blockchain_page.chk_show_orphan.isChecked()
    
    def test_get_filter_state(self, blockchain_page):
        """Test get filter state functionality."""
        # Modify some filters
        blockchain_page.chk_show_genesis.setChecked(False)
        blockchain_page.chk_show_malicious.setChecked(False)
        
        filters = blockchain_page.get_filter_state()
        
        assert filters['show_genesis'] == False
        assert filters['show_normal'] == True
        assert filters['show_malicious'] == False
        assert filters['show_orphan'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
