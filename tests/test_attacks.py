"""
Attack Tests - Pytest Format
Byzantine, DDoS, Sybil, Majority, Partition, Selfish Mining
"""
import pytest
import asyncio
from backend.simulator import Simulator
from backend.attacks.attack_engine import AttackEngine, AttackType
from backend.attacks.ddos import DDoSAttack
from backend.attacks.byzantine import ByzantineAttack
from backend.attacks.sybil import SybilAttack
from backend.attacks.majority_attack import MajorityAttack
from backend.attacks.network_partition import NetworkPartition
from backend.attacks.selfish_mining import SelfishMining
from backend.network.node import Node


class TestAttackEngine:
    """Attack Engine testleri"""
    
    def test_attack_engine_creation(self):
        """Attack engine oluşturma"""
        engine = AttackEngine()
        stats = engine.get_statistics()
        assert stats['total_attacks_triggered'] == 0
        assert stats['active_attacks_count'] == 0
    
    def test_trigger_attack(self, attack_engine):
        """Saldırı tetikleme"""
        attack_id = attack_engine.trigger_attack(
            attack_type=AttackType.DDOS,
            target="node_5",
            parameters={"intensity": "high"}
        )
        assert attack_id is not None
        
        status = attack_engine.get_attack_status(attack_id)
        assert status['attack_type'] == 'ddos'
        assert status['target'] == 'node_5'
    
    def test_stop_attack(self, attack_engine):
        """Saldırı durdurma"""
        attack_id = attack_engine.trigger_attack(
            attack_type=AttackType.DDOS,
            target="node_5",
            parameters={}
        )
        
        success = attack_engine.stop_attack(attack_id)
        assert success is True
        
        status = attack_engine.get_attack_status(attack_id)
        assert status['status'] == 'completed'


@pytest.mark.asyncio
class TestDDoSAttack:
    """DDoS Attack testleri"""
    
    async def test_ddos_execution(self, attack_engine):
        """DDoS saldırı yürütme"""
        node = Node(role="regular", total_validators=4, message_broker=None)
        initial_response_time = node.response_time
        
        ddos = DDoSAttack(
            target_node=node,
            attack_engine=attack_engine,
            intensity="high"
        )
        
        attack_id = await ddos.execute()
        assert attack_id is not None
        assert node.response_time > initial_response_time
        assert node.status == "under_attack"
    
    async def test_ddos_stop(self, attack_engine):
        """DDoS durdurma"""
        node = Node(role="regular", total_validators=4, message_broker=None)
        
        ddos = DDoSAttack(node, attack_engine, "medium")
        await ddos.execute()
        
        ddos.stop()
        await asyncio.sleep(0.5)
        
        assert node.status in ["healthy", "recovering"]


@pytest.mark.asyncio
class TestByzantineAttack:
    """Byzantine Attack testleri"""
    
    async def test_byzantine_trigger(self, simulator):
        """Byzantine saldırı tetikleme"""
        byzantine = ByzantineAttack(simulator)
        target = simulator.validator_nodes[0]
        initial_trust = target.trust_score
        
        result = byzantine.trigger(target.id)
        
        assert result["success"] is True
        assert target.is_byzantine is True
        assert target.trust_score < initial_trust


@pytest.mark.asyncio
class TestSybilAttack:
    """Sybil Attack testleri"""
    
    async def test_sybil_trigger(self, simulator):
        """Sybil saldırı tetikleme"""
        sybil = SybilAttack(simulator)
        initial_node_count = len(simulator.nodes)
        
        result = await sybil.trigger(num_nodes=10)
        
        assert result is True
        assert len(simulator.nodes) == initial_node_count + 10
        
        # Sybil node'ları kontrol
        sybil_nodes = [n for n in simulator.nodes if n.is_sybil]
        assert len(sybil_nodes) == 10
    
    async def test_sybil_stop(self, simulator):
        """Sybil saldırı durdurma"""
        sybil = SybilAttack(simulator)
        await sybil.trigger(num_nodes=5)
        initial_count = len(simulator.nodes)
        
        await sybil.stop()
        
        # Sybil node'lar temizlenmeli
        assert len(simulator.nodes) < initial_count
        sybil_nodes = [n for n in simulator.nodes if n.is_sybil]
        assert len(sybil_nodes) == 0


class TestMajorityAttack:
    """Majority Attack testleri"""
    
    def test_majority_execute(self, simulator):
        """Majority saldırı yürütme"""
        majority = MajorityAttack(simulator)
        
        result = majority.execute()
        
        assert result["success"] is True
        
        # Validator'ların %51'i malicious olmalı
        malicious = [v for v in simulator.validator_nodes if v.is_malicious]
        assert len(malicious) >= len(simulator.validator_nodes) * 0.51


class TestNetworkPartition:
    """Network Partition testleri"""
    
    def test_partition_execute(self, simulator):
        """Partition saldırı yürütme"""
        partition = NetworkPartition(simulator)
        
        result = partition.execute()
        
        assert result["success"] is True
        
        # Partition status kontrolü
        broker_status = simulator.message_broker.get_partition_status()
        assert broker_status['active'] is True


@pytest.mark.asyncio
class TestSelfishMining:
    """Selfish Mining testleri"""
    
    async def test_selfish_mining_trigger(self, simulator):
        """Selfish mining tetikleme"""
        if not simulator.regular_nodes:
            pytest.skip("No regular nodes available")
        
        selfish = SelfishMining(simulator)
        target = simulator.regular_nodes[0]
        
        result = selfish.trigger(target.id)
        
        assert result["success"] is True
        assert target.is_selfish_miner is True
        assert target.private_chain is not None
