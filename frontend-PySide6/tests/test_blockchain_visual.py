"""Test blockchain rendering with sample data."""
import sys
from PySide6.QtWidgets import QApplication
from ui.pages.blockchain_page import BlockchainExplorerPage
from core.data_manager import DataManager
from core.api_client import APIClient
from unittest.mock import Mock

app = QApplication(sys.argv)

# Mock API
mock_api = Mock()
mock_api.is_connected.return_value = True

# Create data manager
data_manager = DataManager(mock_api)

# Create page
page = BlockchainExplorerPage(data_manager)

# Test blockchain data
test_blockchain = {
    'chain_length': 3,
    'pending_transactions': 0,
    'blocks': [
        {
            'index': 0,
            'hash': 'genesis_hash_123',
            'previous_hash': '0',
            'miner_id': 'genesis',
            'transaction_count': 0,
            'timestamp': '2024-01-01 00:00:00',
            'is_orphan': False,
            'is_malicious': False,
            'nonce': 0,
            'transactions': []
        },
        {
            'index': 1,
            'hash': 'block1_hash_456',
            'previous_hash': 'genesis_hash_123',
            'miner_id': 'node_001',
            'transaction_count': 2,
            'timestamp': '2024-01-01 01:00:00',
            'is_orphan': False,
            'is_malicious': False,
            'nonce': 12345,
            'transactions': []
        },
        {
            'index': 2,
            'hash': 'block2_hash_789',
            'previous_hash': 'block1_hash_456',
            'miner_id': 'node_002',
            'transaction_count': 1,
            'timestamp': '2024-01-01 02:00:00',
            'is_orphan': False,
            'is_malicious': False,
            'nonce': 67890,
            'transactions': []
        }
    ]
}

# Render
print("Rendering blockchain...")
page._render_blockchain(test_blockchain)
print(f"Scene items count: {len(page.graph_widget.scene.items())}")

# Show
page.show()
page.resize(1200, 600)

sys.exit(app.exec())
