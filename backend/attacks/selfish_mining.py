"""
Selfish Mining Attack Implementation

Bir node private chain tutarak diğer node'lardan önde kalır.
Public chain'den 2+ blok ileri olduğunda private chain'i yayınlar.
Public chain geçersiz olur ve selfish miner kazanç elde eder.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import'ları önce yapalım
try:
    from backend.core.transaction import Transaction
    from backend.core.blockchain import Blockchain
except ImportError:
    # Relative import denemesi
    from ..core.transaction import Transaction
    from ..core.blockchain import Blockchain


class SelfishMining:
    """
    Selfish Mining Attack simülasyonu
    
    Bir node seçer ve private chain tutmasını sağlar.
    Private chain public'ten 2+ blok önde olduğunda yayınlanır.
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
        self.attack_duration = 60  # Saldırı süresi (saniye)
        self.reveal_threshold = 2  # Private chain kaç blok önde olmalı
        self.blocks_mined_private = 0  # Private chain'de mine edilen blok sayısı
        self.blocks_revealed = 0  # Yayınlanan blok sayısı
        
    def trigger(self, target_node_id: str) -> dict:
        """
        Selfish mining saldırısını başlat
        
        Args:
            target_node_id: Hedef node ID (regular veya validator)
            
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
            
        if self.is_active:
            return {
                "success": False,
                "message": "Selfish mining attack already active"
            }
        
        # Saldırıyı başlat
        self.target_node_id = target_node_id
        self.is_active = True
        self.start_time = datetime.now()
        self.blocks_mined_private = 0
        self.blocks_revealed = 0
        
        # Node'u selfish miner olarak başlat
        target_node.start_selfish_mining()
        target_node.status = "under_attack"
        
        logger.info(f"Selfish mining attack triggered on node {target_node_id}")
        
        # Private chain mining task'i başlat
        asyncio.create_task(self._private_mining_loop())
        
        # Otomatik iyileşme task'i başlat
        asyncio.create_task(self._auto_recovery())
        
        return {
            "success": True,
            "message": f"Selfish mining started on node {target_node_id}",
            "target_node": target_node_id,
            "duration": self.attack_duration,
            "reveal_threshold": self.reveal_threshold
        }
    
    async def _private_mining_loop(self):
        """
        Private chain'de sürekli blok üretimi
        Public chain'den önde kalana kadar mine eder
        """
        while self.is_active:
            target_node = self.simulator.get_node(self.target_node_id)
            if not target_node or not target_node.is_selfish_miner:
                break
            
            # Private chain'de blok mine et
            if target_node.private_chain:
                # Transaction ekle (fake transaction)
                if len(target_node.private_chain.pending_transactions) == 0:
                    # Coinbase transaction ekle (Transaction objesi olarak)
                    coinbase_tx = Transaction(
                        sender='COINBASE',
                        receiver=target_node.wallet.address,
                        amount=50
                    )
                    target_node.private_chain.pending_transactions.append(coinbase_tx)
                
                # Private chain'de mine et
                private_block = target_node.private_chain.mine_pending_transactions(
                    target_node.wallet.address
                )
                
                if private_block:
                    self.blocks_mined_private += 1
                    private_length = len(target_node.private_chain.chain)
                    public_length = len(target_node.blockchain.chain)
                    advantage = private_length - public_length
                    
                    logger.info(f"🟠 Selfish node {target_node.id} mined private block #{private_block.index} "
                               f"(private: {private_length}, public: {public_length}, advantage: +{advantage})")
                    
                    # Avantaj threshold'u geçtiyse reveal et
                    if advantage >= self.reveal_threshold:
                        success = target_node.reveal_private_chain()
                        if success:
                            self.blocks_revealed += advantage
                            logger.warning(f"🔴 Selfish node {target_node.id} REVEALED private chain! "
                                          f"Public chain invalidated ({advantage} blocks)")
                            
                            # Diğer node'lara broadcast et (simüle edilmiş)
                            await self._broadcast_revealed_chain(target_node)
            
            # Mining sonrası bekleme (blok üretim süresi)
            await asyncio.sleep(self.simulator.blockchain_config['block_time'])
    
    async def _broadcast_revealed_chain(self, target_node):
        """
        Revealed chain'i diğer node'lara yayınla
        Diğer node'lar longest chain rule ile bu zinciri kabul eder
        
        Args:
            target_node: Selfish miner node
        """
        revealed_chain = target_node.blockchain
        
        # Tüm diğer node'lara yayınla
        for node in self.simulator.nodes:
            if node.id != target_node.id and not node.is_sybil:
                # Fork detection - chain listesini gönder
                fork_detected = node.blockchain.detect_fork(revealed_chain.chain)
                if fork_detected:
                    # Longest chain rule - revealed chain kabul edilir
                    node.blockchain.resolve_fork(revealed_chain.chain)
                    logger.info(f"Node {node.id} accepted revealed chain from selfish miner")
        
        # Yeni private chain başlat (current public chain'in kopyası)
        target_node.private_chain = Blockchain()
        target_node.private_chain.chain = [block for block in target_node.blockchain.chain]
        target_node.private_chain.pending_transactions = []
    
    async def _auto_recovery(self):
        """
        Otomatik iyileşme - Belirli süre sonra saldırı durur
        """
        await asyncio.sleep(self.attack_duration)
        
        if self.is_active:
            self.stop()
            logger.info(f"Selfish mining attack auto-recovery completed for node {self.target_node_id}")
    
    def stop(self) -> dict:
        """
        Selfish mining saldırısını durdur
        
        Returns:
            İyileşme durumu bilgisi
        """
        if not self.is_active:
            return {
                "success": False,
                "message": "No active selfish mining attack"
            }
        
        # Node'u bul
        target_node = self.simulator.get_node(self.target_node_id)
        if target_node:
            # Private chain'de kalan blokları reveal et (varsa)
            if target_node.private_chain:
                private_length = len(target_node.private_chain.chain)
                public_length = len(target_node.blockchain.chain)
                if private_length > public_length:
                    target_node.reveal_private_chain()
                    logger.info(f"Final reveal: Node {target_node.id} revealed remaining private blocks")
            
            # Selfish mining'i durdur
            target_node.stop_selfish_mining()
            target_node.status = "recovering"
            
            # Trust score düşür (ceza)
            target_node.trust_score = max(0, target_node.trust_score - 30)
            
            logger.info(f"Selfish miner {self.target_node_id} recovered. "
                       f"Mined: {self.blocks_mined_private}, Revealed: {self.blocks_revealed}")
            
            # Kısa süre sonra status'u healthy'ye çevir
            asyncio.create_task(self._restore_health(target_node))
        
        # Saldırı durumunu temizle
        self.is_active = False
        result = {
            "success": True,
            "message": f"Selfish mining stopped on node {self.target_node_id}",
            "target_node": self.target_node_id,
            "blocks_mined_private": self.blocks_mined_private,
            "blocks_revealed": self.blocks_revealed,
            "attack_duration": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
        
        self.target_node_id = None
        self.start_time = None
        
        return result
    
    async def _restore_health(self, node):
        """
        Node'un sağlığını geri yükle (5 saniye sonra)
        """
        await asyncio.sleep(5)
        if node.status == "recovering":
            node.status = "healthy"
            logger.info(f"Node {node.id} fully recovered from selfish mining")
    
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
                "remaining_time": 0,
                "blocks_mined_private": 0,
                "blocks_revealed": 0,
                "private_chain_length": 0,
                "public_chain_length": 0,
                "advantage": 0
            }
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        remaining = max(0, self.attack_duration - elapsed)
        
        # Node bilgilerini al
        target_node = self.simulator.get_node(self.target_node_id)
        private_length = 0
        public_length = 0
        advantage = 0
        
        if target_node and target_node.private_chain:
            private_length = len(target_node.private_chain.chain)
            public_length = len(target_node.blockchain.chain)
            advantage = private_length - public_length
        
        return {
            "active": True,
            "target_node": self.target_node_id,
            "elapsed_time": round(elapsed, 1),
            "remaining_time": round(remaining, 1),
            "attack_duration": self.attack_duration,
            "blocks_mined_private": self.blocks_mined_private,
            "blocks_revealed": self.blocks_revealed,
            "private_chain_length": private_length,
            "public_chain_length": public_length,
            "advantage": advantage,
            "reveal_threshold": self.reveal_threshold
        }
