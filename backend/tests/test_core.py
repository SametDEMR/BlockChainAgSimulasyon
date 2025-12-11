"""
Blockchain Core Modules Test - Pytest Format
"""
import pytest
from backend.core.wallet import Wallet
from backend.core.transaction import Transaction
from backend.core.block import Block
from backend.core.blockchain import Blockchain
import time


class TestWallet:
    """Wallet modülü testleri"""
    
    def test_wallet_creation(self):
        """Wallet oluşturma testi"""
        wallet = Wallet()
        assert wallet.address is not None
        assert len(wallet.address) > 0
        assert wallet.balance == 0
        assert wallet.private_key is not None
        assert wallet.public_key is not None
    
    def test_wallet_uniqueness(self):
        """Her wallet'ın unique olduğunu test et"""
        wallet1 = Wallet()
        wallet2 = Wallet()
        assert wallet1.address != wallet2.address


class TestTransaction:
    """Transaction modülü testleri"""
    
    def test_transaction_creation(self, wallet):
        """Transaction oluşturma testi"""
        wallet2 = Wallet()
        tx = Transaction(
            sender=wallet.address,
            receiver=wallet2.address,
            amount=50
        )
        assert tx.sender == wallet.address
        assert tx.receiver == wallet2.address
        assert tx.amount == 50
        assert tx.transaction_id is not None
    
    def test_transaction_signing_and_verification(self, wallet):
        """Transaction imzalama ve doğrulama testi"""
        wallet2 = Wallet()
        tx = Transaction(
            sender=wallet.address,
            receiver=wallet2.address,
            amount=50
        )
        
        # İmzala
        wallet.sign_transaction(tx)
        assert tx.signature is not None
        
        # Doğrula
        is_valid = tx.verify(wallet.get_public_key_pem())
        assert is_valid is True


class TestBlock:
    """Block modülü testleri"""
    
    def test_block_creation(self, wallet):
        """Block oluşturma testi"""
        coinbase = Transaction("COINBASE", wallet.address, 50)
        coinbase.sign(None)
        
        block = Block(
            index=1,
            timestamp=time.time(),
            transactions=[coinbase],
            previous_hash="0" * 64,
            miner=wallet.address
        )
        
        assert block.index == 1
        assert len(block.transactions) == 1
        assert block.previous_hash == "0" * 64
        assert block.miner == wallet.address
    
    def test_block_mining(self, wallet):
        """Block mining testi"""
        coinbase = Transaction("COINBASE", wallet.address, 50)
        coinbase.sign(None)
        
        block = Block(
            index=1,
            timestamp=time.time(),
            transactions=[coinbase],
            previous_hash="0" * 64,
            miner=wallet.address
        )
        
        # Mine et
        block.mine_block(difficulty=2)
        
        assert block.hash is not None
        assert block.hash.startswith("00")
        assert block.nonce > 0


class TestBlockchain:
    """Blockchain modülü testleri"""
    
    def test_blockchain_creation(self):
        """Blockchain oluşturma testi"""
        blockchain = Blockchain()
        assert len(blockchain.chain) == 1  # Genesis block
        assert blockchain.difficulty == 4
        assert blockchain.mining_reward == 50
    
    def test_blockchain_mining(self):
        """Blockchain mining testi"""
        blockchain = Blockchain()
        wallet1 = Wallet()
        wallet2 = Wallet()
        
        # Transaction ekle
        tx = Transaction(wallet1.address, wallet2.address, 30)
        wallet1.sign_transaction(tx)
        blockchain.add_transaction(tx)
        
        assert len(blockchain.pending_transactions) == 1
        
        # Mine et
        miner_address = "Miner123"
        new_block = blockchain.mine_pending_transactions(miner_address)
        
        assert new_block is not None
        assert new_block.index == 1
        assert len(blockchain.chain) == 2
    
    def test_blockchain_validation(self):
        """Blockchain geçerlilik testi"""
        blockchain = Blockchain()
        wallet1 = Wallet()
        
        # Birkaç blok mine et
        for i in range(3):
            blockchain.mine_pending_transactions(wallet1.address)
        
        # Zincir geçerli mi?
        assert blockchain.is_valid() is True
    
    def test_balance_calculation(self):
        """Bakiye hesaplama testi"""
        blockchain = Blockchain()
        wallet1 = Wallet()
        wallet2 = Wallet()
        
        # Mining reward al
        blockchain.mine_pending_transactions(wallet1.address)
        
        # Balance kontrol
        balance1 = blockchain.get_balance(wallet1.address)
        assert balance1 == 50  # Mining reward


class TestBlockchainIntegration:
    """Tüm modüllerin entegrasyon testi"""
    
    def test_full_workflow(self):
        """Tam işlem akışı testi"""
        # Blockchain ve wallet'lar oluştur
        blockchain = Blockchain()
        wallet1 = Wallet()
        wallet2 = Wallet()
        
        # İlk mining - wallet1'e reward
        blockchain.mine_pending_transactions(wallet1.address)
        assert blockchain.get_balance(wallet1.address) == 50
        
        # Transaction oluştur ve gönder
        tx = Transaction(wallet1.address, wallet2.address, 20)
        wallet1.sign_transaction(tx)
        blockchain.add_transaction(tx)
        
        # İkinci mining
        blockchain.mine_pending_transactions("Miner2")
        
        # Bakiyeleri kontrol et
        balance1 = blockchain.get_balance(wallet1.address)
        balance2 = blockchain.get_balance(wallet2.address)
        
        assert balance1 == 30  # 50 - 20
        assert balance2 == 20
        
        # Zincir geçerli mi?
        assert blockchain.is_valid() is True
