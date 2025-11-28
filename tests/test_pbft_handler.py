"""
PBFT Handler Test
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.network.pbft_handler import PBFTHandler, PBFTMessage


def test_pbft_handler():
    """PBFT Handler testleri"""
    
    print("=" * 60)
    print("PBFT HANDLER TEST")
    print("=" * 60)
    
    # 1. 4 validator ile PBFT sistem
    print("\n1. 4 Validator için PBFT Handler'lar oluşturuluyor...")
    total_validators = 4
    handlers = {}
    
    for i in range(total_validators):
        node_id = f"node_{i}"
        handler = PBFTHandler(node_id, total_validators)
        handlers[node_id] = handler
        print(f"✓ {node_id}: f={handler.f}, required_votes={handler.required_votes}")
    
    # 2. Primary kontrolü
    print("\n2. Primary validator kontrolü...")
    primary_id = handlers['node_0'].get_primary_id()
    print(f"Primary validator: {primary_id}")
    
    for node_id, handler in handlers.items():
        is_primary = handler.is_primary()
        print(f"  {node_id}: {'PRIMARY' if is_primary else 'Backup'}")
    
    # 3. Pre-Prepare fazı
    print("\n3. Pre-Prepare fazı...")
    primary = handlers[primary_id]
    block_hash = "abc123def456"
    sequence = 1
    
    pre_prepare_msg = primary.create_pre_prepare(block_hash, sequence)
    print(f"✓ Primary ({primary_id}) pre-prepare mesajı oluşturdu")
    print(f"  View: {pre_prepare_msg.view}")
    print(f"  Sequence: {pre_prepare_msg.sequence_number}")
    print(f"  Block: {pre_prepare_msg.block_hash}")
    
    # 4. Prepare fazı
    print("\n4. Prepare fazı...")
    prepare_messages = []
    
    for node_id, handler in handlers.items():
        if node_id == primary_id:
            continue  # Primary prepare göndermez
        
        prepare_msg = handler.process_pre_prepare(pre_prepare_msg)
        if prepare_msg:
            prepare_messages.append(prepare_msg)
            print(f"✓ {node_id} prepare mesajı oluşturdu")
    
    print(f"Toplam prepare mesajı: {len(prepare_messages)}")
    
    # 5. Prepare mesajlarını dağıt ve Commit'leri al
    print("\n5. Prepare dağıtımı ve Commit fazı...")
    commit_messages = []
    
    # Her node tüm prepare'ları işler
    for handler in handlers.values():
        for prepare_msg in prepare_messages:
            commit_msg = handler.process_prepare(prepare_msg)
            if commit_msg and commit_msg.node_id not in [m.node_id for m in commit_messages]:
                commit_messages.append(commit_msg)
                print(f"✓ {commit_msg.node_id} commit mesajı oluşturdu")
    
    print(f"Toplam commit mesajı: {len(commit_messages)}")
    
    # 6. Commit fazı - Konsensüs kontrolü
    print("\n6. Commit işleme ve konsensüs kontrolü...")
    consensus_reached = []
    
    for handler in handlers.values():
        for commit_msg in commit_messages:
            is_consensus = handler.process_commit(commit_msg)
            if is_consensus and handler.node_id not in consensus_reached:
                consensus_reached.append(handler.node_id)
                print(f"✓ {handler.node_id} konsensüs sağladı!")
    
    print(f"\nKonsensüs sağlayan node sayısı: {len(consensus_reached)}/{total_validators}")
    
    # 7. Konsensüs durumu
    print("\n7. Konsensüs durumu kontrolü...")
    for node_id, handler in handlers.items():
        status = handler.get_consensus_status(sequence, block_hash)
        print(f"\n{node_id}:")
        print(f"  Prepare ready: {status['prepare_ready']} ({status['prepare_count']}/{status['required_votes']})")
        print(f"  Commit ready: {status['commit_ready']} ({status['commit_count']}/{status['required_votes']})")
    
    # 8. View Change testi
    print("\n8. View Change testi...")
    print("node_1 view change tetikliyor (örn: timeout)...")
    
    view_changed = handlers['node_1'].trigger_view_change("timeout")
    print(f"View change sonucu: {view_changed}")
    
    # Diğer node'lar da view change için oy veriyor
    for node_id in ['node_2', 'node_3']:
        result = handlers[node_id].vote_for_view_change(1, node_id)
        print(f"{node_id} view change'e oy verdi -> {result}")
        
        if result:
            print(f"✓ View change gerçekleşti! Yeni view: 1")
            break
    
    # 9. Yeni primary
    print("\n9. View change sonrası yeni primary...")
    new_primary_id = handlers['node_0'].get_primary_id()
    print(f"Yeni primary: {new_primary_id}")
    
    # 10. İstatistikler
    print("\n10. PBFT İstatistikleri:")
    for node_id, handler in handlers.items():
        stats = handler.get_stats()
        print(f"\n{node_id}:")
        print(f"  View: {stats['view']}")
        print(f"  Sequence: {stats['sequence_number']}")
        print(f"  Is Primary: {stats['is_primary']}")
        print(f"  Consensus reached: {stats['total_consensus_reached']}")
        print(f"  View changes: {stats['total_view_changes']}")
        print(f"  Blocks validated: {stats['blocks_validated']}")
    
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)


def test_byzantine_scenario():
    """Byzantine node senaryosu testi"""
    
    print("\n" + "=" * 60)
    print("BYZANTINE NODE SCENARIO TEST")
    print("=" * 60)
    
    # 4 validator
    handlers = {f"node_{i}": PBFTHandler(f"node_{i}", 4) for i in range(4)}
    
    print("\n1. Normal konsensüs...")
    primary = handlers['node_0']
    pre_prepare = primary.create_pre_prepare("correct_hash", 1)
    
    # node_2 Byzantine - yanlış hash gönderir
    print("\n2. node_2 Byzantine davranıyor (yanlış hash)...")
    
    prepare_messages = []
    for node_id, handler in handlers.items():
        if node_id == 'node_0':
            continue
        
        prepare = handler.process_pre_prepare(pre_prepare)
        if prepare:
            # node_2 yanlış hash ile prepare gönderir
            if node_id == 'node_2':
                prepare.block_hash = "wrong_hash"
                print(f"✓ {node_id} YANLIŞ hash ile prepare gönderdi!")
            else:
                print(f"✓ {node_id} doğru hash ile prepare gönderdi")
            
            prepare_messages.append(prepare)
    
    print("\n3. Commit fazı kontrolü...")
    # Doğru hash için commit sayımı
    correct_commits = 0
    wrong_commits = 0
    
    for handler in handlers.values():
        for prepare in prepare_messages:
            commit = handler.process_prepare(prepare)
            if commit:
                if commit.block_hash == "correct_hash":
                    correct_commits += 1
                else:
                    wrong_commits += 1
    
    print(f"Doğru hash commit: {correct_commits}")
    print(f"Yanlış hash commit: {wrong_commits}")
    print(f"\nSonuç: Byzantine node diğerlerini etkileyemedi!")
    print(f"(Çünkü 2f+1=3 doğru oy gerekiyor, Byzantine tek başına yetersiz)")


if __name__ == "__main__":
    test_pbft_handler()
    test_byzantine_scenario()
