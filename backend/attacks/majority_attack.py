"""
Majority Attack (%51 Attack) Implementation
"""
import asyncio
from typing import Optional, List
from datetime import datetime

class MajorityAttack:
    """Majority (%51) saldırısı simülasyonu
    
    Validator'ların %51'ini kontrol ederek kötü niyetli blokları onaylama saldırısı.
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
        
        # Saldırgan node'lar
        self.malicious_validators: List = []
        self.honest_validators: List = []
        
        # Orijinal değerler
        self.original_states = {}
        
        # Fork tracking
        self.fork_created = False
        self.malicious_chain_blocks = []
        self.honest_chain_blocks = []
    
    async def execute(self) -> str:
        """
        Majority saldırısını başlatır
        
        Returns:
            attack_id: Saldırı ID'si
        """
        from backend.attacks.attack_engine import AttackType
        
        # Validator'ları al
        validators = [n for n in self.simulator.nodes if n.role == "validator"]
        total_validators = len(validators)
        
        if total_validators < 2:
            raise ValueError("Majority attack için en az 2 validator gerekli")
        
        # %51'den fazlasını saldırgan yap
        malicious_count = (total_validators // 2) + 1
        self.malicious_validators = validators[:malicious_count]
        self.honest_validators = validators[malicious_count:]
        
        # Saldırıyı kaydet
        self.attack_id = self.attack_engine.trigger_attack(
            attack_type=AttackType.MAJORITY,
            target="network",
            parameters={
                "total_validators": total_validators,
                "malicious_validators": malicious_count,
                "honest_validators": len(self.honest_validators),
                "malicious_percentage": (malicious_count / total_validators) * 100
            }
        )
        
        # Saldırı etkilerini uygula
        await self._apply_attack_effects()
        
        # Saldırı etkilerini kaydet
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Compromised {malicious_count}/{total_validators} validators ({(malicious_count/total_validators)*100:.1f}%)"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Malicious validators: {', '.join([v.id for v in self.malicious_validators])}"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Network control achieved - malicious chain can be created"
        )
        
        # Otomatik iyileşme başlat (60 saniye)
        self.recovery_task = asyncio.create_task(self._auto_recovery())
        self.attack_engine.set_attack_task(self.attack_id, self.recovery_task)
        
        return self.attack_id
    
    async def _apply_attack_effects(self):
        """Saldırı etkilerini uygular"""
        # Saldırgan validator'ların durumunu değiştir
        for validator in self.malicious_validators:
            # Orijinal durumu sakla
            self.original_states[validator.id] = {
                "trust_score": validator.trust_score,
                "status": validator.status,
                "is_malicious": getattr(validator, "is_malicious", False)
            }
            
            # Saldırgan olarak işaretle
            validator.is_malicious = True
            validator.status = "under_attack"
            validator.trust_score = max(0, validator.trust_score - 30)
        
        # Fork oluştur
        self.fork_created = True
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Chain fork initiated - malicious validators creating alternative chain"
        )
        
        # Çift harcama senaryosu simüle et
        await self._simulate_double_spend()
    
    async def _simulate_double_spend(self):
        """Çift harcama senaryosunu simüle eder"""
        if not self.malicious_validators:
            return
        
        # İlk saldırgan validator'ı kullan
        attacker = self.malicious_validators[0]
        
        # Çift harcama transaction'ı oluştur (simüle)
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Double-spend transaction created by {attacker.id}"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Malicious chain attempting to replace honest chain"
        )
    
    async def _auto_recovery(self):
        """Saldırı sonrası otomatik iyileşme"""
        try:
            # Saldırı süresi (60 saniye)
            attack_duration = 60
            await asyncio.sleep(attack_duration)
            
            # İyileşme başlat
            self.attack_engine.add_attack_effect(
                self.attack_id,
                f"Attack duration ended ({attack_duration}s) - starting recovery"
            )
            
            # Fork çözümlemesi
            await self._resolve_fork()
            
            # Validator'ları temizle
            await self._cleanup_validators()
            
            # Tam iyileşme
            self.attack_engine.add_attack_effect(
                self.attack_id,
                "Network recovered - honest chain restored"
            )
            
            # Saldırıyı tamamla
            self.attack_engine.stop_attack(self.attack_id)
            
        except asyncio.CancelledError:
            # Manuel durdurma
            await self._cleanup_validators()
            self.attack_engine.add_attack_effect(
                self.attack_id,
                "Attack manually stopped - validators restored"
            )
    
    async def _resolve_fork(self):
        """Fork çözümler - en uzun zincir kazanır"""
        if not self.fork_created:
            return
        
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Fork resolution started - longest chain rule applied"
        )
        
        # Simülasyon: Honest chain kazanır (gerçekte en uzun olan kazanır)
        self.attack_engine.add_attack_effect(
            self.attack_id,
            "Honest chain prevailed - malicious blocks orphaned"
        )
        
        self.fork_created = False
    
    async def _cleanup_validators(self):
        """Validator'ları orijinal durumlarına döndürür"""
        for validator in self.malicious_validators:
            if validator.id in self.original_states:
                original = self.original_states[validator.id]
                validator.trust_score = original["trust_score"]
                validator.status = "healthy"
                validator.is_malicious = False
        
        self.malicious_validators.clear()
        self.honest_validators.clear()
        self.original_states.clear()
    
    def stop(self):
        """Saldırıyı manuel olarak durdurur"""
        if self.recovery_task and not self.recovery_task.done():
            self.recovery_task.cancel()
        if self.attack_id:
            self.attack_engine.stop_attack(self.attack_id)
    
    def get_status(self) -> dict:
        """Saldırı durumunu döndürür"""
        return {
            "active": self.attack_id is not None and self.recovery_task and not self.recovery_task.done(),
            "attack_id": self.attack_id,
            "malicious_validators": len(self.malicious_validators),
            "honest_validators": len(self.honest_validators),
            "fork_created": self.fork_created,
            "malicious_validator_ids": [v.id for v in self.malicious_validators]
        }
