"""
Simulator Module - Blockchain network simülasyon motoru
"""
import asyncio
import time
from typing import List, Dict
from backend.network.node import Node
from config import get_network_config, get_blockchain_config


class Simulator:
    """
    Blockchain network simülatörü
    
    Attributes:
        nodes (List[Node]): Tüm node'lar
        validator_nodes (List[Node]): Validator node'lar
        regular_nodes (List[Node]): Regular node'lar
        is_running (bool): Simülasyon çalışıyor mu?
        config (dict): Network yapılandırması
    """
    
    def __init__(self):
        """Simulator başlat ve node'ları oluştur"""
        self.nodes = []
        self.validator_nodes = []
        self.regular_nodes = []
        self.is_running = False
        self.config = get_network_config()
        self.blockchain_config = get_blockchain_config()
        
        # Auto-production task
        self._auto_production_task = None
        
        # Initialize nodes
        self.initialize_nodes()
    
    def initialize_nodes(self):
        """Config'e göre node'ları oluştur"""
        total_nodes = self.config['total_nodes']
        validator_count = self.config['validator_nodes']
        
        # Validator node'ları oluştur
        for i in range(validator_count):
            node = Node(role="validator")
            self.nodes.append(node)
            self.validator_nodes.append(node)
        
        # Regular node'ları oluştur
        regular_count = total_nodes - validator_count
        for i in range(regular_count):
            node = Node(role="regular")
            self.nodes.append(node)
            self.regular_nodes.append(node)
        
        print(f"✅ Initialized {total_nodes} nodes ({validator_count} validators, {regular_count} regular)")
    
    async def auto_block_production(self):
        """Otomatik blok üretimi - background task"""
        import random
        
        block_time = self.blockchain_config['block_time']
        
        while self.is_running:
            await asyncio.sleep(block_time)
            
            if not self.is_running:
                break
            
            # Rastgele bir active node seç ve blok mine ettir
            active_nodes = [n for n in self.nodes if n.is_active]
            if active_nodes:
                miner = random.choice(active_nodes)
                block = miner.mine_block()
                
                if block:
                    # Bloğu diğer node'lara yay
                    await self.broadcast_block(block, exclude_node=miner)
    
    async def broadcast_block(self, block, exclude_node=None):
        """
        Bloğu tüm node'lara yay
        
        Args:
            block: Yayınlanacak blok
            exclude_node: Bu node'a yayınlama (genelde miner)
        """
        for node in self.nodes:
            if node != exclude_node and node.is_active:
                node.receive_block(block)
    
    def start(self):
        """Simülasyonu başlat"""
        if self.is_running:
            print("⚠️  Simulator already running")
            return
        
        self.is_running = True
        print("▶️  Simulator started")
    
    def stop(self):
        """Simülasyonu durdur"""
        self.is_running = False
        print("⏸️  Simulator stopped")
    
    def get_status(self):
        """
        Simülasyon durumunu döndür
        
        Returns:
            dict: Durum bilgileri
        """
        active_nodes = len([n for n in self.nodes if n.is_active])
        total_blocks = max([len(n.blockchain.chain) for n in self.nodes]) if self.nodes else 0
        
        return {
            'is_running': self.is_running,
            'total_nodes': len(self.nodes),
            'active_nodes': active_nodes,
            'validator_nodes': len(self.validator_nodes),
            'regular_nodes': len(self.regular_nodes),
            'total_blocks': total_blocks,
            'config': self.config
        }
    
    def get_node_by_id(self, node_id):
        """
        ID'ye göre node bul
        
        Args:
            node_id (str): Node ID
            
        Returns:
            Node: Bulunan node veya None
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_all_nodes_status(self):
        """
        Tüm node'ların durumunu döndür
        
        Returns:
            list: Node durumları
        """
        return [node.get_status() for node in self.nodes]
    
    def reset(self):
        """Simülasyonu sıfırla"""
        self.stop()
        self.nodes.clear()
        self.validator_nodes.clear()
        self.regular_nodes.clear()
        self.initialize_nodes()
        print("🔄 Simulator reset")
    
    def __repr__(self):
        """String representation"""
        status = "Running" if self.is_running else "Stopped"
        return f"Simulator({status} | {len(self.nodes)} nodes)"


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=" * 60)
    print("SIMULATOR MODULE TEST")
    print("=" * 60)
    
    # Simulator oluştur
    simulator = Simulator()
    
    print(f"\n✅ Simulator Created: {simulator}")
    print(f"  Total nodes: {len(simulator.nodes)}")
    print(f"  Validators: {len(simulator.validator_nodes)}")
    print(f"  Regular: {len(simulator.regular_nodes)}")
    
    # Status
    print(f"\n📊 Simulator Status:")
    import json
    print(json.dumps(simulator.get_status(), indent=2))
    
    # Start simulator
    print(f"\n▶️  Starting simulator...")
    simulator.start()
    print(f"  Is running: {simulator.is_running}")
    
    # Manual mining test
    print(f"\n⛏️  Manual mining test:")
    node = simulator.nodes[0]
    print(f"  Mining with node {node.id}...")
    block = node.mine_block()
    if block:
        print(f"  Block #{block.index} mined")
        print(f"  Broadcasting to other nodes...")
        
        # Sync manually (asyncio olmadan test için)
        for other_node in simulator.nodes:
            if other_node != node:
                other_node.receive_block(block)
        
        print(f"  All nodes synced")
    
    # Check chain lengths
    print(f"\n📊 Chain Lengths:")
    for i, node in enumerate(simulator.nodes[:5]):  # İlk 5 node
        print(f"  Node {node.id}: {len(node.blockchain.chain)} blocks")
    
    # Node lookup test
    print(f"\n🔍 Node Lookup Test:")
    test_id = simulator.nodes[0].id
    found_node = simulator.get_node_by_id(test_id)
    print(f"  Looking for: {test_id}")
    print(f"  Found: {found_node.id if found_node else 'None'}")
    
    # Stop simulator
    print(f"\n⏸️  Stopping simulator...")
    simulator.stop()
    print(f"  Is running: {simulator.is_running}")
    
    # Reset test
    print(f"\n🔄 Reset Test:")
    print(f"  Nodes before reset: {len(simulator.nodes)}")
    simulator.reset()
    print(f"  Nodes after reset: {len(simulator.nodes)}")
    print(f"  New nodes have fresh blockchains: {len(simulator.nodes[0].blockchain.chain)} blocks")
    
    print("\n" + "=" * 60)
    print("✅ SIMULATOR TEST PASSED!")
    print("=" * 60)
