"""Tests for Blockchain Explorer Page - API Integration."""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication
import sys

from ui.pages.blockchain_page import BlockchainExplorerPage
from core.data_manager import DataManager


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
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def data_manager(mock_api_client):
    """Create DataManager instance."""
    return DataManager(mock_api_client)


@pytest.fixture
def blockchain_page(qapp, data_manager):
    """Create BlockchainExplorerPage instance."""
    page = BlockchainExplorerPage(data_manager)
    yield page
    page.deleteLater()


@pytest.fixture
def sample_blockchain():
    """Create sample blockchain data."""
    return {
        'chain_length': 5,
        'pending_transactions': 3,
        'blocks': [
            {
                'index': 0,
                'hash': 'genesis_hash',
                'previous_hash': '0',
                'miner_id': 'genesis',
                'transaction_count': 0,
                'timestamp': '2024-01-01 00:00:00',
                'is_orphan': False,
                'is_malicious': False,
                'transactions': []
            },
            {
                'index': 1,
                'hash': 'block1_hash',
                'previous_hash': 'genesis_hash',
                'miner_id': 'node1',
                'transaction_count': 2,
                'timestamp': '2024-01-01 01:00:00',
                'is_orphan': False,
                'is_malicious': False,
                'transactions': []
            },
            {
                'index': 2,
                'hash': 'block2_hash',
                'previous_hash': 'block1_hash',
                'miner_id': 'node2',
                'transaction_count': 1,
                'timestamp': '2024-01-01 02:00:00',
                'is_orphan': False,
                'is_malicious': False,
                'transactions': []
            }
        ]
    }


class TestBlockchainPageIntegration:
    """Test suite for blockchain page API integration."""
    
    def test_graph_widget_created(self, blockchain_page):
        """Test graph widget is created."""
        assert blockchain_page.graph_widget is not None
    
    def test_chain_drawer_created(self, blockchain_page):
        """Test chain drawer is created."""
        assert blockchain_page.chain_drawer is not None
    
    def test_blockchain_updated_signal(self, blockchain_page, data_manager, sample_blockchain, qapp):
        """Test blockchain update signal handling."""
        data_manager.blockchain_updated.emit(sample_blockchain)
        qapp.processEvents()
        
        assert "5" in blockchain_page.lbl_total_blocks.text()
        assert "3" in blockchain_page.lbl_pending_tx.text()
    
    def test_blockchain_rendering(self, blockchain_page, data_manager, sample_blockchain, qapp):
        """Test blockchain is rendered to graph."""
        data_manager.blockchain_updated.emit(sample_blockchain)
        qapp.processEvents()
        
        # Check that blocks were added to scene
        items = blockchain_page.graph_widget.scene.items()
        assert len(items) > 0
    
    def test_filter_blocks(self, blockchain_page, data_manager, qapp):
        """Test block filtering."""
        blockchain = {
            'chain_length': 4,
            'pending_transactions': 0,
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
                },
                {
                    'index': 1,
                    'hash': 'normal',
                    'previous_hash': 'genesis',
                    'miner_id': 'node1',
                    'transaction_count': 1,
                    'is_orphan': False,
                    'is_malicious': False,
                    'transactions': []
                },
                {
                    'index': 2,
                    'hash': 'orphan',
                    'previous_hash': 'unknown',
                    'miner_id': 'node2',
                    'transaction_count': 0,
                    'is_orphan': True,
                    'is_malicious': False,
                    'transactions': []
                }
            ]
        }
        
        # Set cache so filter can re-render
        data_manager._cache['blockchain'] = blockchain
        
        blockchain_page._render_blockchain(blockchain)
        initial_count = len(blockchain_page.graph_widget.scene.items())
        
        # Uncheck orphan filter
        blockchain_page.chk_show_orphan.setChecked(False)
        qapp.processEvents()
        
        # Should have fewer items
        new_count = len(blockchain_page.graph_widget.scene.items())
        assert new_count < initial_count
    
    def test_zoom_controls(self, blockchain_page):
        """Test zoom control integration."""
        initial_zoom = blockchain_page.graph_widget.get_zoom_level()
        
        blockchain_page.btn_zoom_in.click()
        assert blockchain_page.graph_widget.get_zoom_level() > initial_zoom
        
        blockchain_page.btn_zoom_out.click()
        assert blockchain_page.graph_widget.get_zoom_level() < initial_zoom + 0.2
    
    def test_fit_view_button(self, blockchain_page, sample_blockchain):
        """Test fit view button."""
        blockchain_page._render_blockchain(sample_blockchain)
        blockchain_page.btn_fit_view.click()
        # Should not crash
    
    def test_clear_display(self, blockchain_page, sample_blockchain):
        """Test clear display."""
        blockchain_page._render_blockchain(sample_blockchain)
        assert len(blockchain_page.graph_widget.scene.items()) > 0
        
        blockchain_page.clear_display()
        assert len(blockchain_page.graph_widget.scene.items()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
