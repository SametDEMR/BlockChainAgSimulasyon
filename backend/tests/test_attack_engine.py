"""
Attack Engine Test
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.attacks.attack_engine import AttackEngine, AttackType, AttackStatus
import time

def test_attack_engine():
    """AttackEngine temel fonksiyonlarını test eder"""
    
    print("=" * 60)
    print("ATTACK ENGINE TEST")
    print("=" * 60)
    
    # Attack Engine oluştur
    engine = AttackEngine()
    print("\n✓ Attack Engine oluşturuldu")
    
    # İlk istatistikler
    stats = engine.get_statistics()
    print(f"\n📊 Başlangıç İstatistikleri:")
    print(f"   Total Attacks: {stats['total_attacks_triggered']}")
    print(f"   Active Attacks: {stats['active_attacks_count']}")
    print(f"   Completed Attacks: {stats['completed_attacks_count']}")
    
    # DDoS saldırısı tetikle
    print("\n" + "-" * 60)
    print("1. DDoS Saldırısı Tetikleme")
    print("-" * 60)
    
    attack_id = engine.trigger_attack(
        attack_type=AttackType.DDOS,
        target="node_5",
        parameters={"intensity": "high", "duration": 20}
    )
    
    print(f"✓ Saldırı tetiklendi: {attack_id}")
    
    # Saldırı durumunu kontrol et
    status = engine.get_attack_status(attack_id)
    print(f"\n📋 Saldırı Durumu:")
    print(f"   ID: {status['attack_id']}")
    print(f"   Type: {status['attack_type']}")
    print(f"   Target: {status['target']}")
    print(f"   Status: {status['status']}")
    print(f"   Started: {status['started_at']}")
    print(f"   Active: {status['is_active']}")
    
    # Saldırıya etki ekle
    engine.add_attack_effect(attack_id, "Response time increased to 5 seconds")
    engine.add_attack_effect(attack_id, "Node CPU usage at 95%")
    
    status = engine.get_attack_status(attack_id)
    print(f"\n💥 Saldırı Etkileri:")
    for i, effect in enumerate(status['effects'], 1):
        print(f"   {i}. {effect}")
    
    # Aktif saldırıları listele
    active = engine.get_active_attacks()
    print(f"\n⚡ Aktif Saldırılar: {len(active)}")
    
    # İkinci bir saldırı tetikle
    print("\n" + "-" * 60)
    print("2. Byzantine Saldırısı Tetikleme")
    print("-" * 60)
    
    attack_id_2 = engine.trigger_attack(
        attack_type=AttackType.BYZANTINE,
        target="node_0",
        parameters={"behavior": "send_invalid_hash"}
    )
    
    print(f"✓ Saldırı tetiklendi: {attack_id_2}")
    
    # Şimdi 2 aktif saldırı olmalı
    active = engine.get_active_attacks()
    print(f"\n⚡ Toplam Aktif Saldırılar: {len(active)}")
    for attack in active:
        print(f"   - {attack['attack_id']}: {attack['attack_type']} -> {attack['target']}")
    
    # İlk saldırıyı durdur
    print("\n" + "-" * 60)
    print("3. Saldırı Durdurma")
    print("-" * 60)
    
    time.sleep(0.1)  # Biraz bekle
    
    success = engine.stop_attack(attack_id)
    print(f"✓ Saldırı durduruldu: {success}")
    
    # Durdurulmuş saldırı kontrolü
    status = engine.get_attack_status(attack_id)
    print(f"\n📋 Durdurulmuş Saldırı:")
    print(f"   Status: {status['status']}")
    print(f"   Duration: {status['duration']:.2f} seconds")
    print(f"   Active: {status['is_active']}")
    
    # Aktif saldırılar (1 olmalı)
    active = engine.get_active_attacks()
    print(f"\n⚡ Kalan Aktif Saldırılar: {len(active)}")
    
    # Geçmiş
    history = engine.get_attack_history()
    print(f"\n📜 Saldırı Geçmişi: {len(history)}")
    for attack in history:
        print(f"   - {attack['attack_id']}: {attack['attack_type']} (Duration: {attack['duration']:.2f}s)")
    
    # Son istatistikler
    print("\n" + "-" * 60)
    print("4. Final İstatistikler")
    print("-" * 60)
    
    stats = engine.get_statistics()
    print(f"\n📊 Attack Engine Stats:")
    print(f"   Total Triggered: {stats['total_attacks_triggered']}")
    print(f"   Active: {stats['active_attacks_count']}")
    print(f"   Completed: {stats['completed_attacks_count']}")
    print(f"   Active Types: {stats['active_attack_types']}")
    
    # Reset
    print("\n" + "-" * 60)
    print("5. Reset Test")
    print("-" * 60)
    
    engine.reset()
    print("✓ Engine reset edildi")
    
    stats = engine.get_statistics()
    print(f"\n📊 Reset Sonrası:")
    print(f"   Total Triggered: {stats['total_attacks_triggered']}")
    print(f"   Active: {stats['active_attacks_count']}")
    print(f"   Completed: {stats['completed_attacks_count']}")
    
    print("\n" + "=" * 60)
    print("✅ TÜM TESTLER BAŞARILI!")
    print("=" * 60)

if __name__ == "__main__":
    test_attack_engine()
