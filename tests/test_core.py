"""
Blockchain Core Modules Test Script
Tüm core modülleri test eder
"""
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.wallet import Wallet
from backend.core.transaction import Transaction
from backend.core.block import Block
from backend.core.blockchain import Blockchain
import time


def test_wallet():
    """Wallet modülünü test et"""
    print("\n" + "=" * 60)
    print("TEST: WALLET MODULE")
    print("=" * 60)
    
    wallet1 = Wallet()
    wallet2 = Wallet()
    
    print(f"✅ Wallet 1: {wallet1.address[:20]}... | Balance: {wallet1.balance}")
    print(f"✅ Wallet 2: {wallet2.address[:20]}... | Balance: {wallet2.balance}")
    
    return wallet1, wallet2


def test_transaction(wallet1, wallet2):
    """Transaction modülünü test et"""
    print("\n" + "=" * 60)
    print("TEST: TRANSACTION MODULE")
    print("=" * 60)
    
    tx = Transaction(
        sender=wallet1.address,
        receiver=wallet2.address,
        amount=50
    )
    
    print(f"✅ Transaction Created: {tx.transaction_id[:20]}...")
    print(f"   {wallet1.address[:10]}... -> {wallet2.address[:10]}... : {tx.amount}")
    
    # İmzala
    wallet1.sign_transaction(tx)
    print(f"✅ Transaction Signed: {tx.signature is not None}")
    
    # Doğrula
    is_valid = tx.verify(wallet1.get_public_key_pem())
    print(f"✅ Signature Valid: {is_valid}")
    
    return tx


def test_block(tx):
    """Block modülünü test et"""
    print("\n" + "=" * 60)
    print("TEST: BLOCK MODULE")
    print("=" * 60)
    
    # Coinbase transaction
    coinbase = Transaction("COINBASE", "Miner123", 50)
    coinbase.sign(None)
    
    block = Block(
        index=1,
        timestamp=time.time(),
        transactions=[coinbase, tx],
        previous_hash="0" * 64,
        miner="Miner123"
    )
    
    print(f"✅ Block Created: #{block.index}")
    print(f"   Transactions: {len(block.transactions)}")
    print(f"   Hash (before mining): {block.hash[:20]}...")
    
    # Mining
    print(f"⛏️  Mining block (difficulty=4)...")
    block.mine_block(4)
    
    print(f"✅ Block Mined!")
    print(f"   Hash: {block.hash[:20]}...")
    print(f"   Nonce: {block.nonce}")
    print(f"   Starts with 0000: {block.hash.startswith('0000')}")
    
    return block


def test_blockchain():
    """Blockchain modülünü test et"""
    print("\n" + "=" * 60)
    print("TEST: BLOCKCHAIN MODULE")
    print("=" * 60)
    
    blockchain = Blockchain()
    
    print(f"✅ Blockchain Created: {len(blockchain.chain)} blocks")
    print(f"   Difficulty: {blockchain.difficulty}")
    print(f"   Mining Reward: {blockchain.mining_reward}")
    
    # Genesis block
    genesis = blockchain.get_latest_block()
    print(f"✅ Genesis Block: #{genesis.index} | Hash: {genesis.hash[:20]}...")
    
    # Transaction'lar ekle
    wallet1 = Wallet()
    wallet2 = Wallet()
    
    tx1 = Transaction(wallet1.address, wallet2.address, 30)
    wallet1.sign_transaction(tx1)
    
    tx2 = Transaction(wallet2.address, wallet1.address, 10)
    wallet2.sign_transaction(tx2)
    
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    print(f"✅ Transactions Added: {len(blockchain.pending_transactions)} pending")
    
    # Mining
    print(f"⛏️  Mining block for Miner123...")
    new_block = blockchain.mine_pending_transactions("Miner123")
    
    print(f"✅ Block Mined: #{new_block.index}")
    print(f"   Hash: {new_block.hash[:20]}...")
    print(f"   Transactions in block: {len(new_block.transactions)}")
    
    # Bakiyeler
    print(f"\n💰 Balances:")
    print(f"   Miner123: {blockchain.get_balance('Miner123')}")
    print(f"   Wallet1: {blockchain.get_balance(wallet1.address)}")
    print(f"   Wallet2: {blockchain.get_balance(wallet2.address)}")
    
    # Zincir doğrulama
    is_valid = blockchain.is_valid()
    print(f"\n✅ Blockchain Valid: {is_valid}")
    
    # Bir blok daha mine et
    tx3 = Transaction(wallet1.address, wallet2.address, 5)
    wallet1.sign_transaction(tx3)
    blockchain.add_transaction(tx3)
    
    new_block2 = blockchain.mine_pending_transactions("Miner456")
    print(f"\n✅ Second Block Mined: #{new_block2.index}")
    print(f"   Total Blocks: {len(blockchain.chain)}")
    
    # Son bakiyeler
    print(f"\n💰 Final Balances:")
    print(f"   Miner123: {blockchain.get_balance('Miner123')}")
    print(f"   Miner456: {blockchain.get_balance('Miner456')}")
    print(f"   Wallet1: {blockchain.get_balance(wallet1.address)}")
    print(f"   Wallet2: {blockchain.get_balance(wallet2.address)}")
    
    return blockchain


def main():
    """Ana test fonksiyonu"""
    print("\n")
    print("*" * 60)
    print("BLOCKCHAIN CORE MODULES - INTEGRATION TEST")
    print("*" * 60)
    
    try:
        # Wallet testi
        wallet1, wallet2 = test_wallet()
        
        # Transaction testi
        tx = test_transaction(wallet1, wallet2)
        
        # Block testi
        block = test_block(tx)
        
        # Blockchain testi
        blockchain = test_blockchain()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\nFinal Blockchain State:")
        print(f"  Blocks: {len(blockchain.chain)}")
        print(f"  Chain Valid: {blockchain.is_valid()}")
        print(f"  Pending Transactions: {len(blockchain.pending_transactions)}")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
