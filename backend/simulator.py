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
        
        # İlk node'u oluştur ve genesis block'unu al
        first_node = Node(
            role="validator",
            total_validators=validator_count,
            message_broker=self.message_broker,
            node_id=f"node_0"
        )
        first_node.id = f"node_0"
        genesis_chain = first_node.blockchain.chain.copy()  # Genesis block'u kaydet
        
        self.nodes.append(first_node)
        self.validator_nodes.append(first_node)
        self.message_broker.register_node(first_node.id)
        
        # Diğer validator node'ları oluştur (aynı genesis ile)
        for i in range(1, validator_count):
            node = Node(
                role="validator",
                total_validators=validator_count,
                message_broker=self.message_broker,
                node_id=f"node_{i}"
            )
            node.id = f"node_{i}"
            node.blockchain.chain = genesis_chain.copy()  # Aynı genesis'i kullan
            self.nodes.append(node)
            self.validator_nodes.append(node)
            self.message_broker.register_node(node.id)
        
        # Regular node'ları oluştur (aynı genesis ile)
        regular_count = total_nodes - validator_count
        for i in range(regular_count):
            node = Node(role="regular", message_broker=self.message_broker)
            node.blockchain.chain = genesis_chain.copy()  # Aynı genesis'i kullan
            self.nodes.append(node)
            self.regular_nodes.append(node)
            self.message_broker.register_node(node.id)
        
        print(f"✅ Initialized {total_nodes} nodes ({validator_count} validators, {regular_count} regular)")
        print(f"✅ MessageBroker configured with {len(self.message_broker.message_queues)} nodes")
        print(f"✅ All nodes share genesis block: {genesis_chain[0].hash[:16]}...")
        
        # Setup peer connections
        self._setup_peer_connections()
    
    def _setup_peer_connections(self):
        """Setup realistic mesh topology peer connections"""
        
        # 1. Validators birbirine mesh (full connected)
        for i, v1 in enumerate(self.validator_nodes):
            for v2 in self.validator_nodes[i+1:]:
                v1.add_peer(v2.id)
                v2.add_peer(v1.id)
        
        # 2. Regular nodes -> Multiple validators (2-3 random)
        for regular in self.regular_nodes:
            if len(self.validator_nodes) == 0:
                continue
            
            num_connections = random.randint(2, min(3, len(self.validator_nodes)))
            connected_validators = random.sample(self.validator_nodes, num_connections)
            
            for validator in connected_validators:
                regular.add_peer(validator.id)
                validator.add_peer(regular.id)
        
        # Log peer connections
        total_connections = sum(len(n.peers) for n in self.nodes) // 2  # Divide by 2 (bidirectional)
        print(f"✅ Peer connections established: {total_connections} connections")
    
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
            
            # Random transaction'lar oluştur
            await self._generate_random_transactions()
            
            # Validator'lar için PBFT blok önerisi
            validator_proposed_block = False
            if not self.message_broker.partition_active:
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
                                validator_proposed_block = True
                        except Exception:
                            pass  # Hata durumunda sessizce devam et
            
            # Regular node'lar için klasik mining
            # ÖNEMLİ: Sadece validator blok üretmediyse regular node mine eder
            active_regular = [n for n in self.regular_nodes if n.is_active]
            
            # ✅ PARTITION KONTROLÜ - Her iki grupta ayrı mining (FORK oluşturur)
            # NOT: Partition durumunda da validator varsa regular mine etmez
            # ✅ PARTITION KONTROLÜ - Her iki grupta ayrı mining (FORK oluşturur)
            if self.message_broker.partition_active and not validator_proposed_block:
                # Group A mining
                group_a_miners = [n for n in active_regular if n.id in self.message_broker.group_a_ids]
                block_a = None
                if group_a_miners:
                    miner_a = random.choice(group_a_miners)
                    block_a = miner_a.mine_block()
                    if block_a:
                        # Bloğu sadece Group A node'larına yay
                        for node in self.nodes:
                            if node.id in self.message_broker.group_a_ids and node.id != miner_a.id:
                                node.receive_block(block_a)

                # Group B mining (PARALEL - fork oluşturur)
                group_b_miners = [n for n in active_regular if n.id in self.message_broker.group_b_ids]
                block_b = None
                if group_b_miners:
                    miner_b = random.choice(group_b_miners)
                    block_b = miner_b.mine_block()
                    if block_b:
                        # Bloğu sadece Group B node'larına yay
                        for node in self.nodes:
                            if node.id in self.message_broker.group_b_ids and node.id != miner_b.id:
                                node.receive_block(block_b)

                # ✅ KRİTİK: Fork branch'lerini çapraz bilgilendirme
                # Her grup diğer grubun blok hash'ini duyar (fork detection için)
                if block_a and block_b:
                    # Fork artık kesin - her iki grupta da farklı bloklar var

                    # Group A node'larına Group B'nin bloğunu göster (fork olarak)
                    for node in self.nodes:
                        if node.id in self.message_broker.group_a_ids:
                            # Alternative chain'e ekle (main chain'e değil)
                            node.blockchain._handle_fork_block(block_b)

                    # Group B node'larına Group A'nın bloğunu göster (fork olarak)
                    for node in self.nodes:
                        if node.id in self.message_broker.group_b_ids:
                            # Alternative chain'e ekle (main chain'e değil)
                            node.blockchain._handle_fork_block(block_a)

            else:
                # Normal durum: Partition yoksa tek miner
                # ÖNEMLİ: Sadece validator blok üretmediyse regular node mine eder
                if active_regular and not validator_proposed_block:
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
                    except Exception:
                        pass
    
    async def _generate_random_transactions(self):
        """
        Random transaction'lar oluştur - blockchain'i aktif tutmak için
        """
        # Aktif node'lardan random seç
        active_nodes = [n for n in self.nodes if n.is_active]
        if len(active_nodes) < 2:
            return
        
        # Her çalışmada 1-3 transaction oluştur
        num_txs = random.randint(1, 3)
        
        for _ in range(num_txs):
            sender = random.choice(active_nodes)
            receiver = random.choice([n for n in active_nodes if n != sender])
            amount = random.uniform(1.0, 10.0)
            
            # Transaction oluştur
            tx = sender.create_transaction(receiver.wallet.address, amount)
            if tx:
                # Transaction'ı tüm node'ların pending listesine ekle
                for node in active_nodes:
                    node.blockchain.add_transaction(tx)
    
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
