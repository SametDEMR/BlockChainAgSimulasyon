"""
Node Module - Blockchain network node yapısı
"""
import uuid
import time
from typing import List, Dict
from ..core.blockchain import Blockchain
from ..core.transaction import Transaction
from ..core.wallet import Wallet


class Node:
    """
    Blockchain network node sınıfı
    
    Attributes:
        id (str): Node benzersiz kimliği
        role (str): Node rolü ("validator" veya "regular")
        blockchain (Blockchain): Node'un blockchain kopyası
        wallet (Wallet): Node'un cüzdanı
        status (str): Node durumu ("healthy", "under_attack", "recovering")
        is_active (bool): Node aktif mi?
        response_time (float): İstek yanıt süresi (ms)
        trust_score (int): Güven puanı (0-100)
        is_byzantine (bool): Byzantine node mu?
        is_sybil (bool): Sybil saldırı node'u mu?
    """
    
    def __init__(self, role="regular"):
        """
        Node oluştur
        
        Args:
            role (str): Node rolü ("validator" veya "regular")
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
    
    def mine_block(self):
        """
        Bekleyen transaction'ları mine et ve blok oluştur
        
        Returns:
            Block: Oluşturulan blok veya None
        """
        if not self.is_active:
            return None
        
        if len(self.blockchain.pending_transactions) == 0:
            # Boş blok oluşturma (sadece coinbase)
            pass
        
        # Byzantine node hatalı davranabilir
        if self.is_byzantine and self.role == "validator":
            # Byzantine davranış simülasyonu için şimdilik normal mine
            # İleride PBFT entegrasyonunda hatalı davranış eklenecek
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
        
        # Blok doğrulama ve ekleme
        return self.blockchain.add_block(block)
    
    def sync_blockchain(self, other_chain):
        """
        Blockchain'i başka bir zincir ile senkronize et
        
        Args:
            other_chain (Blockchain): Senkronize edilecek zincir
        """
        # En uzun geçerli zinciri seç
        if len(other_chain.chain) > len(self.blockchain.chain) and other_chain.is_valid():
            self.blockchain.chain = other_chain.chain.copy()
            print(f"Node {self.id} synced blockchain (new length: {len(self.blockchain.chain)})")
    
    def get_status(self):
        """
        Node durumunu döndür
        
        Returns:
            dict: Node durum bilgileri
        """
        return {
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
            'total_earned': self.total_earned
        }
    
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
        self.response_time *= 10  # Response time 10x artar
    
    def recover(self):
        """Node'u iyileştir"""
        self.status = "recovering"
        self.response_time = 50.0
        
        # Güven puanını yavaşça artır
        if not self.is_byzantine and not self.is_sybil:
            self.trust_score = min(100, self.trust_score + 10)
            
        # Kısa süre sonra healthy'ye dön
        time.sleep(1)
        if not self.is_byzantine and not self.is_sybil:
            self.status = "healthy"
    
    def __repr__(self):
        """String representation"""
        return f"Node({self.id} | {self.role} | {self.status})"
    
    def __str__(self):
        """User-friendly string"""
        return f"Node {self.id} ({self.role}) - Status: {self.status} | Chain: {len(self.blockchain.chain)} blocks"


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    print("=" * 60)
    print("NODE MODULE TEST")
    print("=" * 60)
    
    # Regular node oluştur
    node1 = Node(role="regular")
    print(f"\n✅ Regular Node Created:")
    print(f"  ID: {node1.id}")
    print(f"  Role: {node1.role}")
    print(f"  Address: {node1.wallet.address[:20]}...")
    print(f"  Status: {node1.status}")
    print(f"  Trust Score: {node1.trust_score}")
    
    # Validator node oluştur
    node2 = Node(role="validator")
    print(f"\n✅ Validator Node Created:")
    print(f"  ID: {node2.id}")
    print(f"  Role: {node2.role}")
    
    # Transaction oluştur (başlangıçta balance 0 olacağı için başarısız olur)
    print(f"\n📝 Creating transaction (should fail - no balance):")
    tx = node1.create_transaction(node2.wallet.address, 10)
    print(f"  Transaction created: {tx is not None}")
    
    # Mining test
    print(f"\n⛏️  Mining first block with node1:")
    block1 = node1.mine_block()
    if block1:
        print(f"  Block #{block1.index} mined")
        print(f"  Node1 earned: {node1.total_earned} coins")
        print(f"  Node1 balance: {node1.blockchain.get_balance(node1.wallet.address)}")
    
    # Şimdi balance var, transaction oluştur
    print(f"\n📝 Creating transaction (should succeed now):")
    tx = node1.create_transaction(node2.wallet.address, 10)
    if tx:
        print(f"  Transaction created: {tx}")
        print(f"  Sender: {tx.sender[:20]}...")
        print(f"  Receiver: {tx.receiver[:20]}...")
        print(f"  Amount: {tx.amount}")
    
    # İkinci blok mine et
    print(f"\n⛏️  Mining second block with node2:")
    block2 = node2.mine_block()
    if block2:
        print(f"  Block #{block2.index} mined")
    
    # Node status
    print(f"\n📊 Node1 Status:")
    import json
    print(json.dumps(node1.get_status(), indent=2))
    
    # Byzantine test
    print(f"\n⚠️  Setting node1 as Byzantine:")
    node1.set_byzantine(True)
    print(f"  Byzantine: {node1.is_byzantine}")
    print(f"  Status: {node1.status}")
    print(f"  Trust Score: {node1.trust_score}")
    
    # Recovery test
    print(f"\n🔄 Recovering node1:")
    node1.is_byzantine = False
    node1.recover()
    print(f"  Status: {node1.status}")
    print(f"  Trust Score: {node1.trust_score}")
    
    print("\n" + "=" * 60)
