"""
Block Module - Blockchain blok yapısı
"""
import time
import hashlib
import json
from typing import List
from .transaction import Transaction


class Block:
    """
    Blockchain block sınıfı
    
    Attributes:
        index (int): Blok numarası
        timestamp (float): Blok oluşturma zamanı
        transactions (List[Transaction]): Blok içindeki transaction'lar
        previous_hash (str): Önceki bloğun hash'i
        nonce (int): Mining için kullanılan sayı
        hash (str): Bloğun kendi hash'i
        miner (str): Bloğu mine eden adres
    """
    
    def __init__(self, index, timestamp, transactions, previous_hash, miner=""):
        """
        Block oluştur
        
        Args:
            index (int): Blok numarası
            timestamp (float): Blok zamanı
            transactions (List[Transaction]): Transaction listesi
            previous_hash (str): Önceki blok hash'i
            miner (str): Miner adresi
        """
        self.index = index
        self.timestamp = timestamp if timestamp else time.time()
        self.transactions = transactions if transactions else []
        self.previous_hash = previous_hash
        self.nonce = 0
        self.miner = miner
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """
        Bloğun hash'ini hesapla
        
        Returns:
            str: Block hash
        """
        # Transaction'ları serialize et
        transactions_data = [tx.to_dict() for tx in self.transactions]
        
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': transactions_data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'miner': self.miner
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """
        Proof of Work - belirli zorlukta hash bul
        
        Args:
            difficulty (int): Mining zorluğu (hash başındaki 0 sayısı)
        """
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"Block #{self.index} mined: {self.hash}")
    
    def validate_transactions(self):
        """
        Blok içindeki tüm transaction'ları doğrula
        
        Returns:
            bool: Tüm transaction'lar geçerli mi?
        """
        for tx in self.transactions:
            if tx.sender != "COINBASE":
                # Public key bulunmalı (gerçek implementasyonda wallet'tan alınır)
                # Şimdilik basit validasyon
                if not tx.signature:
                    return False
        return True
    
    def to_dict(self):
        """
        Block'u dictionary'ye çevir
        
        Returns:
            dict: Block bilgileri
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash,
            'miner': self.miner
        }
    
    @staticmethod
    def from_dict(data):
        """
        Dictionary'den block oluştur
        
        Args:
            data (dict): Block bilgileri
            
        Returns:
            Block: Oluşturulan block
        """
        from .transaction import Transaction
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        
        block = Block(
            index=data['index'],
            timestamp=data['timestamp'],
            transactions=transactions,
            previous_hash=data['previous_hash'],
            miner=data.get('miner', '')
        )
        
        block.nonce = data['nonce']
        block.hash = data['hash']
        
        return block
    
    def __repr__(self):
        """String representation"""
        return f"Block(#{self.index} | {len(self.transactions)} txs | Hash: {self.hash[:10]}...)"
    
    def __str__(self):
        """User-friendly string"""
        return f"Block #{self.index}\n  Hash: {self.hash}\n  Transactions: {len(self.transactions)}\n  Miner: {self.miner[:10] if self.miner else 'N/A'}..."


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from backend.core.transaction import Transaction
    import json
    
    print("=" * 60)
    print("BLOCK MODULE TEST")
    print("=" * 60)
    
    # Test transaction'lar oluştur
    tx1 = Transaction("Alice", "Bob", 50)
    tx2 = Transaction("Bob", "Charlie", 25)
    
    # Genesis block
    genesis_block = Block(
        index=0,
        timestamp=time.time(),
        transactions=[],
        previous_hash="0",
        miner="Genesis"
    )
    
    print(f"\n✅ Genesis Block Created:")
    print(f"  Index: {genesis_block.index}")
    print(f"  Hash: {genesis_block.hash}")
    print(f"  Previous Hash: {genesis_block.previous_hash}")
    print(f"  Transactions: {len(genesis_block.transactions)}")
    
    # Normal block
    block1 = Block(
        index=1,
        timestamp=time.time(),
        transactions=[tx1, tx2],
        previous_hash=genesis_block.hash,
        miner="Miner123"
    )
    
    print(f"\n✅ Block 1 Created (before mining):")
    print(f"  Hash: {block1.hash}")
    print(f"  Nonce: {block1.nonce}")
    print(f"  Transactions: {len(block1.transactions)}")
    
    # Mining test
    print(f"\n⛏️  Mining Block 1 (difficulty=4)...")
    block1.mine_block(difficulty=4)
    
    print(f"\n✅ Block 1 Mined:")
    print(f"  Hash: {block1.hash}")
    print(f"  Nonce: {block1.nonce}")
    print(f"  Valid: {block1.hash.startswith('0000')}")
    
    # Dictionary conversion test
    print(f"\n✅ Block Dict:")
    print(json.dumps(block1.to_dict(), indent=2)[:300] + "...")
    
    print("\n" + "=" * 60)
