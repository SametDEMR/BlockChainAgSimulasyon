"""
PBFT Handler Test - Pytest Format
"""
import pytest
from backend.network.pbft_handler import PBFTHandler, PBFTMessage


class TestPBFTHandler:
    """PBFT Handler temel testleri"""
    
    @pytest.fixture
    def handlers(self):
        """4 validator için PBFT handler'lar"""
        total_validators = 4
        handlers_dict = {}
        for i in range(total_validators):
            node_id = f"node_{i}"
            handler = PBFTHandler(node_id, total_validators)
            handlers_dict[node_id] = handler
        return handlers_dict
    
    def test_pbft_handler_creation(self):
        """PBFT handler oluşturma"""
        handler = PBFTHandler("node_0", 4)
        assert handler.node_id == "node_0"
        assert handler.total_validators == 4
        assert handler.f == 1  # (4-1)/3 = 1
        assert handler.required_votes == 3  # 2*1 + 1
    
    def test_primary_selection(self, handlers):
        """Primary validator seçimi"""
        primary_id = handlers['node_0'].get_primary_id()
        assert primary_id == 'node_0'
        
        # node_0 primary olmalı
        assert handlers['node_0'].is_primary() is True
        assert handlers['node_1'].is_primary() is False
    
    def test_pre_prepare_phase(self, handlers):
        """Pre-prepare fazı"""
        primary = handlers['node_0']
        block_hash = "test_hash_123"
        sequence = 1
        
        pre_prepare_msg = primary.create_pre_prepare(block_hash, sequence)
        
        assert pre_prepare_msg.phase == 'pre_prepare'
        assert pre_prepare_msg.block_hash == block_hash
        assert pre_prepare_msg.sequence_number == sequence
        assert pre_prepare_msg.node_id == 'node_0'
    
    def test_prepare_phase(self, handlers):
        """Prepare fazı"""
        primary = handlers['node_0']
        pre_prepare = primary.create_pre_prepare("hash123", 1)
        
        # Diğer validator'lar prepare mesajları oluşturur
        prepare_messages = []
        for node_id, handler in handlers.items():
            if node_id != 'node_0':
                prepare = handler.process_pre_prepare(pre_prepare)
                if prepare:
                    prepare_messages.append(prepare)
        
        assert len(prepare_messages) == 3  # 4 validator - 1 primary
    
    def test_commit_phase(self, handlers):
        """Commit fazı"""
        primary = handlers['node_0']
        pre_prepare = primary.create_pre_prepare("hash123", 1)
        
        # Prepare'ları topla
        prepare_messages = []
        for node_id, handler in handlers.items():
            if node_id != 'node_0':
                prepare = handler.process_pre_prepare(pre_prepare)
                if prepare:
                    prepare_messages.append(prepare)
        
        # Commit'leri topla
        commit_messages = []
        for handler in handlers.values():
            for prepare in prepare_messages:
                commit = handler.process_prepare(prepare)
                if commit and commit.node_id not in [m.node_id for m in commit_messages]:
                    commit_messages.append(commit)
        
        assert len(commit_messages) >= 3  # En az 3 commit (2f+1)
    
    def test_consensus_reached(self, handlers):
        """Konsensüs sağlanma testi"""
        block_hash = "hash123"
        sequence = 1
        
        # Pre-prepare
        primary = handlers['node_0']
        pre_prepare = primary.create_pre_prepare(block_hash, sequence)
        
        # Prepare
        prepare_messages = []
        for node_id, handler in handlers.items():
            if node_id != 'node_0':
                prepare = handler.process_pre_prepare(pre_prepare)
                if prepare:
                    prepare_messages.append(prepare)
        
        # Commit
        commit_messages = []
        for handler in handlers.values():
            for prepare in prepare_messages:
                commit = handler.process_prepare(prepare)
                if commit and commit.node_id not in [m.node_id for m in commit_messages]:
                    commit_messages.append(commit)
        
        # Consensus check
        consensus_count = 0
        for handler in handlers.values():
            for commit in commit_messages:
                if handler.process_commit(commit):
                    consensus_count += 1
                    break
        
        assert consensus_count >= 3  # En az 3 node konsensüs sağlamalı
    
    def test_view_change(self, handlers):
        """View change testi"""
        handler = handlers['node_1']
        
        view_changed = handler.trigger_view_change("timeout")
        assert view_changed is True
        assert handler.view == 1
    
    def test_stats(self, handlers):
        """PBFT istatistikleri"""
        handler = handlers['node_0']
        stats = handler.get_stats()
        
        assert 'view' in stats
        assert 'sequence_number' in stats
        assert 'is_primary' in stats
        assert 'total_consensus_reached' in stats


class TestPBFTByzantine:
    """Byzantine senaryo testleri"""
    
    @pytest.fixture
    def handlers(self):
        """4 validator için handler'lar"""
        return {f"node_{i}": PBFTHandler(f"node_{i}", 4) for i in range(4)}
    
    def test_byzantine_node_fake_hash(self, handlers):
        """Byzantine node yanlış hash gönderir"""
        primary = handlers['node_0']
        pre_prepare = primary.create_pre_prepare("correct_hash", 1)
        
        # TÜM handler'lar pre-prepare'i işler ve prepare mesajı üretir
        prepare_messages = []
        for node_id, handler in handlers.items():
            if node_id == 'node_0':  # Primary prepare göndermiyor
                continue
            
            prepare = handler.process_pre_prepare(pre_prepare)
            if prepare:
                # node_2 Byzantine - yanlış hash gönderir
                if node_id == 'node_2':
                    prepare.block_hash = "wrong_hash"
                prepare_messages.append(prepare)
        
        # Prepare mesajlarını say
        correct_prepares = sum(1 for p in prepare_messages if p.block_hash == "correct_hash")
        wrong_prepares = sum(1 for p in prepare_messages if p.block_hash == "wrong_hash")
        
        # Byzantine node tek başına etkisiz olmalı
        # 3 prepare: 2 correct (node_1, node_3), 1 wrong (node_2)
        assert correct_prepares == 2
        assert wrong_prepares == 1
        assert correct_prepares > wrong_prepares
