"""
DDoS Attack Implementation
"""
import asyncio
from typing import Optional
from datetime import datetime, timedelta

class DDoSAttack:
    """DDoS (Distributed Denial of Service) saldırısı simülasyonu"""
    
    def __init__(self, target_node, attack_engine, intensity: str = "high"):
        """
        Args:
            target_node: Hedef node
            attack_engine: AttackEngine referansı
            intensity: Saldırı yoğunluğu (low, medium, high)
        """
        self.target_node = target_node
        self.attack_engine = attack_engine
        self.intensity = intensity
        self.attack_id: Optional[str] = None
        self.recovery_task: Optional[asyncio.Task] = None
        
        # Yoğunluğa göre parametreler
        self.intensity_params = {
            "low": {
                "response_time_multiplier": 2.0,
                "duration": 10,
                "cpu_usage": 70
            },
            "medium": {
                "response_time_multiplier": 5.0,
                "duration": 15,
                "cpu_usage": 85
            },
            "high": {
                "response_time_multiplier": 10.0,
                "duration": 20,
                "cpu_usage": 95
            }
        }
        
        self.params = self.intensity_params.get(intensity, self.intensity_params["high"])
        
        # Orijinal değerleri sakla
        self.original_response_time = target_node.response_time
        self.original_status = target_node.status
    
    async def execute(self) -> str:
        """
        DDoS saldırısını başlatır
        
        Returns:
            attack_id: Saldırı ID'si
        """
        from backend.attacks.attack_engine import AttackType
        
        # Saldırıyı attack engine'e kaydet
        self.attack_id = self.attack_engine.trigger_attack(
            attack_type=AttackType.DDOS,
            target=self.target_node.id,
            parameters={
                "intensity": self.intensity,
                "duration": self.params["duration"],
                "cpu_usage": self.params["cpu_usage"]
            }
        )
        
        # Node'u saldırı altına al
        self._apply_attack_effects()
        
        # Saldırı etkilerini kaydet
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Node {self.target_node.id} response time increased to {self.target_node.response_time:.2f}s"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Node CPU usage at {self.params['cpu_usage']}%"
        )
        self.attack_engine.add_attack_effect(
            self.attack_id,
            f"Node status changed to 'under_attack'"
        )
        
        # Otomatik iyileşme başlat
        self.recovery_task = asyncio.create_task(self._auto_recovery())
        self.attack_engine.set_attack_task(self.attack_id, self.recovery_task)
        
        return self.attack_id
    
    def _apply_attack_effects(self):
        """Saldırı etkilerini node'a uygular"""
        # Response time'ı artır
        self.target_node.response_time = (
            self.original_response_time * self.params["response_time_multiplier"]
        )
        
        # Status'u değiştir
        self.target_node.status = "under_attack"
        
        # CPU metrikleri eklenebilir (opsiyonel)
        if not hasattr(self.target_node, 'cpu_usage'):
            self.target_node.cpu_usage = 0
        self.target_node.cpu_usage = self.params["cpu_usage"]
    
    async def _auto_recovery(self):
        """Saldırı sonrası otomatik iyileşme"""
        try:
            # Saldırı süresince bekle
            await asyncio.sleep(self.params["duration"])
            
            # İyileşme başlat
            self.target_node.status = "recovering"
            self.attack_engine.add_attack_effect(
                self.attack_id,
                f"Recovery started after {self.params['duration']}s"
            )
            
            # İyileşme süresi
            recovery_duration = 5
            steps = 5
            
            for step in range(1, steps + 1):
                await asyncio.sleep(recovery_duration / steps)
                
                # Kademeli iyileşme
                progress = step / steps
                self.target_node.response_time = (
                    self.params["response_time_multiplier"] * self.original_response_time * (1 - progress) +
                    self.original_response_time * progress
                )
                
                if hasattr(self.target_node, 'cpu_usage'):
                    self.target_node.cpu_usage = int(
                        self.params["cpu_usage"] * (1 - progress) + 20 * progress
                    )
            
            # Tam iyileşme
            self.target_node.response_time = self.original_response_time
            self.target_node.status = "healthy"
            if hasattr(self.target_node, 'cpu_usage'):
                self.target_node.cpu_usage = 20
            
            self.attack_engine.add_attack_effect(
                self.attack_id,
                f"Node fully recovered after {recovery_duration}s"
            )
            
            # Saldırıyı tamamla
            self.attack_engine.stop_attack(self.attack_id)
            
        except asyncio.CancelledError:
            # Manuel durdurma
            self.target_node.response_time = self.original_response_time
            self.target_node.status = "healthy"
            if hasattr(self.target_node, 'cpu_usage'):
                self.target_node.cpu_usage = 20
            self.attack_engine.add_attack_effect(
                self.attack_id,
                "Attack manually stopped"
            )
    
    def stop(self):
        """Saldırıyı manuel olarak durdurur"""
        # İlk önce node'u düzelt
        self.target_node.response_time = self.original_response_time
        self.target_node.status = "healthy"
        if hasattr(self.target_node, 'cpu_usage'):
            self.target_node.cpu_usage = 20
        
        # Sonra task'i cancel et
        if self.recovery_task and not self.recovery_task.done():
            self.recovery_task.cancel()
        if self.attack_id:
            self.attack_engine.stop_attack(self.attack_id)
