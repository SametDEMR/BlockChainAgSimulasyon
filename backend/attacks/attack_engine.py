"""
Attack Engine - Saldırı yönetim ve koordinasyon modülü
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class AttackType(Enum):
    """Desteklenen saldırı türleri"""
    DDOS = "ddos"
    BYZANTINE = "byzantine"
    SYBIL = "sybil"
    MAJORITY = "majority_attack"
    NETWORK_PARTITION = "network_partition"
    SELFISH_MINING = "selfish_mining"

class AttackStatus(Enum):
    """Saldırı durumları"""
    IDLE = "idle"
    ACTIVE = "active"
    RECOVERING = "recovering"
    COMPLETED = "completed"

class Attack:
    """Tek bir saldırıyı temsil eden sınıf"""
    
    def __init__(
        self,
        attack_id: str,
        attack_type: AttackType,
        target: Any,
        parameters: Dict[str, Any]
    ):
        self.attack_id = attack_id
        self.attack_type = attack_type
        self.target = target
        self.parameters = parameters
        self.status = AttackStatus.IDLE
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.effects: List[str] = []
        self.task: Optional[asyncio.Task] = None
        
    def to_dict(self) -> dict:
        """Saldırı bilgilerini dict olarak döndürür"""
        return {
            "attack_id": self.attack_id,
            "attack_type": self.attack_type.value,
            "target": str(self.target) if self.target else None,
            "parameters": self.parameters,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": (
                (self.ended_at - self.started_at).total_seconds()
                if self.started_at and self.ended_at
                else None
            ),
            "effects": self.effects,
            "is_active": self.status == AttackStatus.ACTIVE
        }

class AttackEngine:
    """Saldırı motoru - tüm saldırıları yönetir"""
    
    def __init__(self):
        self.active_attacks: Dict[str, Attack] = {}
        self.attack_history: List[Attack] = []
        self.total_attacks_triggered = 0
        
    def trigger_attack(
        self,
        attack_type: AttackType,
        target: Any,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Saldırı tetikler
        
        Args:
            attack_type: Saldırı tipi
            target: Hedef (node, node_id, vb.)
            parameters: Saldırı parametreleri
            
        Returns:
            attack_id: Oluşturulan saldırı ID'si
        """
        attack_id = f"attack_{self.total_attacks_triggered + 1}"
        self.total_attacks_triggered += 1
        
        attack = Attack(
            attack_id=attack_id,
            attack_type=attack_type,
            target=target,
            parameters=parameters or {}
        )
        
        attack.status = AttackStatus.ACTIVE
        attack.started_at = datetime.now()
        
        self.active_attacks[attack_id] = attack
        
        return attack_id
    
    def stop_attack(self, attack_id: str) -> bool:
        """
        Aktif saldırıyı durdurur
        
        Args:
            attack_id: Saldırı ID'si
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        if attack_id not in self.active_attacks:
            return False
        
        attack = self.active_attacks[attack_id]
        
        # Task varsa iptal et
        if attack.task and not attack.task.done():
            attack.task.cancel()
        
        attack.status = AttackStatus.COMPLETED
        attack.ended_at = datetime.now()
        
        # History'ye ekle ve active'den çıkar
        self.attack_history.append(attack)
        del self.active_attacks[attack_id]
        
        return True
    
    def get_attack_status(self, attack_id: str) -> Optional[dict]:
        """
        Saldırı durumunu döndürür
        
        Args:
            attack_id: Saldırı ID'si
            
        Returns:
            dict: Saldırı bilgileri veya None
        """
        # Önce aktif saldırılara bak
        if attack_id in self.active_attacks:
            return self.active_attacks[attack_id].to_dict()
        
        # History'de ara
        for attack in self.attack_history:
            if attack.attack_id == attack_id:
                return attack.to_dict()
        
        return None
    
    def get_active_attacks(self) -> List[dict]:
        """Tüm aktif saldırıları döndürür"""
        return [attack.to_dict() for attack in self.active_attacks.values()]
    
    def get_attack_history(self, limit: int = 10) -> List[dict]:
        """
        Saldırı geçmişini döndürür
        
        Args:
            limit: Döndürülecek maksimum kayıt sayısı
            
        Returns:
            List[dict]: Saldırı geçmişi (en yeniden eskiye)
        """
        return [
            attack.to_dict()
            for attack in reversed(self.attack_history[-limit:])
        ]
    
    def add_attack_effect(self, attack_id: str, effect: str):
        """
        Saldırıya etki ekler
        
        Args:
            attack_id: Saldırı ID'si
            effect: Etki açıklaması
        """
        if attack_id in self.active_attacks:
            self.active_attacks[attack_id].effects.append(effect)
    
    def set_attack_task(self, attack_id: str, task: asyncio.Task):
        """
        Saldırıya asyncio task atar
        
        Args:
            attack_id: Saldırı ID'si
            task: Asyncio task
        """
        if attack_id in self.active_attacks:
            self.active_attacks[attack_id].task = task
    
    def get_statistics(self) -> dict:
        """Saldırı motoru istatistiklerini döndürür"""
        return {
            "total_attacks_triggered": self.total_attacks_triggered,
            "active_attacks_count": len(self.active_attacks),
            "completed_attacks_count": len(self.attack_history),
            "active_attack_types": list(set(
                attack.attack_type.value
                for attack in self.active_attacks.values()
            ))
        }
    
    def reset(self):
        """Saldırı motorunu sıfırlar"""
        # Tüm aktif taskları iptal et
        for attack in self.active_attacks.values():
            if attack.task and not attack.task.done():
                attack.task.cancel()
        
        self.active_attacks.clear()
        self.attack_history.clear()
        self.total_attacks_triggered = 0
