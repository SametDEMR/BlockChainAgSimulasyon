"""
PBFT Handler - Practical Byzantine Fault Tolerance Consensus
4 Aşamalı konsensüs protokolü: Pre-Prepare -> Prepare -> Commit -> Reply
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class PBFTMessage:
    """PBFT protokol mesajı"""
    phase: str  # "pre_prepare", "prepare", "commit"
    view: int
    sequence_number: int
    block_hash: str
    node_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'phase': self.phase,
            'view': self.view,
            'sequence_number': self.sequence_number,
            'block_hash': self.block_hash,
            'node_id': self.node_id,
            'timestamp': self.timestamp.isoformat()
        }


class PBFTHandler:
    """
    PBFT Consensus Handler
    
    Her validator node için bir PBFT handler instance'ı
    4 fazlı konsensüs protokolü:
    1. Pre-Prepare: Primary validator blok önerir
    2. Prepare: Validator'lar hazır olduklarını bildirir
    3. Commit: Validator'lar commit kararı verir
    4. Reply: Blok zincire eklenir
    """
    
    def __init__(self, node_id: str, total_validators: int):
        """
        Args:
            node_id: Bu handler'ın sahibi node ID
            total_validators: Toplam validator sayısı
        """
        self.node_id = node_id
        self.total_validators = total_validators
        
        # PBFT durumu
        self.view = 0  # Mevcut view numarası
        self.sequence_number = 0  # Son işlenen sequence
        
        # Konsensüs için gereken minimum onay sayısı
        # Byzantine fault tolerance: f = (n-1)/3, gereken = 2f + 1
        self.f = (total_validators - 1) // 3
        self.required_votes = 2 * self.f + 1
        
        # Mesaj kayıtları (sequence_number -> phase -> node_id -> message)
        self.message_log: Dict[int, Dict[str, Dict[str, PBFTMessage]]] = {}
        
        # View change tracking
        self.view_change_votes: Dict[int, Set[str]] = {}  # new_view -> node_ids
        
        # İstatistikler
        self.total_consensus_reached = 0
        self.total_view_changes = 0
        self.blocks_validated = 0
        
    def is_primary(self) -> bool:
        """Bu node primary validator mı?"""
        # Primary selection: view % total_validators
        # İlk validator (view 0'da) primary başlar
        return self.view % self.total_validators == int(self.node_id.split('_')[1]) if '_' in self.node_id else False
    
    def get_primary_id(self) -> str:
        """Mevcut view'daki primary validator ID'si"""
        primary_index = self.view % self.total_validators
        return f"node_{primary_index}"
    
    def create_pre_prepare(self, block_hash: str, sequence_number: int) -> PBFTMessage:
        """
        Pre-Prepare mesajı oluştur (sadece primary)
        
        Args:
            block_hash: Önerilen blok hash'i
            sequence_number: Sıra numarası
        """
        if not self.is_primary():
            raise ValueError(f"Node {self.node_id} is not primary in view {self.view}")
        
        return PBFTMessage(
            phase='pre_prepare',
            view=self.view,
            sequence_number=sequence_number,
            block_hash=block_hash,
            node_id=self.node_id
        )
    
    def process_pre_prepare(self, message: PBFTMessage) -> Optional[PBFTMessage]:
        """
        Pre-Prepare mesajını işle ve Prepare mesajı üret
        
        Returns:
            Prepare mesajı veya None (geçersizse)
        """
        # View kontrolü
        if message.view != self.view:
            return None
        
        # Primary kontrolü
        expected_primary = self.get_primary_id()
        if message.node_id != expected_primary:
            return None
        
        # Sequence kontrolü
        if message.sequence_number <= self.sequence_number:
            return None
        
        # Mesajı kaydet
        self._log_message(message)
        
        # Prepare mesajı oluştur
        return PBFTMessage(
            phase='prepare',
            view=self.view,
            sequence_number=message.sequence_number,
            block_hash=message.block_hash,
            node_id=self.node_id
        )
    
    def process_prepare(self, message: PBFTMessage) -> Optional[PBFTMessage]:
        """
        Prepare mesajını işle ve yeterli prepare varsa Commit mesajı üret
        
        Returns:
            Commit mesajı veya None
        """
        # View ve sequence kontrolü
        if message.view != self.view:
            return None
        
        # Mesajı kaydet
        self._log_message(message)
        
        # Yeterli prepare mesajı var mı? (2f + 1)
        prepare_count = self._count_messages(message.sequence_number, 'prepare', message.block_hash)
        
        if prepare_count >= self.required_votes:
            # Commit mesajı oluştur
            return PBFTMessage(
                phase='commit',
                view=self.view,
                sequence_number=message.sequence_number,
                block_hash=message.block_hash,
                node_id=self.node_id
            )
        
        return None
    
    def process_commit(self, message: PBFTMessage) -> bool:
        """
        Commit mesajını işle ve konsensüs sağlandı mı kontrol et
        
        Returns:
            True: Konsensüs sağlandı, blok eklenebilir
            False: Henüz yeterli commit yok
        """
        # View ve sequence kontrolü
        if message.view != self.view:
            return False
        
        # Mesajı kaydet
        self._log_message(message)
        
        # Yeterli commit mesajı var mı? (2f + 1)
        commit_count = self._count_messages(message.sequence_number, 'commit', message.block_hash)
        
        if commit_count >= self.required_votes:
            # Konsensüs sağlandı!
            self.sequence_number = message.sequence_number
            self.total_consensus_reached += 1
            self.blocks_validated += 1
            return True
        
        return False
    
    def validate_block(self, block_hash: str) -> bool:
        """
        Blok hash'ini validate et (basit kontrol)
        
        Gerçek uygulamada:
        - Block data integrity
        - Transaction validity
        - Previous block hash
        vb. kontroller yapılır
        """
        # Şimdilik basit: hash var mı kontrolü
        return len(block_hash) > 0
    
    def trigger_view_change(self, reason: str = "timeout"):
        """
        View change tetikle
        
        Durumlar:
        - Primary timeout
        - Byzantine davranış tespit
        - Network problemi
        """
        new_view = self.view + 1
        
        # View change vote kaydet
        if new_view not in self.view_change_votes:
            self.view_change_votes[new_view] = set()
        
        self.view_change_votes[new_view].add(self.node_id)
        
        # Yeterli vote var mı?
        if len(self.view_change_votes[new_view]) >= self.required_votes:
            # View change!
            self.view = new_view
            self.total_view_changes += 1
            
            # View change sonrası log temizliği
            self._cleanup_old_logs()
            
            return True
        
        return False
    
    def vote_for_view_change(self, new_view: int, voter_id: str) -> bool:
        """
        Başka bir node'un view change vote'unu kaydet
        
        Returns:
            True: View change gerçekleşti
            False: Henüz yeterli vote yok
        """
        if new_view not in self.view_change_votes:
            self.view_change_votes[new_view] = set()
        
        self.view_change_votes[new_view].add(voter_id)
        
        # Yeterli vote var mı?
        if len(self.view_change_votes[new_view]) >= self.required_votes:
            self.view = new_view
            self.total_view_changes += 1
            self._cleanup_old_logs()
            return True
        
        return False
    
    def _log_message(self, message: PBFTMessage):
        """Mesajı internal log'a kaydet"""
        seq = message.sequence_number
        phase = message.phase
        
        if seq not in self.message_log:
            self.message_log[seq] = {}
        
        if phase not in self.message_log[seq]:
            self.message_log[seq][phase] = {}
        
        self.message_log[seq][phase][message.node_id] = message
    
    def _count_messages(self, sequence_number: int, phase: str, block_hash: str) -> int:
        """Belirli bir sequence ve phase için mesaj sayısını döndür"""
        if sequence_number not in self.message_log:
            return 0
        
        if phase not in self.message_log[sequence_number]:
            return 0
        
        # Aynı block_hash için olan mesajları say
        count = 0
        for msg in self.message_log[sequence_number][phase].values():
            if msg.block_hash == block_hash:
                count += 1
        
        return count
    
    def _cleanup_old_logs(self):
        """Eski sequence'lerin loglarını temizle"""
        # Sadece son 10 sequence'i tut
        sequences_to_keep = list(self.message_log.keys())[-10:]
        new_log = {}
        
        for seq in sequences_to_keep:
            new_log[seq] = self.message_log[seq]
        
        self.message_log = new_log
    
    def get_consensus_status(self, sequence_number: int, block_hash: str) -> Dict:
        """Belirli bir sequence için konsensüs durumunu döndür"""
        return {
            'sequence_number': sequence_number,
            'block_hash': block_hash,
            'view': self.view,
            'pre_prepare_received': self._count_messages(sequence_number, 'pre_prepare', block_hash) > 0,
            'prepare_count': self._count_messages(sequence_number, 'prepare', block_hash),
            'commit_count': self._count_messages(sequence_number, 'commit', block_hash),
            'required_votes': self.required_votes,
            'prepare_ready': self._count_messages(sequence_number, 'prepare', block_hash) >= self.required_votes,
            'commit_ready': self._count_messages(sequence_number, 'commit', block_hash) >= self.required_votes
        }
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndür"""
        return {
            'node_id': self.node_id,
            'view': self.view,
            'sequence_number': self.sequence_number,
            'is_primary': self.is_primary(),
            'primary_id': self.get_primary_id(),
            'total_validators': self.total_validators,
            'required_votes': self.required_votes,
            'f': self.f,
            'total_consensus_reached': self.total_consensus_reached,
            'total_view_changes': self.total_view_changes,
            'blocks_validated': self.blocks_validated,
            'pending_sequences': len(self.message_log)
        }
