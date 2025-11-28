"""
Wallet Module - Cüzdan ve key yönetimi
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import hashlib


class Wallet:
    """
    Blockchain cüzdan sınıfı - public/private key yönetimi
    
    Attributes:
        private_key: RSA private key
        public_key: RSA public key
        address (str): Cüzdan adresi (public key'den türetilmiş)
        balance (float): Cüzdan bakiyesi
    """
    
    def __init__(self):
        """Yeni cüzdan oluştur ve key pair generate et"""
        self.private_key = None
        self.public_key = None
        self.address = None
        self.balance = 0.0
        self.generate_keys()
    
    def generate_keys(self):
        """RSA key pair oluştur"""
        # 2048 bit RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        self.public_key = self.private_key.public_key()
        
        # Public key'den adres oluştur
        self.address = self._generate_address()
    
    def _generate_address(self):
        """
        Public key'den cüzdan adresi oluştur
        
        Returns:
            str: Cüzdan adresi (hash)
        """
        # Public key'i PEM formatına çevir
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Hash'le ve ilk 40 karakteri al
        address_hash = hashlib.sha256(public_pem).hexdigest()
        return address_hash[:40]
    
    def get_public_key_pem(self):
        """
        Public key'i PEM formatında döndür
        
        Returns:
            str: PEM formatında public key
        """
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode('utf-8')
    
    def sign_transaction(self, transaction):
        """
        Transaction'ı imzala
        
        Args:
            transaction: İmzalanacak Transaction objesi
        """
        transaction.sign(self.private_key)
    
    def update_balance(self, amount):
        """
        Bakiye güncelle
        
        Args:
            amount (float): Eklenecek/çıkarılacak miktar
        """
        self.balance += amount
    
    def to_dict(self):
        """
        Wallet bilgilerini dictionary'ye çevir
        
        Returns:
            dict: Wallet bilgileri
        """
        return {
            'address': self.address,
            'public_key': self.get_public_key_pem(),
            'balance': self.balance
        }
    
    def __repr__(self):
        """String representation"""
        return f"Wallet({self.address[:10]}... | Balance: {self.balance})"
    
    def __str__(self):
        """User-friendly string"""
        return f"Address: {self.address}\nBalance: {self.balance} coins"


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from backend.core.transaction import Transaction
    import json
    
    print("=" * 60)
    print("WALLET MODULE TEST")
    print("=" * 60)
    
    # Wallet oluştur
    wallet1 = Wallet()
    wallet2 = Wallet()
    
    print(f"\n✅ Wallet 1 Created:")
    print(f"  Address: {wallet1.address}")
    print(f"  Balance: {wallet1.balance}")
    print(f"  Public Key (first 50 chars): {wallet1.get_public_key_pem()[:50]}...")
    
    print(f"\n✅ Wallet 2 Created:")
    print(f"  Address: {wallet2.address}")
    print(f"  Balance: {wallet2.balance}")
    
    # Bakiye güncelleme testi
    wallet1.update_balance(100)
    wallet2.update_balance(50)
    
    print(f"\n✅ After Balance Update:")
    print(f"  Wallet 1: {wallet1.balance} coins")
    print(f"  Wallet 2: {wallet2.balance} coins")
    
    # Transaction imzalama testi
    tx = Transaction(
        sender=wallet1.address,
        receiver=wallet2.address,
        amount=25
    )
    
    print(f"\n✅ Transaction Created:")
    print(f"  {tx}")
    
    wallet1.sign_transaction(tx)
    print(f"  Signed: {tx.signature is not None}")
    
    # İmza doğrulama
    is_valid = tx.verify(wallet1.get_public_key_pem())
    print(f"  Signature Valid: {is_valid}")
    
    print(f"\n✅ Wallet Dict:")
    print(json.dumps(wallet1.to_dict(), indent=2))
    
    print("\n" + "=" * 60)
