"""Tests for Block Item."""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import sys

from ui.widgets.block_item import BlockItem, BlockItemSignalProxy


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def genesis_block_data():
    """Create genesis block data."""
    return {
        'index': 0,
        'hash': 'genesis123456789',        'previous_hash': '0',
        'miner_id': 'genesis',
        'transaction_count': 0,
        'timestamp': '2024-01-01 00:00:00',
        'is_orphan': False,
        'is_malicious': False
    }


@pytest.fixture
def normal_block_data():
    """Create normal block data."""
    return {
        'index': 5,
        'hash': 'abc123def456789',
        'previous_hash': 'prev_hash_123',
        'miner_id': 'node_001',
        'transaction_count': 3,
        'timestamp': '2024-01-01 12:30:00',
        'is_orphan': False,
        'is_malicious': False
    }


@pytest.fixture
def malicious_block_data():
    """Create malicious block data."""
    return {
        'index': 10,
        'hash': 'malicious123456',
        'previous_hash': 'prev_hash_456',
        'miner_id': 'node_evil',
        'transaction_count': 5,
        'timestamp': '2024-01-01 15:00:00',
        'is_orphan': False,
        'is_malicious': True
    }


@pytest.fixture
def orphan_block_data():
    """Create orphan block data."""
    return {
        'index': 7,
        'hash': 'orphan123456789',
        'previous_hash': 'unknown_hash',
        'miner_id': 'node_002',
        'transaction_count': 2,
        'timestamp': '2024-01-01 13:00:00',
        'is_orphan': True,
        'is_malicious': False
    }


class TestBlockItem:
    """Test suite for BlockItem."""
    
    def test_genesis_block_creation(self, qapp, genesis_block_data):
        """Test genesis block creation."""
        item = BlockItem(genesis_block_data)
        
        assert item.index == 0
        assert item.block_type == 'genesis'
        assert item.brush().color() == BlockItem.COLORS['genesis']
    
    def test_normal_block_creation(self, qapp, normal_block_data):
        """Test normal block creation."""
        item = BlockItem(normal_block_data)
        
        assert item.index == 5
        assert item.block_type == 'normal'
        assert item.brush().color() == BlockItem.COLORS['normal']
    
    def test_malicious_block_creation(self, qapp, malicious_block_data):
        """Test malicious block creation."""
        item = BlockItem(malicious_block_data)
        
        assert item.index == 10
        assert item.block_type == 'malicious'
        assert item.brush().color() == BlockItem.COLORS['malicious']
    
    def test_orphan_block_creation(self, qapp, orphan_block_data):
        """Test orphan block creation."""
        item = BlockItem(orphan_block_data)
        
        assert item.index == 7
        assert item.block_type == 'orphan'
        assert item.brush().color() == BlockItem.COLORS['orphan']
    
    def test_block_dimensions(self, qapp, normal_block_data):
        """Test block has correct dimensions."""
        item = BlockItem(normal_block_data)
        rect = item.rect()
        
        assert rect.width() == 100
        assert rect.height() == 80
    
    def test_block_data_extraction(self, qapp, normal_block_data):
        """Test block data is correctly extracted."""
        item = BlockItem(normal_block_data)
        
        assert item.index == 5
        assert item.hash == 'abc123de'  # First 8 chars
        assert item.miner == 'node_001'
        assert item.tx_count == 3
    
    def test_text_items_created(self, qapp, normal_block_data):
        """Test all text items are created."""
        item = BlockItem(normal_block_data)
        
        assert item.index_text is not None
        assert item.hash_text is not None
        assert item.miner_text is not None
        assert item.tx_text is not None
        
        # Check text content
        assert str(item.index) in item.index_text.toPlainText()
        assert item.hash in item.hash_text.toPlainText()
        assert str(item.tx_count) in item.tx_text.toPlainText()
    
    def test_tooltip_setup(self, qapp, normal_block_data):
        """Test tooltip is set with block details."""
        item = BlockItem(normal_block_data)
        tooltip = item.toolTip()
        
        assert 'Block #5' in tooltip
        assert 'abc123def456789' in tooltip
        assert 'node_001' in tooltip
        assert 'Transactions: 3' in tooltip
    
    def test_selectable_flag(self, qapp, normal_block_data):
        """Test block is selectable."""
        item = BlockItem(normal_block_data)
        assert item.flags() & QGraphicsItem.ItemIsSelectable
    
    def test_hover_events_accepted(self, qapp, normal_block_data):
        """Test block accepts hover events."""
        item = BlockItem(normal_block_data)
        assert item.acceptHoverEvents()
    
    def test_get_block_data(self, qapp, normal_block_data):
        """Test getting block data."""
        item = BlockItem(normal_block_data)
        data = item.get_block_data()
        
        assert data == normal_block_data
        assert data['index'] == 5
        assert data['hash'] == 'abc123def456789'
    
    def test_update_data(self, qapp, normal_block_data, malicious_block_data):
        """Test updating block data."""
        item = BlockItem(normal_block_data)
        
        # Initial state
        assert item.index == 5
        assert item.block_type == 'normal'
        
        # Update to malicious block
        item.update_data(malicious_block_data)
        
        assert item.index == 10
        assert item.block_type == 'malicious'
        assert item.brush().color() == BlockItem.COLORS['malicious']
    
    def test_signal_proxy_exists(self, qapp, normal_block_data):
        """Test signal proxy is created."""
        item = BlockItem(normal_block_data)
        assert item._signal_proxy is not None
        assert isinstance(item._signal_proxy, BlockItemSignalProxy)
    
    def test_clicked_signal(self, qapp, normal_block_data):
        """Test clicked signal emission."""
        item = BlockItem(normal_block_data)
        signal_data = [None]
        
        def on_clicked(data):
            signal_data[0] = data
        
        item._signal_proxy.clicked.connect(on_clicked)
        
        # Emit signal directly
        item._signal_proxy.clicked.emit(normal_block_data)
        qapp.processEvents()
        
        assert signal_data[0] == normal_block_data
    
    def test_double_clicked_signal(self, qapp, normal_block_data):
        """Test double clicked signal emission."""
        item = BlockItem(normal_block_data)
        signal_data = [None]
        
        def on_double_clicked(data):
            signal_data[0] = data
        
        item._signal_proxy.double_clicked.connect(on_double_clicked)
        
        # Emit signal directly
        item._signal_proxy.double_clicked.emit(normal_block_data)
        qapp.processEvents()
        
        assert signal_data[0] == normal_block_data
    
    def test_color_mapping(self, qapp):
        """Test all block types have correct colors."""
        assert BlockItem.COLORS['genesis'] == QColor('#2196F3')
        assert BlockItem.COLORS['normal'] == QColor('#4CAF50')
        assert BlockItem.COLORS['malicious'] == QColor('#F44336')
        assert BlockItem.COLORS['orphan'] == QColor('#9E9E9E')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
