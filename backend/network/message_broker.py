"""
Message Broker - Node'lar arası mesajlaşma sistemi
Network delay simülasyonu ile birlikte
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class Message:
    """Network mesajı"""
    sender_id: str
    receiver_id: str  # "broadcast" için özel değer
    message_type: str  # "pre_prepare", "prepare", "commit", "new_block" vb.
    content: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Mesajı dict'e çevir"""
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


class MessageBroker:
    """
    Merkezi mesaj broker'ı
    - Node'lar arası mesaj iletimi
    - Network delay simülasyonu
    - Broadcast desteği
    - Mesaj kuyruğu yönetimi
    """
    
    def __init__(self, min_delay: float = 0.1, max_delay: float = 0.5):
        """
        Args:
            min_delay: Minimum network gecikmesi (saniye)
            max_delay: Maximum network gecikmesi (saniye)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        # Her node için mesaj kuyruğu
        self.message_queues: Dict[str, List[Message]] = {}
        
        # İstatistikler
        self.total_messages_sent = 0
        self.total_broadcasts = 0
        
    def register_node(self, node_id: str):
        """Yeni node kaydı"""
        if node_id not in self.message_queues:
            self.message_queues[node_id] = []
    
    def unregister_node(self, node_id: str):
        """Node kaydını kaldır"""
        if node_id in self.message_queues:
            del self.message_queues[node_id]
    
    async def send_message(self, sender_id: str, receiver_id: str, 
                          message_type: str, content: Dict):
        """
        Tek bir node'a mesaj gönder (network delay ile)
        
        Args:
            sender_id: Gönderen node ID
            receiver_id: Alıcı node ID
            message_type: Mesaj tipi
            content: Mesaj içeriği
        """
        # Network delay simülasyonu
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)
        
        # Mesaj oluştur
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content
        )
        
        # Alıcı node'un kuyruğuna ekle
        if receiver_id in self.message_queues:
            self.message_queues[receiver_id].append(message)
            self.total_messages_sent += 1
    
    async def broadcast(self, sender_id: str, message_type: str, 
                       content: Dict, exclude_sender: bool = True):
        """
        Tüm node'lara mesaj gönder
        
        Args:
            sender_id: Gönderen node ID
            message_type: Mesaj tipi
            content: Mesaj içeriği
            exclude_sender: Gönderen node hariç tutulsun mu?
        """
        self.total_broadcasts += 1
        
        # Tüm node'lara ayrı ayrı gönder (gerçekçi network simülasyonu)
        tasks = []
        for node_id in self.message_queues.keys():
            if exclude_sender and node_id == sender_id:
                continue
            
            task = self.send_message(
                sender_id=sender_id,
                receiver_id=node_id,
                message_type=message_type,
                content=content
            )
            tasks.append(task)
        
        # Paralel olarak tüm mesajları gönder
        await asyncio.gather(*tasks)
    
    def get_messages_for_node(self, node_id: str, 
                             message_type: Optional[str] = None) -> List[Message]:
        """
        Bir node için bekleyen mesajları al ve kuyruğu temizle
        
        Args:
            node_id: Node ID
            message_type: Sadece belirli tip mesajlar (None ise tümü)
        
        Returns:
            Mesaj listesi
        """
        if node_id not in self.message_queues:
            return []
        
        messages = self.message_queues[node_id]
        
        # Tip filtresi varsa uygula
        if message_type:
            filtered = [m for m in messages if m.message_type == message_type]
            # Alınan mesajları kuyruktan kaldır
            self.message_queues[node_id] = [
                m for m in messages if m.message_type != message_type
            ]
            return filtered
        else:
            # Tüm mesajları al ve kuyruğu temizle
            self.message_queues[node_id] = []
            return messages
    
    def peek_messages_for_node(self, node_id: str, 
                              message_type: Optional[str] = None) -> List[Message]:
        """
        Bir node için bekleyen mesajları görüntüle (kuyruğu temizlemeden)
        
        Args:
            node_id: Node ID
            message_type: Sadece belirli tip mesajlar
        
        Returns:
            Mesaj listesi
        """
        if node_id not in self.message_queues:
            return []
        
        messages = self.message_queues[node_id]
        
        if message_type:
            return [m for m in messages if m.message_type == message_type]
        else:
            return messages
    
    def get_queue_size(self, node_id: str) -> int:
        """Bir node'un mesaj kuyruğu boyutu"""
        if node_id not in self.message_queues:
            return 0
        return len(self.message_queues[node_id])
    
    def clear_queue(self, node_id: str):
        """Bir node'un mesaj kuyruğunu temizle"""
        if node_id in self.message_queues:
            self.message_queues[node_id] = []
    
    def clear_all_queues(self):
        """Tüm mesaj kuyruklarını temizle"""
        for node_id in self.message_queues:
            self.message_queues[node_id] = []
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndür"""
        return {
            'total_messages_sent': self.total_messages_sent,
            'total_broadcasts': self.total_broadcasts,
            'registered_nodes': len(self.message_queues),
            'total_pending_messages': sum(
                len(queue) for queue in self.message_queues.values()
            )
        }
    
    def get_all_messages(self) -> List[Dict]:
        """Tüm bekleyen mesajları döndür (debug için)"""
        all_messages = []
        for node_id, messages in self.message_queues.items():
            for msg in messages:
                msg_dict = msg.to_dict()
                msg_dict['in_queue_of'] = node_id
                all_messages.append(msg_dict)
        return all_messages
