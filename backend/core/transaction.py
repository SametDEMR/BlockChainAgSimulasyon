"""
Transaction Module - Blockchain işlem yönetimi
"""
import time
import hashlib
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


class Transaction:
    """
    Blockchain transaction sınıfı
    
    Attributes:
        sender (str): Gönderen adres (public key)
        receiver (str): Alıcı adres (public key)
        amount (float): Transfer miktarı
        timestamp (float): İşlem zamanı
        signature (bytes): İşlem imzası
        transaction_id (str): İşlem kimliği
    """
    
    def __init__(self, sender, receiver, amount, timestamp=None):
        """
        Transaction oluştur
        
        Args:
            sender (str): Gönderen adres
            receiver (str): Alıcı adres
            amount (float): Transfer miktarı
            timestamp (float, optional): İşlem zamanı. None ise şimdi.
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp if timestamp else time.time()
        self.signature = None
        self.transaction_id = self._calculate_hash()
    
    def _calculate_hash(self):
        """
        Transaction hash'ini hesapla
        
        Returns:
            str: Transaction hash
        """
        transaction_string = json.dumps({
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp
        }, sort_keys=True)
        
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def sign(self, private_key):
        """
        Transaction'ı private key ile imzala
        
        Args:
            private_key: RSA private key objesi
        """
        if self.sender == "COINBASE":
            # Coinbase transaction'ları imzalanmaz
            self.signature = b"COINBASE"
            return
        
        transaction_hash = self.transaction_id.encode()
        
        self.signature = private_key.sign(
            transaction_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    
    def verify(self, public_key_pem):
        """
        Transaction imzasını doğrula
        
        Args:
            public_key_pem (str): PEM formatında public key
            
        Returns:
            bool: İmza geçerli mi?
        """
        if self.sender == "COINBASE":
            # Coinbase transaction'ları her zaman geçerli
            return True
        
        if not self.signature:
            return False
        
        try:
            # PEM formatından public key yükle
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode()
            )
            
            transaction_hash = self.transaction_id.encode()
            
            public_key.verify(
                self.signature,
                transaction_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def to_dict(self):
        """
        Transaction'ı dictionary'ye çevir
        
        Returns:
            dict: Transaction bilgileri
        """
        return {
            'transaction_id': self.transaction_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature.hex() if self.signature and self.signature != b"COINBASE" else "COINBASE"
        }
    
    @staticmethod
    def from_dict(data):
        """
        Dictionary'den transaction oluştur
        
        Args:
            data (dict): Transaction bilgileri
            
        Returns:
            Transaction: Oluşturulan transaction
        """
        tx = Transaction(
            sender=data['sender'],
            receiver=data['receiver'],
            amount=data['amount'],
            timestamp=data['timestamp']
        )
        
        if data['signature'] == "COINBASE":
            tx.signature = b"COINBASE"
        elif data['signature']:
            tx.signature = bytes.fromhex(data['signature'])
        
        return tx
    
    def __repr__(self):
        """String representation"""
        return f"Transaction({self.sender[:10]}... -> {self.receiver[:10]}...: {self.amount})"
    
    def __str__(self):
        """User-friendly string"""
        return f"{self.sender[:10]}... -> {self.receiver[:10]}...: {self.amount} coins"


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("TRANSACTION MODULE TEST")
    print("=" * 60)
    
    # Test transaction oluştur
    tx = Transaction(
        sender="Alice_Public_Key_123",
        receiver="Bob_Public_Key_456",
        amount=100.5
    )
    
    print(f"\n✅ Transaction Created:")
    print(f"  ID: {tx.transaction_id}")
    print(f"  From: {tx.sender}")
    print(f"  To: {tx.receiver}")
    print(f"  Amount: {tx.amount}")
    print(f"  Timestamp: {tx.timestamp}")
    
    print(f"\n✅ Transaction Dict:")
    print(json.dumps(tx.to_dict(), indent=2))
    
    # Coinbase transaction test
    coinbase_tx = Transaction(
        sender="COINBASE",
        receiver="Miner_Public_Key",
        amount=50
    )
    coinbase_tx.sign(None)
    
    print(f"\n✅ Coinbase Transaction:")
    print(f"  {coinbase_tx}")
    print(f"  Signature: {coinbase_tx.signature}")
    print(f"  Valid: {coinbase_tx.verify(None)}")
    
    print("\n" + "=" * 60)
