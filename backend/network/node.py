"""
Node Module - Blockchain network node yapısı
"""
import uuid
import time
from typing import List, Dict, Optional
from ..core.blockchain import Blockchain
from ..core.transaction import Transaction
from ..core.wallet import Wallet
from .pbft_handler import PBFTHandler


class Node:
    """
    Blockchain network node sınıfı
    
    Attributes:
        id (str): Node benzersiz kimliği
        role (str): Node rolü ("validator" veya "regular")
        blockchain (Blockchain): Node'un blockchain kopyası
        wallet (Wallet): Node'un cüzdanı
        pbft (PBFTHandler): PBFT consensus handler (sadece validator'lar için)
        message_broker: MessageBroker referansı (node'lar arası iletişim)
        status (str): Node durumu ("healthy", "under_attack", "recovering")
        is_active (bool): Node aktif mi?
        response_time (float): İstek yanıt süresi (ms)
        trust_score (int): Güven puanı (0-100)
        is_byzantine (bool): Byzantine node mu?
        is_sybil (bool): Sybil saldırı node'u mu?
    """
    
    def __init__(self, role="regular", total_validators=4, message_broker=None):
        """
        Node oluştur
        
        Args:
            role (str): Node rolü ("validator" veya "regular")
            total_validators (int): Toplam validator sayısı (PBFT için)
            message_broker: MessageBroker instance (opsiyonel)
        """
        self.id = str(uuid.uuid4())[:8]
        self.role = role
        self.blockchain = Blockchain()
        self.wallet = Wallet()
        self.status = "healthy"
        self.is_active = True
        self.response_time = 50.0  # ms
        self.trust_score = 100
        self.is_byzantine = False
        self.is_sybil = False
        self.is_malicious = False  # Majority attack için
        self.partition_group = None  # "A", "B" veya None (Network partition için)
        self.is_selfish_miner = False  # Selfish mining saldırısı için
        self.private_chain = None  # Selfish miner'ın gizli zinciri
        
        # Metrikler
        self.cpu_usage = 20  # %
        self.memory_usage = 30  # %
        self.network_latency = 10.0  # ms
        self.packet_loss = 0.0  # %
        self.requests_per_second = 0
        self.errors_count = 0
        
        # PBFT için MessageBroker referansı
        self.message_broker = message_broker
        
        # PBFT Handler (sadece validator'lar için)
        self.pbft: Optional[PBFTHandler] = None
        if role == "validator":
            self.pbft = PBFTHandler(self.id, total_validators)
        
        # İstatistikler
        self.blocks_mined = 0
        self.transactions_created = 0
        self.total_earned = 0.0
        
    def create_transaction(self, receiver_address, amount):
        """
        Yeni transaction oluştur
        
        Args:
            receiver_address (str): Alıcı adres
            amount (float): Miktar
            
        Returns:
            Transaction: Oluşturulan transaction veya None
        """
        if not self.is_active:
            return None
        
        # Bakiye kontrolü (basitleştirilmiş)
        balance = self.blockchain.get_balance(self.wallet.address)
        if balance < amount:
            print(f"Node {self.id}: Insufficient balance ({balance} < {amount})")
            return None
        
        # Transaction oluştur ve imzala
        tx = Transaction(
            sender=self.wallet.address,
            receiver=receiver_address,
            amount=amount
        )
        self.wallet.sign_transaction(tx)
        
        # Blockchain'e ekle
        if self.blockchain.add_transaction(tx):
            self.transactions_created += 1
            return tx
        
        return None
    
    async def propose_block(self):
        """
        Yeni blok öner (validator için)
        PBFT Pre-Prepare fazı başlatır
        
        Returns:
            Block: Önerilen blok veya None
        """
        if not self.is_active or self.role != "validator":
            return None
        
        if not self.pbft or not self.pbft.is_primary():
            return None
        
        # Blok oluştur (mine)
        block = self.blockchain.mine_pending_transactions(self.wallet.address)
        
        if not block or not self.message_broker:
            return None
        
        # PBFT Pre-Prepare mesajı oluştur
        sequence = self.pbft.sequence_number + 1
        pre_prepare = self.pbft.create_pre_prepare(block.hash, sequence)
        
        # Tüm validator'lara broadcast
        await self.message_broker.broadcast(
            sender_id=self.id,
            message_type='pre_prepare',
            content={
                'block': block.to_dict(),
                'pbft_message': pre_prepare.to_dict()
            },
            exclude_sender=False  # Primary da almalı (kendi log'una eklemek için)
        )
        
        print(f"Node {self.id} (PRIMARY) proposed block #{block.index}")
        return block
    
    async def process_pbft_messages(self):
        """
        Bekleyen PBFT mesajlarını işle
        Validator node'lar için
        """
        if not self.is_active or self.role != "validator" or not self.message_broker:
            return
        
        # Mesajları al
        messages = self.message_broker.get_messages_for_node(self.id)
        
        for msg in messages:
            if msg.message_type == 'pre_prepare':
                await self._handle_pre_prepare(msg)
            elif msg.message_type == 'prepare':
                await self._handle_prepare(msg)
            elif msg.message_type == 'commit':
                await self._handle_commit(msg)
    
    async def _handle_pre_prepare(self, message):
        """Pre-Prepare mesajını işle"""
        if not self.pbft:
            return
        
        pbft_msg_dict = message.content.get('pbft_message')
        if not pbft_msg_dict:
            return
        
        # PBFT mesajını oluştur
        from .pbft_handler import PBFTMessage
        pbft_msg = PBFTMessage(
            phase=pbft_msg_dict['phase'],
            view=pbft_msg_dict['view'],
            sequence_number=pbft_msg_dict['sequence_number'],
            block_hash=pbft_msg_dict['block_hash'],
            node_id=pbft_msg_dict['node_id']
        )
        
        # Block hash validasyonu - Byzantine detection
        block_data = message.content.get('block')
        if block_data and block_data.get('hash') != pbft_msg.block_hash:
            # HATA: Pre-prepare'deki hash ile gerçek blok hash'i uyuşmuyor!
            # Bu Byzantine davranış işaretidir
            print(f"⚠️  Node {self.id} detected MISMATCH in pre-prepare from {pbft_msg.node_id}")
            print(f"    Expected: {pbft_msg.block_hash[:16]}...")
            print(f"    Actual: {block_data.get('hash', 'N/A')[:16]}...")
            
            # Mesajı reddet, prepare gönderme
            return
        
        # Fake hash detection (tamamı 0)
        if pbft_msg.block_hash == "0" * 64:
            print(f"⚠️  Node {self.id} detected FAKE hash from {pbft_msg.node_id}")
            # Byzantine davranış - mesajı reddet
            return
        
        # PBFT'ye gönder ve prepare mesajı al
        prepare_msg = self.pbft.process_pre_prepare(pbft_msg)
        
        if prepare_msg and self.message_broker:
            # Doğru davranış - trust score +1
            self.trust_score = min(100, self.trust_score + 1)
            
            # Prepare mesajını broadcast et
            await self.message_broker.broadcast(
                sender_id=self.id,
                message_type='prepare',
                content={'pbft_message': prepare_msg.to_dict()},
                exclude_sender=False
            )
            print(f"Node {self.id} sent PREPARE (trust: {self.trust_score})")
    
    async def _handle_prepare(self, message):
        """Prepare mesajını işle"""
        if not self.pbft:
            return
        
        pbft_msg_dict = message.content.get('pbft_message')
        if not pbft_msg_dict:
            return
        
        from .pbft_handler import PBFTMessage
        pbft_msg = PBFTMessage(
            phase=pbft_msg_dict['phase'],
            view=pbft_msg_dict['view'],
            sequence_number=pbft_msg_dict['sequence_number'],
            block_hash=pbft_msg_dict['block_hash'],
            node_id=pbft_msg_dict['node_id']
        )
        
        # PBFT'ye gönder ve commit mesajı al
        commit_msg = self.pbft.process_prepare(pbft_msg)
        
        if commit_msg and self.message_broker:
            # Doğru davranış - trust score +1
            self.trust_score = min(100, self.trust_score + 1)
            
            # Commit mesajını broadcast et
            await self.message_broker.broadcast(
                sender_id=self.id,
                message_type='commit',
                content={'pbft_message': commit_msg.to_dict()},
                exclude_sender=False
            )
            print(f"Node {self.id} sent COMMIT (trust: {self.trust_score})")
    
    async def _handle_commit(self, message):
        """Commit mesajını işle"""
        if not self.pbft:
            return
        
        pbft_msg_dict = message.content.get('pbft_message')
        if not pbft_msg_dict:
            return
        
        from .pbft_handler import PBFTMessage
        pbft_msg = PBFTMessage(
            phase=pbft_msg_dict['phase'],
            view=pbft_msg_dict['view'],
            sequence_number=pbft_msg_dict['sequence_number'],
            block_hash=pbft_msg_dict['block_hash'],
            node_id=pbft_msg_dict['node_id']
        )
        
        # PBFT'ye gönder ve konsensüs kontrolü
        consensus_reached = self.pbft.process_commit(pbft_msg)
        
        if consensus_reached:
            # Konsensüs sağlandı - trust score +2 (bonus)
            self.trust_score = min(100, self.trust_score + 2)
            
            # Bloğu zincire ekle - consensus sonrası
            if len(self.blockchain.pending_transactions) >= 0:
                block = self.blockchain.mine_pending_transactions(self.wallet.address)
                if block:
                    self.blocks_mined += 1
                    self.total_earned += self.blockchain.mining_reward
                    print(f"✅ Node {self.id} added block #{block.index} after CONSENSUS! (trust: {self.trust_score})")
            else:
                print(f"Node {self.id} reached CONSENSUS! (trust: {self.trust_score})")
    
    def mine_block(self):
        """
        Bekleyen transaction'ları mine et ve blok oluştur
        (Eski PoW yöntemi - validator olmayan node'lar için)
        
        Returns:
            Block: Oluşturulan blok veya None
        """
        if not self.is_active:
            return None
        
        if self.role == "validator":
            # Validator'lar PBFT kullanır, mine_block değil
            print(f"Node {self.id} is validator, use propose_block() instead")
            return None
        
        if len(self.blockchain.pending_transactions) == 0:
            pass
        
        # Byzantine node hatalı davranabilir
        if self.is_byzantine and self.role == "validator":
            pass
        
        # Mining yap
        block = self.blockchain.mine_pending_transactions(self.wallet.address)
        
        if block:
            self.blocks_mined += 1
            self.total_earned += self.blockchain.mining_reward
            print(f"Node {self.id} ({self.role}) mined block #{block.index}")
        
        return block
    
    def receive_block(self, block):
        """
        Başka bir node'dan blok al ve zincire ekle
        
        Args:
            block: Alınan blok
            
        Returns:
            bool: Blok kabul edildi mi?
        """
        if not self.is_active:
            return False
        
        return self.blockchain.add_block(block)
    
    def sync_blockchain(self, other_chain):
        """
        Blockchain'i başka bir zincir ile senkronize et
        
        Args:
            other_chain (Blockchain): Senkronize edilecek zincir
        """
        if len(other_chain.chain) > len(self.blockchain.chain) and other_chain.is_valid():
            self.blockchain.chain = other_chain.chain.copy()
            print(f"Node {self.id} synced blockchain (new length: {len(self.blockchain.chain)})")
    
    def get_metrics(self):
        """
        Node metriklerini döndür
        
        Returns:
            dict: Node metrikleri
        """
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'response_time': self.response_time,
            'network_latency': self.network_latency,
            'packet_loss': self.packet_loss,
            'requests_per_second': self.requests_per_second,
            'errors_count': self.errors_count,
            'trust_score': self.trust_score
        }
    
    def get_status(self):
        """
        Node durumunu döndür
        
        Returns:
            dict: Node durum bilgileri
        """
        status_dict = {
            'id': self.id,
            'role': self.role,
            'address': self.wallet.address,
            'status': self.status,
            'is_active': self.is_active,
            'response_time': self.response_time,
            'trust_score': self.trust_score,
            'is_byzantine': self.is_byzantine,
            'is_sybil': self.is_sybil,
            'balance': self.blockchain.get_balance(self.wallet.address),
            'chain_length': len(self.blockchain.chain),
            'pending_txs': len(self.blockchain.pending_transactions),
            'blocks_mined': self.blocks_mined,
            'transactions_created': self.transactions_created,
            'total_earned': self.total_earned,
            'metrics': self.get_metrics()
        }
        
        # PBFT bilgileri ekle (validator ise)
        if self.pbft:
            pbft_stats = self.pbft.get_stats()
            status_dict['pbft'] = pbft_stats
        
        # Private chain bilgileri ekle (selfish miner ise)
        if self.is_selfish_miner and self.private_chain:
            status_dict['private_chain'] = {
                'exists': True,
                'length': len(self.private_chain.chain),
                'chain': self.private_chain.to_dict()
            }
        else:
            status_dict['private_chain'] = {'exists': False}
        
        return status_dict
    
    def set_byzantine(self, is_byzantine=True):
        """Byzantine node olarak işaretle"""
        self.is_byzantine = is_byzantine
        if is_byzantine:
            self.status = "under_attack"
            self.trust_score = max(0, self.trust_score - 20)
    
    def set_sybil(self, is_sybil=True):
        """Sybil node olarak işaretle"""
        self.is_sybil = is_sybil
        if is_sybil:
            self.trust_score = 0
    
    def set_under_attack(self):
        """Node'u saldırı altında işaretle"""
        self.status = "under_attack"
        self.response_time *= 10
    
    def recover(self):
        """Node'u iyileştir"""
        self.status = "recovering"
        self.response_time = 50.0
        
        if not self.is_byzantine and not self.is_sybil:
            self.trust_score = min(100, self.trust_score + 10)
            
        time.sleep(1)
        if not self.is_byzantine and not self.is_sybil:
            self.status = "healthy"
    
    def reveal_private_chain(self):
        """
        Selfish miner'in private chain'ini yayınla
        Private chain public chain'den uzunsa onu yayınlar
        
        Returns:
            bool: Reveal başarılı mı?
        """
        if not self.is_selfish_miner or not self.private_chain:
            return False
        
        # Private chain public'ten uzunsa yayınla
        private_length = len(self.private_chain.chain)
        public_length = len(self.blockchain.chain)
        
        if private_length > public_length:
            # Private chain'i public yap
            old_public = self.blockchain
            self.blockchain = self.private_chain
            self.private_chain = old_public
            
            print(f"🔴 Node {self.id} REVEALED private chain ({private_length} blocks > {public_length} public blocks)")
            return True
        
        return False
    
    def start_selfish_mining(self):
        """
        Selfish mining'i başlat
        Private chain oluşturur
        """
        if not self.is_selfish_miner:
            self.is_selfish_miner = True
            # Private chain oluştur (public chain'in kopyası)
            self.private_chain = Blockchain()
            self.private_chain.chain = [block for block in self.blockchain.chain]
            self.private_chain.pending_transactions = []
            print(f"🟠 Node {self.id} started SELFISH MINING")
    
    def stop_selfish_mining(self):
        """
        Selfish mining'i durdur
        Private chain'i sıfırla
        """
        if self.is_selfish_miner:
            self.is_selfish_miner = False
            self.private_chain = None
            print(f"🟢 Node {self.id} stopped SELFISH MINING")
    
    def __repr__(self):
        return f"Node({self.id} | {self.role} | {self.status})"
    
    def __str__(self):
        return f"Node {self.id} ({self.role}) - Status: {self.status} | Chain: {len(self.blockchain.chain)} blocks"
