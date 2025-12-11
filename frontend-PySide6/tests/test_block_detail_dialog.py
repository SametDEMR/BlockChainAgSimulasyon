"""Tests for Block Detail Dialog."""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import sys

from ui.dialogs.block_detail_dialog import BlockDetailDialog


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def block_data():
    """Create sample block data."""
    return {
        'index': 5,
        'hash': 'abc123def456',
        'previous_hash': 'prev_hash_123',
        'miner_id': 'node_001',
        'timestamp': '2024-01-01 12:00:00',
        'nonce': 12345,
        'transaction_count': 2,
        'is_orphan': False,
        'is_malicious': False,
        'transactions': [
            {
                'from': 'alice',
                'to': 'bob',
                'amount': 10.5,
                'timestamp': '2024-01-01 11:59:00'
            },
            {
                'from': 'bob',
                'to': 'charlie',
                'amount': 5.25,
                'timestamp': '2024-01-01 11:59:30'
            }
        ]
    }


@pytest.fixture
def all_blocks():
    """Create list of blocks for navigation."""
    return [
        {'index': 0, 'hash': 'genesis'},
        {'index': 1, 'hash': 'block1'},
        {'index': 2, 'hash': 'block2'},
        {'index': 3, 'hash': 'block3'},
        {'index': 4, 'hash': 'block4'},
        {'index': 5, 'hash': 'abc123def456'},
        {'index': 6, 'hash': 'block6'},
    ]


