"""
Message Broker Test - Pytest Format
"""
import pytest
import asyncio
from backend.network.message_broker import MessageBroker


class TestMessageBroker:
    """MessageBroker temel testleri"""
    
    def test_broker_creation(self):
        """Broker oluşturma"""
        broker = MessageBroker(min_delay=0.01, max_delay=0.05)
        assert broker is not None
        stats = broker.get_stats()
        assert stats['registered_nodes'] == 0
    
    def test_node_registration(self, message_broker):
        """Node kayıt testi"""
        node_ids = ['node1', 'node2', 'node3']
        for node_id in node_ids:
            message_broker.register_node(node_id)
        
        stats = message_broker.get_stats()
        assert stats['registered_nodes'] == 3
    
    def test_node_unregistration(self, message_broker):
        """Node kayıt silme testi"""
        message_broker.register_node('node1')
        message_broker.unregister_node('node1')
        
        stats = message_broker.get_stats()
        assert stats['registered_nodes'] == 0


@pytest.mark.asyncio
class TestMessageBrokerAsync:
    """MessageBroker async testleri"""
    
    async def test_send_message(self, message_broker):
        """Mesaj gönderme testi"""
        message_broker.register_node('node1')
        message_broker.register_node('node2')
        
        await message_broker.send_message(
            sender_id='node1',
            receiver_id='node2',
            message_type='test',
            content={'data': 'test_message'}
        )
        
        messages = message_broker.peek_messages_for_node('node2')
        assert len(messages) == 1
        assert messages[0].message_type == 'test'
    
    async def test_broadcast(self, message_broker):
        """Broadcast testi"""
        nodes = ['node1', 'node2', 'node3']
        for node_id in nodes:
            message_broker.register_node(node_id)
        
        await message_broker.broadcast(
            sender_id='node1',
            message_type='broadcast_test',
            content={'data': 'broadcast'},
            exclude_sender=True
        )
        
        # node1 hariç diğerleri mesaj almış olmalı
        assert message_broker.get_queue_size('node1') == 0
        assert message_broker.get_queue_size('node2') == 1
        assert message_broker.get_queue_size('node3') == 1
    
    async def test_get_messages(self, message_broker):
        """Mesaj alma testi"""
        message_broker.register_node('node1')
        message_broker.register_node('node2')
        
        await message_broker.send_message('node1', 'node2', 'test', {})
        
        messages = message_broker.get_messages_for_node('node2')
        assert len(messages) == 1
        
        # Kuyruk temizlenmeli
        assert message_broker.get_queue_size('node2') == 0
    
    async def test_message_type_filter(self, message_broker):
        """Tip filtreli mesaj alma testi"""
        message_broker.register_node('node1')
        
        await message_broker.send_message('node0', 'node1', 'type_a', {})
        await message_broker.send_message('node0', 'node1', 'type_b', {})
        await message_broker.send_message('node0', 'node1', 'type_a', {})
        
        # Sadece type_a'ları al
        type_a_messages = message_broker.get_messages_for_node('node1', message_type='type_a')
        assert len(type_a_messages) == 2
        
        # type_b hala kuyrukta olmalı
        assert message_broker.get_queue_size('node1') == 1


class TestMessageBrokerPartition:
    """Partition özellikleri testi"""
    
    def test_set_partition(self, message_broker):
        """Partition set testi"""
        nodes_a = ['node1', 'node2']
        nodes_b = ['node3', 'node4']
        
        for node_id in nodes_a + nodes_b:
            message_broker.register_node(node_id)
        
        message_broker.set_partition(nodes_a, nodes_b)
        
        status = message_broker.get_partition_status()
        assert status['active'] is True
        assert len(status['group_a']) == 2
        assert len(status['group_b']) == 2
    
    def test_clear_partition(self, message_broker):
        """Partition clear testi"""
        message_broker.set_partition(['node1'], ['node2'])
        message_broker.clear_partition()
        
        status = message_broker.get_partition_status()
        assert status['active'] is False
