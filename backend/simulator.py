"""
Simulator Module - Blockchain network simülasyon motoru
"""
import asyncio
import time
import random
from typing import List, Dict
from backend.network.node import Node
from backend.network.message_broker import MessageBroker
from config import get_network_config, get_blockchain_config


class Simulator:
    """
    Blockchain network simülatörü
    
    Attributes:
        nodes (List[Node]): Tüm node'lar
        validator_nodes (List[Node]): Validator node'lar
        regular_nodes (List[Node]): Regular node'lar
        message_broker (MessageBroker): Node'lar arası mesajlaşma
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
        
        # MessageBroker oluştur
        self.message_broker = MessageBroker(min_delay=0.1, max_delay=0.3)
        
        # Auto-production task
        self._auto_production_task = None
        self._pbft_processing_task = None
        
        # Initialize nodes
        self.initialize_nodes()
    
    def initialize_nodes(self):
        """Config'e göre node'ları oluştur"""
        total_nodes = self.config['total_nodes']
        validator_count = self.config['validator_nodes']
        
        # Validator node'ları oluştur
        for i in range(validator_count):
            node = Node(
                role="validator",
                total_validators=validator_count,
                message_broker=self.message_broker
            )
            node.id = f"node_{i}"  # PBFT primary selection için sabit ID
            self.nodes.append(node)
            self.validator_nodes.append(node)
            self.message_broker.register_node(node.id)
        
        # Regular node'ları oluştur
        regular_count = total_nodes - validator_count
        for i in range(regular_count):
            node = Node(role="regular", message_broker=self.message_broker)
            self.nodes.append(node)
            self.regular_nodes.append(node)
            self.message_broker.register_node(node.id)
        
        print(f"✅ Initialized {total_nodes} nodes ({validator_count} validators, {regular_count} regular)")
        print(f"✅ MessageBroker configured with {len(self.message_broker.message_queues)} nodes")
    
    async def auto_block_production(self):
        """
        Otomatik blok üretimi - background task
        Validator'lar PBFT kullanır, Regular'lar mine eder
        """
        block_time = self.blockchain_config['block_time']
        
        while self.is_running:
            await asyncio.sleep(block_time)
            
            if not self.is_running:
                break
            
            # Validator'lar için PBFT blok önerisi
            if self.validator_nodes:
                # Primary validator blok önerir
                primary = None
                for validator in self.validator_nodes:
                    if validator.pbft and validator.pbft.is_primary() and validator.is_active:
                        primary = validator
                        break
                
                if primary:
                    # Primary blok önerir
                    try:
                        block = await primary.propose_block()
                        if block:
                            print(f"✓ Primary {primary.id} proposed block via PBFT")
                    except Exception as e:
                        print(f"⚠️  Error in block proposal: {e}")
            
            # Regular node'lar için klasik mining
            active_regular = [n for n in self.regular_nodes if n.is_active]
            if active_regular:
                miner = random.choice(active_regular)
                block = miner.mine_block()
                
                if block:
                    # Bloğu diğer regular node'lara yay
                    await self.broadcast_block(block, exclude_node=miner)
    
    async def pbft_message_processing(self):
        """
        PBFT mesajlarını periyodik olarak işle
        Background task
        """
        while self.is_running:
            await asyncio.sleep(0.5)  # Her 500ms'de bir mesaj işle
            
            if not self.is_running:
                break
            
            # Tüm validator'lar mesajlarını işler
            for validator in self.validator_nodes:
                if validator.is_active:
                    try:
                        await validator.process_pbft_messages()
                    except Exception as e:
                        print(f"⚠️  Error processing PBFT messages for {validator.id}: {e}")
    
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
        
        # Background task'leri durdur
        if self._auto_production_task:
            self._auto_production_task.cancel()
            self._auto_production_task = None
        
        if self._pbft_processing_task:
            self._pbft_processing_task.cancel()
            self._pbft_processing_task = None
        
        print("⏸️  Simulator stopped")
    
    def get_status(self):
        """
        Simülasyon durumunu döndür
        
        Returns:
            dict: Durum bilgileri
        """
        active_nodes = len([n for n in self.nodes if n.is_active])
        total_blocks = max([len(n.blockchain.chain) for n in self.nodes]) if self.nodes else 0
        
        # PBFT istatistikleri
        pbft_stats = {}
        if self.validator_nodes:
            primary_id = self.validator_nodes[0].pbft.get_primary_id() if self.validator_nodes[0].pbft else None
            total_consensus = sum(v.pbft.total_consensus_reached for v in self.validator_nodes if v.pbft)
            
            pbft_stats = {
                'primary_validator': primary_id,
                'total_consensus_reached': total_consensus,
                'current_view': self.validator_nodes[0].pbft.view if self.validator_nodes[0].pbft else 0
            }
        
        # MessageBroker istatistikleri
        broker_stats = self.message_broker.get_stats()
        
        return {
            'is_running': self.is_running,
            'total_nodes': len(self.nodes),
            'active_nodes': active_nodes,
            'validator_nodes': len(self.validator_nodes),
            'regular_nodes': len(self.regular_nodes),
            'total_blocks': total_blocks,
            'pbft': pbft_stats,
            'message_broker': broker_stats,
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
    
    def get_node(self, node_id):
        """
        ID'ye göre node bul (kısa alias)
        
        Args:
            node_id (str): Node ID
            
        Returns:
            Node: Bulunan node veya None
        """
        return self.get_node_by_id(node_id)
    
    def get_all_nodes_status(self):
        """
        Tüm node'ların durumunu döndür
        
        Returns:
            list: Node durumları
        """
        return [node.get_status() for node in self.nodes]
    
    def get_pbft_messages(self):
        """
        Tüm PBFT mesajlarını döndür (debug için)
        
        Returns:
            list: PBFT mesajları
        """
        all_messages = self.message_broker.get_all_messages()
        pbft_messages = [
            msg for msg in all_messages 
            if msg['message_type'] in ['pre_prepare', 'prepare', 'commit']
        ]
        return pbft_messages
    
    def _create_sybil_node(self, node_id: str):
        """
        Sahte Sybil node oluştur
        
        Args:
            node_id: Node ID
            
        Returns:
            Node: Oluşturulan sahte node
        """
        # Sahte node oluştur (regular role)
        node = Node(role="regular", message_broker=self.message_broker)
        node.id = node_id
        node.is_sybil = True  # Sybil bayrağını set et
        node.is_active = True
        
        # Listeye ekle
        self.nodes.append(node)
        self.regular_nodes.append(node)
        
        # MessageBroker'a kaydet
        self.message_broker.register_node(node.id)
        
        print(f"🔴 Sybil node created: {node_id}")
        return node
    
    def _remove_sybil_node(self, node_id: str):
        """
        Sahte Sybil node'u kaldır
        
        Args:
            node_id: Node ID
        """
        # Node'u bul
        node = self.get_node_by_id(node_id)
        if not node:
            return
        
        # Sadece Sybil node'ları kaldır
        if not node.is_sybil:
            print(f"⚠️  Node {node_id} is not a Sybil node")
            return
        
        # Listelerden çıkar
        if node in self.nodes:
            self.nodes.remove(node)
        if node in self.regular_nodes:
            self.regular_nodes.remove(node)
        
        # MessageBroker'dan kaldır
        self.message_broker.unregister_node(node_id)
        
        print(f"✓ Sybil node removed: {node_id}")
    
    def reset(self):
        """Simülasyonu sıfırla"""
        self.stop()
        
        # MessageBroker'ı temizle
        self.message_broker.clear_all_queues()
        
        # Node'ları temizle
        self.nodes.clear()
        self.validator_nodes.clear()
        self.regular_nodes.clear()
        
        # Yeniden başlat
        self.initialize_nodes()
        print("🔄 Simulator reset")
    
    def __repr__(self):
        """String representation"""
        status = "Running" if self.is_running else "Stopped"
        return f"Simulator({status} | {len(self.nodes)} nodes)"
