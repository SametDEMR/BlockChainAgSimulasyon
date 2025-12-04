"""
DDoS Attack Test
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import pytest
from backend.attacks.attack_engine import AttackEngine
from backend.attacks.ddos import DDoSAttack
from backend.network.node import Node


@pytest.mark.asyncio
async def test_ddos_attack():
    """DDoS saldırısını test eder"""
    
    print("=" * 60)
    print("DDOS ATTACK TEST")
    print("=" * 60)
    
    # Test için bir node oluştur
    print("\n📦 Test Node Oluşturuluyor...")
    node = Node(
        role="regular",
        total_validators=4,
        message_broker=None
    )
    
    print(f"✓ Node oluşturuldu: {node.id}")
    print(f"   Orijinal Status: {node.status}")
    print(f"   Orijinal Response Time: {node.response_time}s")
    
    # Attack Engine oluştur
    engine = AttackEngine()
    print("\n✓ Attack Engine oluşturuldu")
    
    # HIGH intensity DDoS saldırısı
    print("\n" + "-" * 60)
    print("1. HIGH Intensity DDoS Saldırısı")
    print("-" * 60)
    
    ddos = DDoSAttack(
        target_node=node,
        attack_engine=engine,
        intensity="high"
    )
    
    attack_id = await ddos.execute()
    print(f"\n✓ DDoS saldırısı başlatıldı: {attack_id}")
    
    # Saldırı anındaki durum
    print(f"\n💥 Saldırı Anındaki Node Durumu:")
    print(f"   Status: {node.status}")
    print(f"   Response Time: {node.response_time:.2f}s")
    print(f"   CPU Usage: {node.cpu_usage}%")
    
    # Saldırı durumu
    status = engine.get_attack_status(attack_id)
    print(f"\n📋 Saldırı Bilgileri:")
    print(f"   Type: {status['attack_type']}")
    print(f"   Target: {status['target']}")
    print(f"   Status: {status['status']}")
    print(f"   Parameters: {status['parameters']}")
    
    print(f"\n⏱️  Saldırı Etkileri:")
    for i, effect in enumerate(status['effects'], 1):
        print(f"   {i}. {effect}")
    
    # 5 saniye bekle (saldırı devam ediyor)
    print(f"\n⏳ 5 saniye bekleniyor... (saldırı devam ediyor)")
    await asyncio.sleep(5)
    
    print(f"\n📊 5 saniye sonraki durum:")
    print(f"   Status: {node.status}")
    print(f"   Response Time: {node.response_time:.2f}s")
    
    # Tüm süreç boyunca bekle (toplam 20s saldırı + 5s iyileşme = 25s)
    print(f"\n⏳ Otomatik iyileşme bekleniyor... (20s saldırı + 5s recovery)")
    await asyncio.sleep(21)  # Kalan süre: 16s + 5s recovery = 21s
    
    # Recovery sırasındaki durum
    print(f"\n🔄 Recovery Sırasındaki Durum:")
    print(f"   Status: {node.status}")
    print(f"   Response Time: {node.response_time:.2f}s")
    if hasattr(node, 'cpu_usage'):
        print(f"   CPU Usage: {node.cpu_usage}%")
    
    # Son kontrol (tam iyileşme)
    await asyncio.sleep(5)
    
    print(f"\n✅ Tam İyileşme Sonrası:")
    print(f"   Status: {node.status}")
    print(f"   Response Time: {node.response_time:.2f}s")
    if hasattr(node, 'cpu_usage'):
        print(f"   CPU Usage: {node.cpu_usage}%")
    
    # Final saldırı durumu
    final_status = engine.get_attack_status(attack_id)
    print(f"\n📋 Final Saldırı Durumu:")
    print(f"   Status: {final_status['status']}")
    print(f"   Duration: {final_status['duration']:.2f}s")
    print(f"   Total Effects: {len(final_status['effects'])}")
    
    print(f"\n⏱️  Tüm Etki Geçmişi:")
    for i, effect in enumerate(final_status['effects'], 1):
        print(f"   {i}. {effect}")
    
    # Test 2: MEDIUM intensity
    print("\n" + "-" * 60)
    print("2. MEDIUM Intensity DDoS Saldırısı")
    print("-" * 60)
    
    node2 = Node(
        role="regular",
        total_validators=4,
        message_broker=None
    )
    
    ddos2 = DDoSAttack(
        target_node=node2,
        attack_engine=engine,
        intensity="medium"
    )
    
    attack_id_2 = await ddos2.execute()
    print(f"\n✓ MEDIUM DDoS başlatıldı: {attack_id_2}")
    print(f"   Response Time: {node2.response_time:.2f}s")
    print(f"   CPU Usage: {node2.cpu_usage}%")
    
    # 3 saniye bekle sonra manuel durdur
    await asyncio.sleep(3)
    
    print(f"\n⏹️  Manuel Durdurma Test")
    ddos2.stop()
    await asyncio.sleep(0.5)
    
    print(f"   Status: {node2.status}")
    print(f"   Response Time: {node2.response_time:.2f}s")
    
    # Engine istatistikleri
    print("\n" + "-" * 60)
    print("3. Attack Engine İstatistikleri")
    print("-" * 60)
    
    stats = engine.get_statistics()
    print(f"\n📊 Engine Stats:")
    print(f"   Total Triggered: {stats['total_attacks_triggered']}")
    print(f"   Active: {stats['active_attacks_count']}")
    print(f"   Completed: {stats['completed_attacks_count']}")
    
    active_attacks = engine.get_active_attacks()
    print(f"\n⚡ Aktif Saldırılar: {len(active_attacks)}")
    
    history = engine.get_attack_history()
    print(f"\n📜 Tamamlanmış Saldırılar: {len(history)}")
    for attack in history:
        print(f"   - {attack['attack_id']}: {attack['parameters']['intensity']} intensity, "
              f"{attack['duration']:.1f}s duration")
    
    print("\n" + "=" * 60)
    print("✅ TÜM TESTLER BAŞARILI!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ddos_attack())
