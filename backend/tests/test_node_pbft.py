"""
Node + PBFT Entegrasyon Testi
"""

import asyncio
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.network.node import Node
from backend.network.message_broker import MessageBroker


@pytest.mark.asyncio
async def test_node_pbft_integration():
    """Node ve PBFT entegrasyonu testi"""
    
    print("=" * 60)
    print("NODE + PBFT INTEGRATION TEST")
    print("=" * 60)
    
    # 1. MessageBroker oluştur
    print("\n1. MessageBroker oluşturuluyor...")
    broker = MessageBroker(min_delay=0.01, max_delay=0.05)
    print("✓ MessageBroker hazır")
    
    # 2. 4 validator node oluştur
    print("\n2. 4 Validator node oluşturuluyor...")
    validators = []
    for i in range(4):
        node = Node(role="validator", total_validators=4, message_broker=broker)
        node.id = f"node_{i}"  # Test için sabit ID
        validators.append(node)
        broker.register_node(node.id)
        print(f"✓ {node.id} oluşturuldu (PBFT aktif)")
    
    # 3. Primary kontrolü
    print("\n3. Primary validator kontrolü...")
    primary = validators[0]  # node_0 primary olmalı
    print(f"Primary: {primary.id} (is_primary: {primary.pbft.is_primary()})")
    
    # 4. Primary blok önerir (Pre-Prepare)
    print("\n4. Primary blok öneriyor...")
    
    # Önce bir transaction ekle
    tx = primary.create_transaction(validators[1].wallet.address, 10)
    if tx:
        primary.blockchain.add_transaction(tx)
        print(f"✓ Transaction eklendi")
    
    # Primary blok önerir
    block = await primary.propose_block()
    if block:
        print(f"✓ Block #{block.index} önerildi")
        print(f"  Hash: {block.hash[:20]}...")
    
    # 5. PBFT mesajları işle
    print("\n5. Validator'lar PBFT mesajlarını işliyor...")
    
    # Her validator mesajları işler
    for validator in validators:
        await validator.process_pbft_messages()
        await asyncio.sleep(0.1)  # Mesajların yayılması için
    
    # Tekrar işle (Prepare -> Commit)
    await asyncio.sleep(0.2)
    for validator in validators:
        await validator.process_pbft_messages()
        await asyncio.sleep(0.1)
    
    # Son kez işle (Commit -> Consensus)
    await asyncio.sleep(0.2)
    for validator in validators:
        await validator.process_pbft_messages()
        await asyncio.sleep(0.1)
    
    # 6. Konsensüs durumu kontrol
    print("\n6. Konsensüs durumu:")
    for validator in validators:
        if validator.pbft:
            stats = validator.pbft.get_stats()
            print(f"{validator.id}:")
            print(f"  Consensus reached: {stats['total_consensus_reached']}")
            print(f"  Blocks validated: {stats['blocks_validated']}")
            print(f"  View: {stats['view']}")
    
    # 7. MessageBroker istatistikleri
    print("\n7. MessageBroker İstatistikleri:")
    broker_stats = broker.get_stats()
    print(f"  Toplam mesaj: {broker_stats['total_messages_sent']}")
    print(f"  Broadcast: {broker_stats['total_broadcasts']}")
    print(f"  Bekleyen mesaj: {broker_stats['total_pending_messages']}")
    
    # 8. Node status
    print("\n8. Node Status:")
    for validator in validators:
        status = validator.get_status()
        print(f"\n{validator.id}:")
        print(f"  Role: {status['role']}")
        print(f"  Trust Score: {status['trust_score']}")
        print(f"  Chain Length: {status['chain_length']}")
        if 'pbft' in status:
            pbft = status['pbft']
            print(f"  PBFT Primary: {pbft['is_primary']}")
            print(f"  PBFT View: {pbft['view']}")
    
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)


@pytest.mark.asyncio
async def test_regular_vs_validator():
    """Regular vs Validator node testi"""
    
    print("\n" + "=" * 60)
    print("REGULAR VS VALIDATOR TEST")
    print("=" * 60)
    
    broker = MessageBroker()
    
    # Regular node
    regular = Node(role="regular", message_broker=broker)
    print(f"\n✓ Regular node: {regular.id}")
    print(f"  PBFT: {regular.pbft is not None}")
    
    # Validator node
    validator = Node(role="validator", total_validators=4, message_broker=broker)
    print(f"\n✓ Validator node: {validator.id}")
    print(f"  PBFT: {validator.pbft is not None}")
    
    # Regular node mine edebilir
    print(f"\nRegular node mining...")
    block = regular.mine_block()
    if block:
        print(f"✓ Regular mined block #{block.index}")
    
    # Validator node propose eder
    print(f"\nValidator node proposing...")
    broker.register_node(validator.id)
    validator.id = "node_0"  # Primary yapmak için
    block = await validator.propose_block()
    if block:
        print(f"✓ Validator proposed block #{block.index}")


if __name__ == "__main__":
    asyncio.run(test_node_pbft_integration())
    asyncio.run(test_regular_vs_validator())
