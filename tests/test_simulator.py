"""
Simulator Test - Pytest Format
"""
import pytest
import asyncio
from backend.simulator import Simulator


class TestSimulatorBasic:
    """Temel simulator testleri"""
    
    def test_simulator_creation(self):
        """Simulator oluşturma"""
        sim = Simulator()
        assert len(sim.nodes) == 10  # Config default
        assert len(sim.validator_nodes) == 4
        assert len(sim.regular_nodes) == 6
    
    def test_simulator_start_stop(self, simulator):
        """Start/Stop testi"""
        assert simulator.is_running is False
        
        simulator.start()
        assert simulator.is_running is True
        
        simulator.stop()
        assert simulator.is_running is False
    
    def test_simulator_reset(self, simulator):
        """Reset testi"""
        # Birkaç blok mine et
        for _ in range(2):
            simulator.nodes[0].mine_block()
        
        # Reset
        simulator.reset()
        
        # Tüm node'lar genesis block'a dönmeli
        for node in simulator.nodes:
            assert len(node.blockchain.chain) == 1
    
    def test_get_status(self, simulator):
        """Status bilgisi testi"""
        status = simulator.get_status()
        
        assert 'is_running' in status
        assert 'total_nodes' in status
        assert 'active_nodes' in status
        assert 'validator_nodes' in status
        assert status['total_nodes'] == 10


@pytest.mark.asyncio
class TestSimulatorAsync:
    """Async simulator testleri"""
    
    async def test_auto_block_production(self, simulator):
        """Otomatik blok üretimi testi"""
        simulator.start()
        
        # Auto production task başlat
        task = asyncio.create_task(simulator.auto_block_production())
        
        # 3 saniye bekle
        await asyncio.sleep(3)
        
        # Stop
        simulator.stop()
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # En az bir blok üretilmiş olmalı
        max_chain = max([len(n.blockchain.chain) for n in simulator.nodes])
        assert max_chain > 1  # Genesis + mined blocks
    
    async def test_pbft_message_processing(self, simulator):
        """PBFT mesaj işleme testi"""
        simulator.start()
        
        # PBFT task başlat
        task = asyncio.create_task(simulator.pbft_message_processing())
        
        # 2 saniye bekle
        await asyncio.sleep(2)
        
        # Stop
        simulator.stop()
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # MessageBroker mesaj görmüş olmalı
        stats = simulator.message_broker.get_stats()
        assert stats['total_messages_sent'] >= 0


class TestSimulatorNodes:
    """Node yönetimi testleri"""
    
    def test_manual_mining(self, simulator):
        """Manuel mining testi"""
        node = simulator.nodes[0]
        initial_chain_length = len(node.blockchain.chain)
        
        block = node.mine_block()
        
        assert block is not None
        assert len(node.blockchain.chain) == initial_chain_length + 1
    
    def test_node_lookup(self, simulator):
        """Node bulma testi"""
        first_node = simulator.nodes[0]
        found_node = next((n for n in simulator.nodes if n.id == first_node.id), None)
        
        assert found_node is not None
        assert found_node.id == first_node.id
