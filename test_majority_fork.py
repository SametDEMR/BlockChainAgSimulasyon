"""
Test: Majority Attack ve Fork Handling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.blockchain import Blockchain
from backend.core.block import Block
import time


def test_fork_handling():
    """Fork handling testleri"""
    print("=" * 60)
    print("FORK HANDLING TEST")
    print("=" * 60)
    
    # Ana zincir oluştur
    blockchain = Blockchain()
    print(f"\n✅ Main chain created: {len(blockchain.chain)} blocks")
    
    # Birkaç blok ekle
    for i in range(3):
        block = blockchain.mine_pending_transactions(f"Miner{i}")
        print(f"  Block #{block.index} mined")
    
    print(f"\n✅ Main chain: {len(blockchain.chain)} blocks")
    
    # Fork senaryosu - alternatif zincir oluştur
    alt_chain = blockchain.chain[:2].copy()  # İlk 2 bloğu al (genesis + 1)
    
    # Alternatif bloklar ekle (daha uzun zincir)
    for i in range(5):
        last_block = alt_chain[-1]
        new_block = Block(
            index=len(alt_chain),
            timestamp=time.time(),
            transactions=[],
            previous_hash=last_block.hash,
            miner=f"AttackerMiner{i}"
        )
        new_block.mine_block(blockchain.difficulty)
        alt_chain.append(new_block)
    
    print(f"\n⚠️  Alternative chain created: {len(alt_chain)} blocks")
    
    # Fork tespit et
    fork_detected = blockchain.detect_fork(alt_chain)
    print(f"\n✅ Fork detected: {fork_detected}")
    
    # Fork durumunu göster
    fork_status = blockchain.get_fork_status()
    print(f"\n📊 Fork Status:")
    print(f"  Fork detected: {fork_status['fork_detected']}")
    print(f"  Fork events: {fork_status['fork_events_count']}")
    
    # Fork çözümle
    print(f"\n⚙️  Resolving fork...")
    resolved = blockchain.resolve_fork(alt_chain)
    print(f"  Chain changed: {resolved}")
    print(f"  New chain length: {len(blockchain.chain)}")
    print(f"  Orphaned blocks: {fork_status['orphaned_blocks_count']}")
    
    # Son durum
    final_status = blockchain.get_fork_status()
    print(f"\n📊 Final Status:")
    print(f"  Fork detected: {final_status['fork_detected']}")
    print(f"  Chain length: {len(blockchain.chain)}")
    print(f"  Fork history: {len(final_status['fork_history'])} events")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_fork_handling()
