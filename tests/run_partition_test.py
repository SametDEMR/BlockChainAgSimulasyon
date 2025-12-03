"""
Network Partition Attack Test
Direkt çalıştırın: python tests/run_partition_test.py
"""
import asyncio
import sys
import os

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulator import Simulator
from backend.attacks.attack_engine import AttackEngine
from backend.attacks.network_partition import NetworkPartition


async def run_test():
    """Network Partition test"""
    print("\n" + "=" * 60)
    print("TEST: Network Partition Attack")
    print("=" * 60)
    
    try:
        # Setup
        print("\n[Setup] Simulator başlatılıyor...")
        simulator = Simulator()
        attack_engine = AttackEngine()
        partition = NetworkPartition(simulator, attack_engine)
        
        total_nodes = len(simulator.nodes)
        print(f"✓ Simulator hazır: {total_nodes} node")
        
        # Test 1: Partition tetikle
        print("\n[Test 1] Partition tetikleme...")
        attack_id = await partition.execute()
        print(f"✓ Attack ID: {attack_id}")
        
        await asyncio.sleep(1)
        
        # Test 2: Partition durumu
        print("\n[Test 2] Partition durumu kontrol...")
        status = partition.get_status()
        print(f"✓ Active: {status['active']}")
        print(f"✓ Group A: {status['group_a_size']} nodes")
        print(f"✓ Group B: {status['group_b_size']} nodes")
        
        # Test 3: MessageBroker
        print("\n[Test 3] MessageBroker partition kontrol...")
        broker = simulator.message_broker.get_partition_status()
        print(f"✓ Active: {broker['active']}")
        print(f"✓ Blocked messages: {broker['blocked_messages']}")
        
        # Test 4: Node grupları
        print("\n[Test 4] Node partition grupları...")
        group_a = [n for n in simulator.nodes if n.partition_group == "A"]
        group_b = [n for n in simulator.nodes if n.partition_group == "B"]
        print(f"✓ Group A: {len(group_a)} nodes")
        print(f"✓ Group B: {len(group_b)} nodes")
        
        # Test 5: Mesaj bloklama
        print("\n[Test 5] Mesaj bloklama testi...")
        if group_a and group_b:
            node_a_id = group_a[0].id
            node_b_id = group_b[0].id
            
            blocked_before = broker['blocked_messages']
            await simulator.message_broker.send_message(
                node_a_id, node_b_id, "test", {"data": "test"}
            )
            
            broker = simulator.message_broker.get_partition_status()
            blocked_after = broker['blocked_messages']
            
            print(f"✓ Blocked: {blocked_before} -> {blocked_after}")
            assert blocked_after > blocked_before, "Mesaj bloke edilmeliydi"
            print(f"✓ Farklı gruplara mesaj başarıyla bloke edildi")
        
        # Test 6: Manuel stop
        print("\n[Test 6] Manuel stop...")
        partition.stop()
        await asyncio.sleep(1)
        print("✓ Stop komutu gönderildi")
        
        # Test 7: Cleanup kontrolü
        print("\n[Test 7] Cleanup kontrolü...")
        final_status = partition.get_status()
        final_broker = simulator.message_broker.get_partition_status()
        
        print(f"✓ Partition active: {final_status['active']}")
        print(f"✓ MessageBroker active: {final_broker['active']}")
        
        # Assertions
        print("\n[Assertions] Kontroller yapılıyor...")
        assert status['active'] == True, "❌ Partition aktif olmalıydı"
        assert status['group_a_size'] > 0, "❌ Group A boş olmamalı"
        assert status['group_b_size'] > 0, "❌ Group B boş olmamalı"
        assert final_status['active'] == False, "❌ Stop sonrası inactive olmalı"
        assert final_broker['active'] == False, "❌ MessageBroker partition temizlenmeli"
        print("✓ Tüm assertion'lar geçti")
        
        print("\n" + "=" * 60)
        print("✅ TÜM TESTLER BAŞARILI")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION HATASI: {e}")
        return False
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ana fonksiyon"""
    print("\n🚀 Network Partition Test Başlatılıyor...")
    success = asyncio.run(run_test())
    
    if success:
        print("\n✅ Test başarıyla tamamlandı!")
        sys.exit(0)
    else:
        print("\n❌ Test başarısız!")
        sys.exit(1)


if __name__ == "__main__":
    main()
