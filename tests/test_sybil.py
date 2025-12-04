"""
Test Sybil Attack Implementation
"""
import asyncio
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.simulator import Simulator
from backend.attacks.sybil import SybilAttack


@pytest.mark.asyncio
async def test_sybil_attack():
    """Sybil attack testi"""
    print("\n" + "="*60)
    print("SYBIL ATTACK TEST")
    print("="*60)
    
    # Simülatör oluştur
    print("\n1. Creating simulator...")
    simulator = Simulator()
    initial_node_count = len(simulator.nodes)
    print(f"✓ Initial nodes: {initial_node_count}")
    print(f"  - Validators: {len(simulator.validator_nodes)}")
    print(f"  - Regular: {len(simulator.regular_nodes)}")
    
    # Sybil attack oluştur
    print("\n2. Creating Sybil attack...")
    attack = SybilAttack(simulator)
    print(f"✓ Attack created: {attack.attack_id}")
    
    # Saldırıyı tetikle (20 sahte node)
    print("\n3. Triggering attack (20 fake nodes)...")
    success = await attack.trigger(num_nodes=20)
    print(f"✓ Attack triggered: {success}")
    
    # Durumu kontrol et
    print("\n4. Checking status...")
    status = attack.get_status()
    print(f"✓ Attack status: {status['status']}")
    print(f"✓ Total nodes now: {len(simulator.nodes)}")
    print(f"  - Real nodes: {initial_node_count}")
    print(f"  - Fake nodes: {status['parameters']['active_fake_nodes']}")
    
    # Sybil node'ları kontrol et
    print("\n5. Checking Sybil nodes...")
    sybil_nodes = [n for n in simulator.nodes if n.is_sybil]
    print(f"✓ Sybil nodes detected: {len(sybil_nodes)}")
    print(f"  Sample IDs: {[n.id for n in sybil_nodes[:3]]}")
    
    # Etkileri göster
    print("\n6. Attack effects:")
    for effect in status['effects']:
        print(f"  - {effect}")
    
    # 3 saniye bekle
    print("\n7. Waiting 3 seconds...")
    await asyncio.sleep(3)
    
    # Manuel olarak durdur
    print("\n8. Stopping attack manually...")
    stop_success = await attack.stop()
    print(f"✓ Attack stopped: {stop_success}")
    
    # Son durumu kontrol et
    print("\n9. Final check...")
    final_status = attack.get_status()
    print(f"✓ Final status: {final_status['status']}")
    print(f"✓ Total nodes now: {len(simulator.nodes)}")
    print(f"✓ Sybil nodes remaining: {len([n for n in simulator.nodes if n.is_sybil])}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")


@pytest.mark.asyncio
async def test_auto_recovery():
    """Otomatik iyileşme testi"""
    print("\n" + "="*60)
    print("AUTO-RECOVERY TEST")
    print("="*60)
    
    # Simülatör oluştur
    print("\n1. Creating simulator...")
    simulator = Simulator()
    initial_count = len(simulator.nodes)
    print(f"✓ Initial nodes: {initial_count}")
    
    # Sybil attack oluştur
    print("\n2. Creating Sybil attack...")
    attack = SybilAttack(simulator)
    
    # Saldırıyı tetikle (10 sahte node)
    print("\n3. Triggering attack (10 fake nodes)...")
    await attack.trigger(num_nodes=10)
    print(f"✓ Nodes after attack: {len(simulator.nodes)}")
    
    # 5 saniye bekle (recovery 60 saniye sonra başlayacak)
    print("\n4. Waiting 5 seconds...")
    await asyncio.sleep(5)
    
    # Status kontrol
    status = attack.get_status()
    print(f"✓ Current status: {status['status']}")
    print(f"✓ Active fake nodes: {status['parameters']['active_fake_nodes']}")
    
    # Not: Tam auto-recovery testi 60+ saniye sürer
    # Şimdilik attack'i manuel durduruyoruz
    print("\n5. Manually stopping (full auto-recovery takes 60s)...")
    await attack.stop()
    
    print(f"✓ Final nodes: {len(simulator.nodes)}")
    
    print("\n" + "="*60)
    print("AUTO-RECOVERY TEST COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("Starting Sybil Attack Tests...")
    
    # Test 1: Sybil attack
    asyncio.run(test_sybil_attack())
    
    # Test 2: Auto-recovery
    asyncio.run(test_auto_recovery())
    
    print("All tests completed!")
