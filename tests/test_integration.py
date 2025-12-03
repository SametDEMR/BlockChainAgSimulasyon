"""
Integration Tests - Node+PBFT, Simulator+PBFT - Pytest Format
"""
import pytest
import asyncio
from backend.simulator import Simulator
from backend.network.node import Node
from backend.network.message_broker import MessageBroker


@pytest.mark.asyncio
class TestNodePBFTIntegration:
    """Node + PBFT entegrasyon testleri"""
    
    async def test_node_pbft_setup(self):
        """Node PBFT setup testi"""
        broker = MessageBroker(min_delay=0.01, max_delay=0.05)
        
        # 4 validator oluştur
        validators = []
        for i in range(4):
            node = Node(role="validator", total_validators=4, message_broker=broker)
            node.id = f"node_{i}"
            validators.append(node)
            broker.register_node(node.id)
        
        # Primary kontrolü
        primary = validators[0]
        assert primary.pbft.is_primary() is True
    
    async def test_pbft_propose_block(self):
        """PBFT blok önerisi testi"""
        broker = MessageBroker(min_delay=0.01, max_delay=0.05)
        validators = []
        
        for i in range(4):
            node = Node(role="validator", total_validators=4, message_broker=broker)
            node.id = f"node_{i}"
            validators.append(node)
            broker.register_node(node.id)
        
        primary = validators[0]
        
        # Blok öner
        block = await primary.propose_block()
        assert block is not None
    
    async def test_regular_vs_validator(self):
        """Regular vs Validator node karşılaştırma"""
        broker = MessageBroker()
        
        # Regular node - PBFT yok
        regular = Node(role="regular", message_broker=broker)
        assert regular.pbft is None
        
        # Validator node - PBFT var
        validator = Node(role="validator", total_validators=4, message_broker=broker)
        assert validator.pbft is not None


@pytest.mark.asyncio
class TestSimulatorPBFTIntegration:
    """Simulator + PBFT entegrasyon testleri"""
    
    async def test_simulator_pbft_initialization(self):
        """Simulator PBFT başlatma"""
        sim = Simulator()
        
        assert sim.message_broker is not None
        assert len(sim.validator_nodes) == 4
        
        # Her validator'ın PBFT'si var mı?
        for validator in sim.validator_nodes:
            assert validator.pbft is not None
    
    async def test_simulator_pbft_primary(self):
        """Simulator PBFT primary kontrolü"""
        sim = Simulator()
        sim.start()
        
        status = sim.get_status()
        
        assert 'pbft' in status
        assert 'primary_validator' in status['pbft']
        
        sim.stop()
    
    async def test_simulator_background_tasks(self):
        """Simulator background task'leri"""
        sim = Simulator()
        sim.start()
        
        # Task'leri başlat
        production_task = asyncio.create_task(sim.auto_block_production())
        pbft_task = asyncio.create_task(sim.pbft_message_processing())
        
        await asyncio.sleep(2)
        
        sim.stop()
        production_task.cancel()
        pbft_task.cancel()
        
        try:
            await production_task
        except asyncio.CancelledError:
            pass
        
        try:
            await pbft_task
        except asyncio.CancelledError:
            pass
        
        # Mesaj broker stats kontrolü
        stats = sim.message_broker.get_stats()
        assert stats is not None


class TestBlockchainFork:
    """Blockchain fork handling testleri"""
    
    def test_fork_detection(self, blockchain):
        """Fork detection testi"""
        # Ana zincir
        for _ in range(3):
            blockchain.mine_pending_transactions("Miner1")
        
        # Alternatif zincir oluştur
        alt_chain = blockchain.chain[:2].copy()
        
        # Fork detect
        fork_detected = blockchain.detect_fork(alt_chain)
        assert fork_detected is True
    
    def test_fork_resolution(self, blockchain):
        """Fork resolution testi - longest chain wins"""
        # Ana zincir
        for _ in range(2):
            blockchain.mine_pending_transactions("Miner1")
        
        # Daha uzun alternatif zincir
        from backend.core.block import Block
        import time
        
        alt_chain = blockchain.chain[:1].copy()
        for i in range(5):
            last_block = alt_chain[-1]
            new_block = Block(
                index=len(alt_chain),
                timestamp=time.time(),
                transactions=[],
                previous_hash=last_block.hash,
                miner=f"Miner{i}"
            )
            new_block.mine_block(blockchain.difficulty)
            alt_chain.append(new_block)
        
        # Fork çözümle
        resolved = blockchain.resolve_fork(alt_chain)
        assert resolved is True
        assert len(blockchain.chain) == len(alt_chain)
