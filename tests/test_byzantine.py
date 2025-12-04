"""
Test Byzantine Attack - Milestone 4.1
"""
import asyncio
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.simulator import Simulator
from backend.attacks.byzantine import ByzantineAttack


@pytest.mark.asyncio
async def test_byzantine_attack():
    print("=" * 80)
    print("BYZANTINE ATTACK TEST - MILESTONE 4.1")
    print("=" * 80)
    
    # Simulator başlat
    print("\n1️⃣  Initializing simulator...")
    simulator = Simulator()
    
    # Byzantine attack oluştur
    byzantine_attack = ByzantineAttack(simulator)
    
    # Simülatörü başlat
    print("\n2️⃣  Starting simulator...")
    simulator.start()
    
    # Background task'leri başlat
    production_task = asyncio.create_task(simulator.auto_block_production())
    pbft_task = asyncio.create_task(simulator.pbft_message_processing())
    
    print("✅ Simulator started")
    print(f"   Validator nodes: {len(simulator.validator_nodes)}")
    for v in simulator.validator_nodes:
        print(f"      - {v.id} | Trust Score: {v.trust_score} | Status: {v.status}")
    
    # Normal çalışmayı gözlemle (10 saniye)
    print("\n3️⃣  Normal operation for 10 seconds...")
    await asyncio.sleep(10)
    
    # İlk validator'ın durumunu kontrol et
    first_validator = simulator.validator_nodes[0]
    print(f"\n📊 Before attack - {first_validator.id}:")
    print(f"   Status: {first_validator.status}")
    print(f"   Trust Score: {first_validator.trust_score}")
    print(f"   Is Byzantine: {first_validator.is_byzantine}")
    print(f"   Blockchain length: {len(first_validator.blockchain.chain)}")
    
    if first_validator.pbft:
        pbft_stats = first_validator.pbft.get_stats()
        print(f"   PBFT consensus reached: {pbft_stats['total_consensus_reached']}")
        print(f"   View: {pbft_stats['view']}")
    
    # Byzantine saldırısı tetikle
    print(f"\n4️⃣  Triggering Byzantine attack on {first_validator.id}...")
    result = byzantine_attack.trigger(first_validator.id)
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"   Target: {result['target_node']}")
        print(f"   Duration: {result['duration']} seconds")
    else:
        print(f"❌ {result['message']}")
        return
    
    # Saldırı sırasında gözlemle
    print("\n5️⃣  Observing attack effects (15 seconds)...")
    for i in range(15):
        await asyncio.sleep(1)
        status = byzantine_attack.get_status()
        
        if i % 5 == 0:  # Her 5 saniyede bir
            print(f"\n   ⏱️  {i}s - Byzantine Attack Status:")
            print(f"      Active: {status['active']}")
            print(f"      Elapsed: {status['elapsed_time']}s")
            print(f"      Remaining: {status['remaining_time']}s")
            print(f"      Node Status: {first_validator.status}")
            print(f"      Node Trust Score: {first_validator.trust_score}")
            print(f"      Is Byzantine: {first_validator.is_byzantine}")
    
    # Otomatik iyileşmeyi bekle
    print("\n6️⃣  Waiting for auto-recovery (15 seconds)...")
    await asyncio.sleep(15)
    
    # Saldırı sonrası durum
    print(f"\n📊 After attack - {first_validator.id}:")
    print(f"   Status: {first_validator.status}")
    print(f"   Trust Score: {first_validator.trust_score}")
    print(f"   Is Byzantine: {first_validator.is_byzantine}")
    print(f"   Blockchain length: {len(first_validator.blockchain.chain)}")
    
    final_status = byzantine_attack.get_status()
    print(f"\n📊 Byzantine Attack Final Status:")
    print(f"   Active: {final_status['active']}")
    print(f"   Target: {final_status['target_node']}")
    
    # Temizlik
    print("\n7️⃣  Cleanup...")
    simulator.stop()
    production_task.cancel()
    pbft_task.cancel()
    
    try:
        await production_task
    except asyncio.CancelledError:
        pass
    
    try:
        await pbft_task
    except asyncio.CancelledError:
        pass
    
    print("\n✅ Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_byzantine_attack())
