"""
Network Partition Attack Implementation
"""
import asyncio
from typing import Optional, List, Set
from datetime import datetime

class NetworkPartition:
    """Network Partition saldırısı simülasyonu
    
    Ağı ikiye bölerek izole gruplar oluşturur ve paralel zincir oluşumunu simüle eder.
    """
    
    def __init__(self, simulator, attack_engine):
        """
        Args:
            simulator: Simulator referansı (node'lara erişim için)
            attack_engine: AttackEngine referansı
        """
        self.simulator = simulator
        self.attack_engine = attack_engine
        self.attack_id: Optional[str] = None
        self.recovery_task: Optional[asyncio.Task] = None
        
        # Partition grupları
        self.group_a: List = []
        self.group_b: List = []
        self.group_a_ids: Set[str] = set()
        self.group_b_ids: Set[str] = set()
        
        # Orijinal değerler
        self.original_states = {}
        
        # Partition durumu
        self.partition_active = False
        self.partition_line = None  # Group A ve B arasındaki bölme noktası
    
    async def execute(self) -> str:
        """
        Network partition saldırısını başlatır
        
        Returns:
            attack_id: Saldırı ID'si
        """
        from backend.attacks.attack_engine import AttackType
        
        # Tüm node'ları al
        all_nodes = self.simulator.nodes.copy()
        total_nodes = len(all_nodes)
        
        if total_nodes < 4:
            raise ValueError("Network partition için en az 4 node gerekli")

        # Ağı ikiye böl
        mid_point = total_nodes // 2
        self.group_a = all_nodes[:mid_point]
        self.group_b = all_nodes[mid_point:]

        # ID setlerini oluştur
        self.group_a_ids = {node.id for node in self.group_a}
        self.group_b_ids = {node.id for node in self.group_b}

        # ✅ EKLE - Console'a yazdır
        print("\n" + "=" * 60)
        print("🔴 NETWORK PARTITION ATTACK")
        print("=" * 60)
        print(f"📊 Total nodes: {total_nodes}")
        print(f"🔵 Group A ({len(self.group_a)} nodes): {[n.id for n in self.group_a]}")
        print(f"🔴 Group B ({len(self.group_b)} nodes): {[n.id for n in self.group_b]}")
        print(f"⚡ Groups isolated - parallel chains forming")
        print("=" * 60 + "\n")
        
        # Partition line hesapla (görselleştirme için)
        self.partition_line = mid_point
        
        # Saldırıyı kaydet
        self.attack_id = self.attack_engine.trigger_attack(
            attack_type=AttackType.NETWORK_PARTITION,
            target="network",
            parameters={
                "total_nodes": total_nodes,
                "group_a_size": len(self.group_a),
                "group_b_size": len(self.group_b),
                "partition_at": mid_point
            }
        )
        
        # Saldırı etkilerini uygula
        await self._apply_partition()
        
        # Saldırı etkilerini kaydet
        group_a_ids = [n.id for n in self.group_a]
        group_b_ids = [n.id for n in self.group_b]
        
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Network partitioned into 2 isolated groups"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Group A ({len(self.group_a)} nodes): {', '.join(group_a_ids[:3])}{'...' if len(group_a_ids) > 3 else ''}"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Group B ({len(self.group_b)} nodes): {', '.join(group_b_ids[:3])}{'...' if len(group_b_ids) > 3 else ''}"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Groups cannot communicate - parallel chains forming"
        )
        
        # Otomatik iyileşme başlat (45 saniye)
        self.recovery_task = asyncio.create_task(self._auto_recovery())
        self.attack_engine.set_attack_task(self.attack_id, self.recovery_task)
        
        return self.attack_id
    
    async def _apply_partition(self):
        """Partition'ı uygular - MessageBroker'a partition bilgisi ekler"""
        # MessageBroker'da partition aktif et
        if hasattr(self.simulator, 'message_broker'):
            self.simulator.message_broker.set_partition(
                self.group_a_ids,
                self.group_b_ids
            )
        
        # Node'ları işaretle
        for node in self.group_a:
            self.original_states[node.id] = {
                "status": node.status,
                "partition_group": None
            }
            node.status = "under_attack"
            node.partition_group = "A"
            # ✅ Fork detection'u aktif et
            node.blockchain.fork_detected = True
        
        for node in self.group_b:
            self.original_states[node.id] = {
                "status": node.status,
                "partition_group": None
            }
            node.status = "under_attack"
            node.partition_group = "B"
            # ✅ Fork detection'u aktif et
            node.blockchain.fork_detected = True
        
        self.partition_active = True
        
        # Paralel zincir oluşumu simülasyonu
        await asyncio.sleep(0.5)  # Simülasyon gecikmesi
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Parallel blockchain branches detected in each partition"
        )
    
    async def _auto_recovery(self):
        """Saldırı sonrası otomatik iyileşme ve merge"""
        try:
            # Saldırı süresi (45 saniye)
            attack_duration = 45
            await asyncio.sleep(attack_duration)
            
            # İyileşme başlat
            self.attack_engine.add_attack_effect(
                self.attack_id,
                f"Partition duration ended ({attack_duration}s) - merging partitions"
            )
            
            # Partition'ı kaldır ve merge yap
            await self._merge_partitions()
            
            # Tam iyileşme
            self.attack_engine.add_attack_effect(
                self.attack_id,
                "Network merged - single chain restored"
            )
            
            # Saldırıyı tamamla
            self.attack_engine.stop_attack(self.attack_id)
            
        except asyncio.CancelledError:
            # Manuel durdurma
            await self._merge_partitions()
            self.attack_engine.add_attack_effect(
                self.attack_id,
                "Partition manually stopped - network merged"
            )
    
    async def _merge_partitions(self):
        """Partition'ları birleştirir - en uzun zincir kazanır"""
        if not self.partition_active:
            return
        
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Merge process started - comparing chain lengths"
        )

        print("\n" + "=" * 60)
        print("🔍 PRE-MERGE FORK STATUS")
        print("=" * 60)
        for node in self.group_a[:1]:  # Sadece ilk node'u göster (örnek)
            fork_status = node.blockchain.get_fork_status()
            print(f"📊 Group A Sample ({node.id}):")
            print(f"   Main chain: {len(node.blockchain.chain)} blocks")
            print(f"   Alternative chains: {fork_status['alternative_chains_count']}")
            print(f"   Fork detected: {fork_status['fork_detected']}")
            break

        for node in self.group_b[:1]:  # Sadece ilk node'u göster (örnek)
            fork_status = node.blockchain.get_fork_status()
            print(f"📊 Group B Sample ({node.id}):")
            print(f"   Main chain: {len(node.blockchain.chain)} blocks")
            print(f"   Alternative chains: {fork_status['alternative_chains_count']}")
            print(f"   Fork detected: {fork_status['fork_detected']}")
            break
        print("=" * 60 + "\n")
        
        # Her grubun en uzun zincirini bul
        group_a_chains = [(n, len(n.blockchain.chain)) for n in self.group_a]
        group_b_chains = [(n, len(n.blockchain.chain)) for n in self.group_b]
        
        group_a_max_length = max([length for _, length in group_a_chains], default=0)
        group_b_max_length = max([length for _, length in group_b_chains], default=0)
        
        # ✅ FORK TESPİT ET - Partition sırasında farklı uzunluklar = fork
        if group_a_max_length != group_b_max_length:
            # Tüm node'larda fork_detected flag'ini set et
            for node in self.group_a + self.group_b:
                node.blockchain.fork_detected = True
        
        # En uzun zinciri belirle
        winner_group = "A" if group_a_max_length >= group_b_max_length else "B"
        winner_length = max(group_a_max_length, group_b_max_length)
        loser_length = min(group_a_max_length, group_b_max_length)
        
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Group {winner_group} chain won (length: {winner_length} vs {loser_length})"
        )
        
        # Kazanıcı grubu belirle
        winner_nodes = self.group_a if winner_group == "A" else self.group_b
        loser_nodes = self.group_b if winner_group == "A" else self.group_a
        
        # En uzun zinciri bul
        winner_chain_node = None
        for node, length in (group_a_chains if winner_group == "A" else group_b_chains):
            if length == winner_length:
                winner_chain_node = node
                break
        
        # ✅ TÜM NODE'LARI KAZANAN ZİNCİRLE SENKRONİZE ET
        # ✅ TÜM NODE'LARI KAZANAN ZİNCİRLE SENKRONİZE ET
        orphaned_blocks = 0
        if winner_chain_node:
            winner_chain = winner_chain_node.blockchain.chain

            # Kaybeden grubu güncelle
            for loser_node in loser_nodes:
                loser_chain_length = len(loser_node.blockchain.chain)

                # Kaybeden zincir orphaned olarak işaretle
                if loser_chain_length > 0:
                    # Fork tespit et ve kaydet
                    loser_node.blockchain.detect_fork(winner_chain)
                    # Kazanan zinciri kabul et (resolve_fork zaten orphan'ları işaretler)
                    loser_node.blockchain.resolve_fork(winner_chain)

                    # Orphaned block sayısını hesapla
                    fork_point = 0
                    for i in range(min(len(loser_node.blockchain.chain), len(winner_chain))):
                        if loser_node.blockchain.chain[i].hash != winner_chain[i].hash:
                            fork_point = i
                            break
                    orphaned_blocks += (loser_chain_length - fork_point)

            # ✅ KAZANAN GRUBU DA GÜNCELLEMELİYİZ
            for winner_node in winner_nodes:
                # Kendi gruptaki alternatif zincirleri de temizle
                if winner_node.blockchain.alternative_chains:
                    winner_node.blockchain.resolve_fork(winner_chain)

                # En uzun zinciri al
                if len(winner_node.blockchain.chain) < winner_length:
                    winner_node.blockchain.chain = [b for b in winner_chain]
                    print(f"✅ Synced {winner_node.id} to winning chain ({winner_length} blocks)")
            
            # ✅ KAZANAN GRUBU DA GÜNCELLEMELİYİZ (kısa olanlar varsa)
            for winner_node in winner_nodes:
                if len(winner_node.blockchain.chain) < winner_length:
                    # Bu node kazanan gruptaki en uzun zinciri almamış
                    winner_node.blockchain.chain = [b for b in winner_chain]
                    print(f"✅ Synced {winner_node.id} to winning chain ({winner_length} blocks)")
        
        # Merge sonucunu yazdır
        print("\n" + "=" * 60)
        print("🔗 PARTITION MERGE")
        print("=" * 60)
        print(f"🏆 Winner: Group {winner_group} (chain length: {winner_length})")
        print(f"❌ Loser: Group {'B' if winner_group == 'A' else 'A'} (chain length: {loser_length})")
        print(f"📦 {orphaned_blocks} blocks orphaned")
        print("=" * 60 + "\n")
        
        if orphaned_blocks > 0:
            self.attack_engine.add_attack_effect(
                self.attack_id,
                f"{orphaned_blocks} blocks from losing partition marked as orphaned"
            )
        
        # MessageBroker'da partition'ı kaldır
        if hasattr(self.simulator, 'message_broker'):
            self.simulator.message_broker.clear_partition()
        
        # Node'ları temizle
        await self._cleanup_nodes()
        
        # Simülasyon: Zincir senkronizasyonu
        await asyncio.sleep(0.5)
        
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"All nodes synchronized to winning chain (length: {winner_length})"
        )
        
        self.partition_active = False
    
    async def _cleanup_nodes(self):
        """Node'ları orijinal durumlarına döndürür"""
        all_partition_nodes = self.group_a + self.group_b
        
        for node in all_partition_nodes:
            if node.id in self.original_states:
                original = self.original_states[node.id]
                node.status = "healthy"
                node.partition_group = None
                # ✅ Fork resolved - flag'ı temizle
                node.blockchain.fork_detected = False
        
        self.group_a.clear()
        self.group_b.clear()
        self.group_a_ids.clear()
        self.group_b_ids.clear()
        self.original_states.clear()
        self.partition_line = None
    
    def stop(self):
        """Saldırıyı manuel olarak durdurur"""
        if self.recovery_task and not self.recovery_task.done():
            self.recovery_task.cancel()
        if self.attack_id:
            self.attack_engine.stop_attack(self.attack_id)
    
    def get_status(self) -> dict:
        """Saldırı durumunu döndürür"""
        return {
            "active": self.partition_active,
            "attack_id": self.attack_id,
            "group_a_size": len(self.group_a),
            "group_b_size": len(self.group_b),
            "group_a_ids": [n.id for n in self.group_a],
            "group_b_ids": [n.id for n in self.group_b],
            "partition_line": self.partition_line,
            "partition_active": self.partition_active
        }
