"""
Simulator + PBFT Entegrasyon Testi
"""

import asyncio
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.simulator import Simulator


@pytest.mark.asyncio
async def test_simulator_pbft():
    """Simulator + PBFT tam entegrasyon testi"""
    
    print("=" * 60)
    print("SIMULATOR + PBFT INTEGRATION TEST")
    print("=" * 60)
    
    # 1. Simulator oluştur
    print("\n1. Simulator başlatılıyor...")
    sim = Simulator()
    print(f"✓ Simulator hazır")
    print(f"  Toplam node: {len(sim.nodes)}")
    print(f"  Validator: {len(sim.validator_nodes)}")
    print(f"  Regular: {len(sim.regular_nodes)}")
    
    # 2. Status kontrol
    print("\n2. Initial Status:")
    status = sim.get_status()
    print(f"  Running: {status['is_running']}")
    print(f"  PBFT Primary: {status['pbft'].get('primary_validator', 'N/A')}")
    print(f"  MessageBroker nodes: {status['message_broker']['registered_nodes']}")
    
    # 3. Simulator başlat
    print("\n3. Simulator başlatılıyor...")
    sim.start()
    print(f"✓ Started")
    
    # 4. Manual PBFT proposal
    print("\n4. Primary validator blok öneriyor...")
    primary = sim.validator_nodes[0]  # node_0 primary olmalı
    print(f"  Primary: {primary.id} (is_primary: {primary.pbft.is_primary()})")
    
    # Transaction ekle
    tx = primary.create_transaction(sim.validator_nodes[1].wallet.address, 5)
    if tx:
        primary.blockchain.add_transaction(tx)
        print(f"✓ Transaction eklendi")
    
    # Blok öner
    block = await primary.propose_block()
    if block:
        print(f"✓ Block #{block.index} önerildi")
    
    # 5. PBFT mesajları işle (3 tur)
    print("\n5. PBFT konsensüsü işleniyor...")
    for round in range(3):
        await asyncio.sleep(0.3)
        for validator in sim.validator_nodes:
            await validator.process_pbft_messages()
        print(f"  Tur {round + 1} tamamlandı")
    
    # 6. Konsensüs durumu
    print("\n6. Konsensüs Sonucu:")
    for validator in sim.validator_nodes:
        stats = validator.pbft.get_stats()
        print(f"  {validator.id}: {stats['total_consensus_reached']} konsensüs")
    
    # 7. MessageBroker stats
    print("\n7. MessageBroker İstatistikleri:")
    broker_stats = sim.message_broker.get_stats()
    print(f"  Toplam mesaj: {broker_stats['total_messages_sent']}")
    print(f"  Broadcast: {broker_stats['total_broadcasts']}")
    print(f"  Bekleyen: {broker_stats['total_pending_messages']}")
    
    # 8. PBFT mesajları
    print("\n8. PBFT Mesajları:")
    pbft_msgs = sim.get_pbft_messages()
    print(f"  Toplam PBFT mesajı: {len(pbft_msgs)}")
    for msg in pbft_msgs[:5]:  # İlk 5'i göster
        print(f"    {msg['message_type']} from {msg['sender_id']}")
    
    # 9. Stop
    print("\n9. Simulator durduruluyor...")
    sim.stop()
    print(f"✓ Stopped")
    
    # 10. Final status
    print("\n10. Final Status:")
    final_status = sim.get_status()
    print(f"  Total blocks: {final_status['total_blocks']}")
    print(f"  PBFT consensus: {final_status['pbft'].get('total_consensus_reached', 0)}")
    
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)


@pytest.mark.asyncio
async def test_auto_production():
    """Otomatik blok üretimi testi"""
    
    print("\n" + "=" * 60)
    print("AUTO BLOCK PRODUCTION TEST")
    print("=" * 60)
    
    sim = Simulator()
    sim.start()
    
    print("\n3 saniye otomatik production...")
    
    # Background task'leri başlat
    production_task = asyncio.create_task(sim.auto_block_production())
    pbft_task = asyncio.create_task(sim.pbft_message_processing())
    
    await asyncio.sleep(3)
    
    sim.stop()
    
    # Task'leri bekle
    await asyncio.sleep(0.5)
    
    status = sim.get_status()
    print(f"\n✓ Total blocks produced: {status['total_blocks']}")
    print(f"✓ PBFT consensus: {status['pbft'].get('total_consensus_reached', 0)}")
    
    # Cleanup
    production_task.cancel()
    pbft_task.cancel()


if __name__ == "__main__":
    asyncio.run(test_simulator_pbft())
    asyncio.run(test_auto_production())