class TestBlockDetailDialog:
    """Test suite for BlockDetailDialog."""
    
    def test_initialization(self, qapp, block_data):
        """Test dialog initializes correctly."""
        dialog = BlockDetailDialog(block_data)
        assert dialog is not None
        assert dialog.block_data == block_data
    
    def test_window_title(self, qapp, block_data):
        """Test window title is set."""
        dialog = BlockDetailDialog(block_data)
        assert dialog.windowTitle() == "Block Details"
    
    def test_block_info_labels_exist(self, qapp, block_data):
        """Test all block info labels exist."""
        dialog = BlockDetailDialog(block_data)
        
        assert dialog.lbl_index is not None
        assert dialog.lbl_hash is not None
        assert dialog.lbl_prev_hash is not None
        assert dialog.lbl_miner is not None
        assert dialog.lbl_timestamp is not None
        assert dialog.lbl_tx_count is not None
        assert dialog.lbl_nonce is not None
        assert dialog.lbl_status is not None
    
    def test_block_info_populated(self, qapp, block_data):
        """Test block info is populated correctly."""
        dialog = BlockDetailDialog(block_data)
        
        assert dialog.lbl_index.text() == '5'
        assert dialog.lbl_hash.text() == 'abc123def456'
        assert dialog.lbl_prev_hash.text() == 'prev_hash_123'
        assert dialog.lbl_miner.text() == 'node_001'
        assert dialog.lbl_timestamp.text() == '2024-01-01 12:00:00'
        assert dialog.lbl_nonce.text() == '12345'
        assert dialog.lbl_tx_count.text() == '2'
    
    def test_status_normal(self, qapp, block_data):
        """Test normal block status."""
        dialog = BlockDetailDialog(block_data)
        assert 'Normal' in dialog.lbl_status.text()
    
    def test_status_orphan(self, qapp, block_data):
        """Test orphan block status."""
        block_data['is_orphan'] = True
        dialog = BlockDetailDialog(block_data)
        assert 'Orphan' in dialog.lbl_status.text()
    
    def test_status_malicious(self, qapp, block_data):
        """Test malicious block status."""
        block_data['is_malicious'] = True
        dialog = BlockDetailDialog(block_data)
        assert 'Malicious' in dialog.lbl_status.text()
    
    def test_status_genesis(self, qapp):
        """Test genesis block status."""
        genesis_data = {
            'index': 0,
            'hash': 'genesis',
            'previous_hash': '0',
            'miner_id': 'genesis',
            'timestamp': '2024-01-01 00:00:00',
            'nonce': 0,
            'is_orphan': False,
            'is_malicious': False,
            'transactions': []
        }
        dialog = BlockDetailDialog(genesis_data)
        assert 'Genesis' in dialog.lbl_status.text()
    
    def test_transaction_table_exists(self, qapp, block_data):
        """Test transaction table is created."""
        dialog = BlockDetailDialog(block_data)
        assert dialog.tx_table is not None
        assert dialog.tx_table.columnCount() == 4
    
    def test_transactions_populated(self, qapp, block_data):
        """Test transactions are populated in table."""
        dialog = BlockDetailDialog(block_data)
        
        assert dialog.tx_table.rowCount() == 2
        
        # Check first transaction
        assert dialog.tx_table.item(0, 0).text() == 'alice'
        assert dialog.tx_table.item(0, 1).text() == 'bob'
        assert '10.5' in dialog.tx_table.item(0, 2).text()
        
        # Check second transaction
        assert dialog.tx_table.item(1, 0).text() == 'bob'
        assert dialog.tx_table.item(1, 1).text() == 'charlie'
        assert '5.25' in dialog.tx_table.item(1, 2).text()
    
    def test_empty_transactions(self, qapp, block_data):
        """Test handling of empty transactions."""
        block_data['transactions'] = []
        dialog = BlockDetailDialog(block_data)
        
        assert dialog.tx_table.rowCount() == 0
        assert dialog.lbl_tx_count.text() == '0'
    
    def test_navigation_buttons_exist(self, qapp, block_data):
        """Test navigation buttons exist."""
        dialog = BlockDetailDialog(block_data)
        
        assert dialog.btn_prev is not None
        assert dialog.btn_next is not None
        assert dialog.btn_close is not None
    
    def test_navigation_without_blocks(self, qapp, block_data):
        """Test navigation buttons disabled without all_blocks."""
        dialog = BlockDetailDialog(block_data)
        
        assert not dialog.btn_prev.isEnabled()
        assert not dialog.btn_next.isEnabled()
    
    def test_navigation_with_blocks(self, qapp, block_data, all_blocks):
        """Test navigation buttons enabled with all_blocks."""
        dialog = BlockDetailDialog(block_data, all_blocks)
        
        # Should be able to navigate both ways from index 5
        assert dialog.btn_prev.isEnabled()
        assert dialog.btn_next.isEnabled()
    
    def test_navigation_at_genesis(self, qapp, all_blocks):
        """Test navigation at genesis block."""
        genesis = all_blocks[0]
        dialog = BlockDetailDialog(genesis, all_blocks)
        
        assert not dialog.btn_prev.isEnabled()
        assert dialog.btn_next.isEnabled()
    
    def test_navigation_at_end(self, qapp, all_blocks):
        """Test navigation at last block."""
        last_block = all_blocks[-1]
        dialog = BlockDetailDialog(last_block, all_blocks)
        
        assert dialog.btn_prev.isEnabled()
        assert not dialog.btn_next.isEnabled()
    
    def test_navigate_previous_signal(self, qapp, block_data, all_blocks):
        """Test navigate to previous block."""
        dialog = BlockDetailDialog(block_data, all_blocks)
        signal_data = [None]
        
        def on_navigate(block_hash):
            signal_data[0] = block_hash
        
        dialog.navigate_to_block.connect(on_navigate)
        dialog.btn_prev.click()
        qapp.processEvents()
        
        assert signal_data[0] == 'block4'
    
    def test_navigate_next_signal(self, qapp, block_data, all_blocks):
        """Test navigate to next block."""
        dialog = BlockDetailDialog(block_data, all_blocks)
        signal_data = [None]
        
        def on_navigate(block_hash):
            signal_data[0] = block_hash
        
        dialog.navigate_to_block.connect(on_navigate)
        dialog.btn_next.click()
        qapp.processEvents()
        
        assert signal_data[0] == 'block6'
    
    def test_update_block_data(self, qapp, block_data, all_blocks):
        """Test updating dialog with new block data."""
        dialog = BlockDetailDialog(block_data, all_blocks)
        
        new_block = {
            'index': 10,
            'hash': 'new_hash',
            'previous_hash': 'prev',
            'miner_id': 'node_002',
            'timestamp': '2024-01-02 00:00:00',
            'nonce': 99999,
            'is_orphan': False,
            'is_malicious': False,
            'transactions': []
        }
        
        dialog.update_block_data(new_block)
        
        assert dialog.lbl_index.text() == '10'
        assert dialog.lbl_hash.text() == 'new_hash'
        assert dialog.lbl_miner.text() == 'node_002'
    
    def test_hash_selectable(self, qapp, block_data):
        """Test hash labels are selectable."""
        dialog = BlockDetailDialog(block_data)
        
        flags = dialog.lbl_hash.textInteractionFlags()
        assert flags & Qt.TextSelectableByMouse
        
        flags = dialog.lbl_prev_hash.textInteractionFlags()
        assert flags & Qt.TextSelectableByMouse


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
