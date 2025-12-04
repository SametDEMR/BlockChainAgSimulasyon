"""
Byzantine Attack Implementation

Bir validator node'u Byzantine (hatalı) davranışa geçirir.
Byzantine node PBFT sürecinde hatalı hash gönderir ve view change tetiklenir.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ByzantineAttack:
    """
    Byzantine Node Attack simülasyonu
    
    Bir validator'ı seçer ve hatalı blok hash'leri göndermesini sağlar.
    PBFT protokolünde konsensüs başarısız olur ve view change tetiklenir.
    Saldırgan node'un trust score'u düşer.
    """
    
    def __init__(self, simulator):
        """
        Args:
            simulator: Network simulator instance
        """
        self.simulator = simulator
        self.target_node_id: Optional[str] = None
        self.is_active = False
        self.start_time: Optional[datetime] = None
        self.attack_duration = 30  # Saldırı süresi (saniye)
        self.original_behavior = None  # Node'un orijinal davranışı
        
    def trigger(self, target_node_id: str) -> dict:
        """
        Byzantine saldırısını başlat
        
        Args:
            target_node_id: Hedef validator node ID
            
        Returns:
            Saldırı durumu bilgisi
        """
        # Target node'u kontrol et
        target_node = self.simulator.get_node(target_node_id)
        if not target_node:
            return {
                "success": False,
                "message": f"Node {target_node_id} not found"
            }
            
        if target_node.role != "validator":
            return {
                "success": False,
                "message": f"Node {target_node_id} is not a validator"
            }
            
        if self.is_active:
            return {
                "success": False,
                "message": "Byzantine attack already active"
            }
        
        # Saldırıyı başlat
        self.target_node_id = target_node_id
        self.is_active = True
        self.start_time = datetime.now()
        
        # Node'u Byzantine olarak işaretle
        target_node.is_byzantine = True
        target_node.status = "under_attack"
        
        # Trust score'ı hemen düşür (saldırı başlatıldığında)
        target_node.trust_score = max(0, target_node.trust_score - 20)
        
        # Byzantine davranış: PBFT pre-prepare mesajında hatalı hash gönder
        # Node'un propose_block metodunu override ederiz
        self.original_behavior = target_node.propose_block
        target_node.propose_block = self._create_byzantine_propose_block(target_node)
        
        logger.info(f"Byzantine attack triggered on node {target_node_id}")
        
        # Otomatik iyileşme task'i başlat
        asyncio.create_task(self._auto_recovery())
        
        return {
            "success": True,
            "message": f"Byzantine attack started on validator {target_node_id}",
            "target_node": target_node_id,
            "duration": self.attack_duration
        }
    
    def _create_byzantine_propose_block(self, node):
        """
        Byzantine propose_block metodu oluştur
        
        Node'un orijinal propose_block metodunu hatalı hash göndermek için override eder.
        """
        original_method = self.original_behavior
        
        async def byzantine_propose_block():
            """
            Byzantine versiyonu - Hatalı hash gönderir
            """
            # Orijinal metod gibi blok oluştur
            if not node.blockchain.pending_transactions:
                # Boş transaction ile coinbase oluştur
                coinbase_tx = {
                    'sender': 'COINBASE',
                    'receiver': node.wallet.address,
                    'amount': 50,
                    'timestamp': datetime.now().isoformat(),
                    'signature': None
                }
                node.blockchain.pending_transactions.append(coinbase_tx)
            
            # Blok oluştur
            new_block = node.blockchain.mine_pending_transactions(node.wallet.address)
            
            if new_block and node.pbft:
                # HATA: Kasıtlı olarak yanlış hash gönder
                fake_hash = "0" * 64  # Tamamen yanlış hash
                
                logger.warning(f"Byzantine node {node.id} sending FAKE hash: {fake_hash[:16]}...")
                
                # Pre-prepare mesajı gönder ama YANLIŞ hash ile
                from backend.network.pbft_handler import PBFTMessage
                pre_prepare_msg = PBFTMessage(
                    phase="pre-prepare",
                    view=node.pbft.view,
                    sequence_number=node.pbft.sequence_number,
                    block_hash=fake_hash,  # ❌ YANLIŞ HASH
                    node_id=node.id
                )
                
                # Mesajı broadcast et
                await node.message_broker.broadcast(
                    sender_id=node.id,
                    message_type="pbft",
                    content=pre_prepare_msg.to_dict()
                )
                
                # Sequence number'ı artır
                node.pbft.sequence_number += 1
                
                logger.info(f"Byzantine node {node.id} proposed block with FAKE hash")
                
                return new_block
            
            return None
        
        return byzantine_propose_block
    
    async def _auto_recovery(self):
        """
        Otomatik iyileşme - Belirli süre sonra saldırı durur
        """
        await asyncio.sleep(self.attack_duration)
        
        if self.is_active:
            self.stop()
            logger.info(f"Byzantine attack auto-recovery completed for node {self.target_node_id}")
    
    def stop(self) -> dict:
        """
        Byzantine saldırısını durdur
        
        Returns:
            İyileşme durumu bilgisi
        """
        if not self.is_active:
            return {
                "success": False,
                "message": "No active Byzantine attack"
            }
        
        # Node'u bul
        target_node = self.simulator.get_node(self.target_node_id)
        if target_node:
            # Byzantine flag'i kaldır
            target_node.is_byzantine = False
            target_node.status = "recovering"
            
            # Orijinal davranışı geri yükle
            if self.original_behavior:
                target_node.propose_block = self.original_behavior
            
            # Trust score biraz düşür (ceza)
            target_node.trust_score = max(0, target_node.trust_score - 20)
            
            logger.info(f"Byzantine node {self.target_node_id} recovered. New trust score: {target_node.trust_score}")
            
            # Kısa süre sonra status'u healthy'ye çevir
            asyncio.create_task(self._restore_health(target_node))
        
        # Saldırı durumunu temizle
        self.is_active = False
        result = {
            "success": True,
            "message": f"Byzantine attack stopped on node {self.target_node_id}",
            "target_node": self.target_node_id,
            "attack_duration": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
        
        self.target_node_id = None
        self.start_time = None
        self.original_behavior = None
        
        return result
    
    async def _restore_health(self, node):
        """
        Node'un sağlığını geri yükle (5 saniye sonra)
        """
        await asyncio.sleep(5)
        if node.status == "recovering":
            node.status = "healthy"
            logger.info(f"Node {node.id} fully recovered")
    
    def get_status(self) -> dict:
        """
        Saldırı durumunu döndür
        
        Returns:
            Saldırı durumu bilgisi
        """
        if not self.is_active:
            return {
                "active": False,
                "target_node": None,
                "elapsed_time": 0,
                "remaining_time": 0
            }
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        remaining = max(0, self.attack_duration - elapsed)
        
        return {
            "active": True,
            "target_node": self.target_node_id,
            "elapsed_time": round(elapsed, 1),
            "remaining_time": round(remaining, 1),
            "attack_duration": self.attack_duration
        }
