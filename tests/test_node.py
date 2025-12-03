"""
Node Module Test - Pytest Format
"""
import pytest
from backend.network.node import Node


class TestNode:
    """Node modülü testleri"""
    
    def test_node_creation_regular(self):
        """Regular node oluşturma"""
        node = Node(role="regular")
        assert node.role == "regular"
        assert node.is_active is True
        assert node.status == "healthy"
        assert node.pbft is None  # Regular node PBFT yok
    
    def test_node_creation_validator(self, message_broker):
        """Validator node oluşturma"""
        node = Node(role="validator", total_validators=4, message_broker=message_broker)
        assert node.role == "validator"
        assert node.pbft is not None  # Validator PBFT var
    
    def test_node_mining(self, node):
        """Node mining testi"""
        block = node.mine_block()
        assert block is not None
        assert block.index > 0
        assert node.blocks_mined == 1
    
    def test_node_transaction_creation(self):
        """Transaction oluşturma testi"""
        node1 = Node(role="regular")
        node2 = Node(role="regular")
        
        # İlk mining (reward için)
        node1.mine_block()
        
        # Transaction oluştur
        tx = node1.create_transaction(node2.wallet.address, 25)
        assert tx is not None
        assert tx.amount == 25
        assert len(node1.blockchain.pending_transactions) == 1
    
    def test_node_sync(self):
        """Blockchain senkronizasyonu testi"""
        node1 = Node(role="regular")
        node2 = Node(role="regular")
        
        # node1 birkaç blok mine et
        for _ in range(3):
            node1.mine_block()
        
        # node2 sync yap
        initial_length = len(node2.blockchain.chain)
        node2.sync_blockchain(node1.blockchain)
        
        assert len(node2.blockchain.chain) > initial_length
        assert len(node2.blockchain.chain) == len(node1.blockchain.chain)
    
    def test_node_metrics(self, node):
        """Node metrics testi"""
        metrics = node.get_metrics()
        
        assert 'cpu_usage' in metrics
        assert 'memory_usage' in metrics
        assert 'response_time' in metrics
        assert 'trust_score' in metrics
        assert metrics['trust_score'] == 100  # Initial
    
    def test_node_byzantine_flag(self, node):
        """Byzantine flag testi"""
        assert node.is_byzantine is False
        
        node.set_byzantine(True)
        assert node.is_byzantine is True
        assert node.status == "under_attack"
    
    def test_node_under_attack(self, node):
        """Under attack status testi"""
        initial_response_time = node.response_time
        
        node.set_under_attack()
        
        assert node.status == "under_attack"
        assert node.response_time > initial_response_time
    
    def test_node_recovery(self, node):
        """Recovery testi"""
        node.set_under_attack()
        assert node.status == "under_attack"
        
        node.recover()
        
        assert node.status == "healthy"
        assert node.response_time == 50.0  # Default value


class TestNodeStatus:
    """Node status fonksiyonları testi"""
    
    def test_get_status(self, node):
        """get_status() testi"""
        status = node.get_status()
        
        assert 'id' in status
        assert 'role' in status
        assert 'status' in status
        assert 'metrics' in status
        assert 'chain_length' in status
        assert status['is_active'] is True
