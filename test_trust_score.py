"""
Test Trust Score System - Milestone 4.2
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.simulator import Simulator
from backend.attacks.byzantine import ByzantineAttack


async def test_trust_score():
    print("=" * 80)
    print("TRUST SCORE SYSTEM TEST - MILESTONE 4.2")
    print("=" * 80)
    
    # Simulator başlat
    print("\n1️⃣  Initializing simulator...")
    simulator = Simulator()
    byzantine_attack = ByzantineAttack(simulator)
    
    # Simülatörü başlat
    print("\n2️⃣  Starting simulator...")
    simulator.start()
    
    # Background task'leri başlat
    production_task = asyncio.create_task(simulator.auto_block_production())
    pbft_task = asyncio.create_task(simulator.pbft_message_processing())
    
    print("✅ Simulator started")
    
    # Tüm validator'ların başlangıç trust score'larını göster
    print("\n📊 Initial Trust Scores:")
    for v in simulator.validator_nodes:
        print(f"   {v.id}: {v.trust_score}")
    
    # Normal çalışma - trust score artışını gözlemle (15 saniye)
    print("\n3️⃣  Normal operation - observing trust score increase (15 seconds)...")
    for i in range(3):
        await asyncio.sleep(5)
        print(f"\n   ⏱️  {(i+1)*5}s - Trust Scores:")
        for v in simulator.validator_nodes:
            print(f"      {v.id}: {v.trust_score} | Status: {v.status}")
    
    # İlk validator'ı Byzantine yap
    target_validator = simulator.validator_nodes[0]
    print(f"\n4️⃣  Triggering Byzantine attack on {target_validator.id}...")
    print(f"   Before attack - Trust Score: {target_validator.trust_score}")
    
    result = byzantine_attack.trigger(target_validator.id)
    if not result["success"]:
        print(f"❌ Attack failed: {result['message']}")
        return
    
    print(f"✅ {result['message']}")
    
    # Byzantine node'un trust score'u düşmeli (saldırı sırasında başka node'lar onu tespit eder)
    print("\n5️⃣  Observing Byzantine node behavior (20 seconds)...")
    for i in range(4):
        await asyncio.sleep(5)
        print(f"\n   ⏱️  {(i+1)*5}s:")
        print(f"      Byzantine {target_validator.id}:")
        print(f"         Trust Score: {target_validator.trust_score}")
        print(f"         Status: {target_validator.status}")
        print(f"         Is Byzantine: {target_validator.is_byzantine}")
        
        # Diğer validator'lar
        print(f"      Other validators:")
        for v in simulator.validator_nodes[1:]:
            print(f"         {v.id}: Trust={v.trust_score}")
    
    # Otomatik iyileşmeyi bekle
    print("\n6️⃣  Waiting for auto-recovery (10 seconds)...")
    await asyncio.sleep(10)
    
    # İyileşme sonrası durum
    print(f"\n📊 After Recovery:")
    print(f"   {target_validator.id}:")
    print(f"      Trust Score: {target_validator.trust_score}")
    print(f"      Status: {target_validator.status}")
    print(f"      Is Byzantine: {target_validator.is_byzantine}")
    
    print(f"\n   Other validators:")
    for v in simulator.validator_nodes[1:]:
        print(f"      {v.id}: Trust={v.trust_score}, Status={v.status}")
    
    # Trust score özeti
    print("\n7️⃣  Trust Score Summary:")
    print(f"   {'Node':<10} {'Initial':<10} {'Final':<10} {'Change':<10}")
    print(f"   {'-'*40}")
    for v in simulator.validator_nodes:
        initial = 100  # Başlangıç değeri
        final = v.trust_score
        change = final - initial
        status_icon = "⚠️" if v.id == target_validator.id else "✅"
        print(f"   {status_icon} {v.id:<10} {initial:<10} {final:<10} {change:+d}")
    
    # Beklenen davranış
    print("\n✅ Expected Behavior:")
    print("   1. Normal operation: Trust scores increase (+1 per correct PBFT action)")
    print("   2. Byzantine attack: Target node sends fake hash")
    print("   3. Detection: Other nodes reject fake hash, don't increase attacker's trust")
    print("   4. Recovery: Attacker's trust score penalized (-20)")
    print("   5. Result: Byzantine node has lower trust score than honest nodes")
    
    # Temizlik
    print("\n8️⃣  Cleanup...")
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
    asyncio.run(test_trust_score())
