"""
Test Network Partition Resolution (7.2)
Partition merge, longest chain rule, orphan blocks
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulator import Simulator
from backend.attacks.attack_engine import AttackEngine
from backend.attacks.network_partition import NetworkPartition


async def run_test():
    """Network Partition Resolution test"""
    print("\n" + "=" * 60)
    print("TEST: Network Partition Resolution (Milestone 7.2)")
    print("=" * 60)
    
    try:
        # Setup
        print("\n[Setup] Simulator başlatılıyor...")
        simulator = Simulator()
        attack_engine = AttackEngine()
        partition = NetworkPartition(simulator, attack_engine)
        
        simulator.start()
        print(f"✓ Simulator başlatıldı: {len(simulator.nodes)} node")
        
        # İlk durum
        initial_lengths = [len(n.blockchain.chain) for n in simulator.nodes]
        print(f"✓ İlk chain uzunlukları: {initial_lengths}")
        
        # Test 1: Partition oluştur
        print("\n[Test 1] Partition oluşturma...")
        attack_id = await partition.execute()
        print(f"✓ Attack ID: {attack_id}")
        
        await asyncio.sleep(1)
        
        status = partition.get_status()
        group_a_ids = status['group_a_ids']
        group_b_ids = status['group_b_ids']
        print(f"✓ Group A: {len(group_a_ids)} nodes")
        print(f"✓ Group B: {len(group_b_ids)} nodes")
        
        # Test 2: Her grupta blok üretimi simüle et
        print("\n[Test 2] Her grupta farklı sayıda blok üretimi...")
        
        # Group A'da 3 blok üret
        for node in simulator.nodes:
            if node.id in group_a_ids and node.role == "regular":
                for i in range(3):
                    block = node.mine_block()
                    if block:
                        print(f"  Group A - {node.id}: Block {block.index}")
                break
        
        # Group B'de 2 blok üret
        for node in simulator.nodes:
            if node.id in group_b_ids and node.role == "regular":
                for i in range(2):
                    block = node.mine_block()
                    if block:
                        print(f"  Group B - {node.id}: Block {block.index}")
                break
        
        await asyncio.sleep(1)
        
        # Test 3: Partition sırasında chain uzunlukları
        print("\n[Test 3] Partition sırasında chain uzunlukları...")
        group_a_lengths = [len(n.blockchain.chain) for n in simulator.nodes if n.id in group_a_ids]
        group_b_lengths = [len(n.blockchain.chain) for n in simulator.nodes if n.id in group_b_ids]
        
        group_a_max = max(group_a_lengths) if group_a_lengths else 0
        group_b_max = max(group_b_lengths) if group_b_lengths else 0
        
        print(f"  Group A max chain: {group_a_max}")
        print(f"  Group B max chain: {group_b_max}")
        print(f"✓ Beklenen kazanan: Group {'A' if group_a_max >= group_b_max else 'B'}")
        
        # Test 4: Manuel stop ile merge tetikle
        print("\n[Test 4] Merge işlemi başlatılıyor...")
        partition.stop()
        await asyncio.sleep(2)  # Merge için bekle
        
        # Test 5: Merge sonrası kontrol
        print("\n[Test 5] Merge sonrası kontroller...")
        
        # Partition temizlendi mi?
        final_status = partition.get_status()
        final_broker = simulator.message_broker.get_partition_status()
        
        print(f"✓ Partition active: {final_status['active']}")
        print(f"✓ MessageBroker partition: {final_broker['active']}")
        
        # Test 6: Fork durumu
        print("\n[Test 6] Fork durumu kontrol...")
        fork_count = 0
        orphan_count = 0
        
        for node in simulator.nodes:
            fork_status = node.blockchain.get_fork_status()
            if fork_status['fork_detected']:
                fork_count += 1
            orphan_count += fork_status['orphaned_blocks_count']  # Düzeltildi
        
        print(f"✓ Fork tespit edilen node sayısı: {fork_count}")
        print(f"✓ Toplam orphan block: {orphan_count}")
        
        # Test 7: Chain senkronizasyonu
        print("\n[Test 7] Chain senkronizasyonu kontrol...")
        final_lengths = [len(n.blockchain.chain) for n in simulator.nodes]
        max_chain = max(final_lengths)
        min_chain = min(final_lengths)
        
        print(f"✓ Max chain length: {max_chain}")
        print(f"✓ Min chain length: {min_chain}")
        print(f"✓ Chain length farkı: {max_chain - min_chain}")
        
        # Test 8: Attack effects
        print("\n[Test 8] Attack effects kontrol...")
        attack_info = attack_engine.get_attack_status(attack_id)
        if attack_info and attack_info['effects']:
            print(f"✓ Toplam {len(attack_info['effects'])} effect kaydedildi")
            
            # Merge ile ilgili effect'leri bul
            merge_effects = [e for e in attack_info['effects'] if 'merge' in e.lower() or 'orphan' in e.lower()]
            if merge_effects:
                print(f"✓ Merge effects ({len(merge_effects)}):")
                for effect in merge_effects[:3]:
                    print(f"    • {effect}")
        
        # Cleanup
        simulator.stop()
        
        # Assertions
        print("\n[Assertions] Final kontroller...")
        assert final_status['active'] == False, "❌ Partition inactive olmalı"
        assert final_broker['active'] == False, "❌ MessageBroker partition temiz olmalı"
        assert orphan_count > 0, "❌ Orphan block olmalı"
        assert max_chain >= max(group_a_max, group_b_max), "❌ En uzun chain kazanmalı"
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
    print("\n🚀 Network Partition Resolution Test Başlatılıyor...")
    success = asyncio.run(run_test())
    
    if success:
        print("\n✅ Test başarıyla tamamlandı!")
        sys.exit(0)
    else:
        print("\n❌ Test başarısız!")
        sys.exit(1)


if __name__ == "__main__":
    main()
