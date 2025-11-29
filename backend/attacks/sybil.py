"""
Sybil Attack Implementation
Çok sayıda sahte node oluşturarak ağı manipüle eder
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List
from .attack_engine import Attack, AttackType, AttackStatus


class SybilAttack(Attack):
    """Sybil Attack - Çok sayıda sahte node oluşturma"""
    
    def __init__(self, simulator):
        super().__init__(
            attack_id=f"sybil_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            attack_type=AttackType.SYBIL,
            target=None,
            parameters={}
        )
        self.simulator = simulator
        self.fake_nodes: List[str] = []  # Sahte node ID'leri
        self.num_fake_nodes = 0
        self.recovery_task = None
        self.start_time = None
        self.end_time = None
        
    async def trigger(self, num_nodes: int = 20) -> bool:
        """
        Sybil saldırısını başlat
        Args:
            num_nodes: Oluşturulacak sahte node sayısı (varsayılan: 20)
        Returns:
            bool: Başarı durumu
        """
        try:
            if self.status == AttackStatus.ACTIVE:
                return False
            
            self.num_fake_nodes = num_nodes
            self.status = AttackStatus.ACTIVE
            self.start_time = datetime.now()
            
            # Sahte node'ları oluştur
            for i in range(num_nodes):
                node_id = f"sybil_{self.attack_id}_{i}"
                # Simülatörde yeni sahte node oluştur
                fake_node = self.simulator._create_sybil_node(node_id)
                self.fake_nodes.append(node_id)
                
            # Etkileri kaydet
            self.effects = [
                f"Created {num_nodes} fake nodes",
                f"Network size increased from {len(self.simulator.nodes) - num_nodes} to {len(self.simulator.nodes)}",
                "Network topology manipulated",
                "Consensus process may be affected",
                "Real nodes may be outnumbered"
            ]
            
            # Otomatik iyileşme başlat (60 saniye)
            self.recovery_task = asyncio.create_task(self._auto_recovery())
            
            return True
            
        except Exception as e:
            self.status = AttackStatus.COMPLETED
            self.effects.append(f"Error: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Saldırıyı durdur ve sahte node'ları temizle"""
        try:
            if self.status != AttackStatus.ACTIVE:
                return False
            
            # Recovery task'i iptal et
            if self.recovery_task and not self.recovery_task.done():
                self.recovery_task.cancel()
                
            # Sahte node'ları kaldır
            for node_id in self.fake_nodes:
                self.simulator._remove_sybil_node(node_id)
            
            self.status = AttackStatus.COMPLETED
            self.end_time = datetime.now()
            self.effects.append(f"Removed all {len(self.fake_nodes)} fake nodes")
            self.fake_nodes = []
            
            return True
            
        except Exception as e:
            self.effects.append(f"Error during stop: {str(e)}")
            return False
    
    async def _auto_recovery(self):
        """Otomatik iyileşme - 60 saniye sonra sahte node'ları temizle"""
        try:
            await asyncio.sleep(60)  # 60 saniye bekle
            
            # Recovering durumuna geç
            self.status = AttackStatus.RECOVERING
            self.effects.append("Auto-recovery initiated")
            
            # Kademeli olarak sahte node'ları kaldır
            total_nodes = len(self.fake_nodes)
            for i, node_id in enumerate(self.fake_nodes[:]):
                self.simulator._remove_sybil_node(node_id)
                self.fake_nodes.remove(node_id)
                # Her 5 node'da bir kısa bekle
                if (i + 1) % 5 == 0:
                    await asyncio.sleep(0.5)
            
            self.status = AttackStatus.COMPLETED
            self.end_time = datetime.now()
            self.effects.append(f"Recovery complete - removed {total_nodes} fake nodes")
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.effects.append(f"Recovery error: {str(e)}")
            self.status = AttackStatus.COMPLETED
    
    def get_status(self) -> Dict[str, Any]:
        """Saldırı durumunu döndür"""
        base_status = self.to_dict()
        base_status["parameters"] = {
            "num_fake_nodes": self.num_fake_nodes,
            "active_fake_nodes": len(self.fake_nodes)
        }
        base_status["fake_node_ids"] = self.fake_nodes
        base_status["effects"] = self.effects
        return base_status
