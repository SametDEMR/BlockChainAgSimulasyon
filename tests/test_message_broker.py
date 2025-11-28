"""
Message Broker Test
"""

import asyncio
import sys
import os

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.network.message_broker import MessageBroker


async def test_message_broker():
    """Message Broker testleri"""
    
    print("=" * 60)
    print("MESSAGE BROKER TEST")
    print("=" * 60)
    
    # 1. MessageBroker oluştur
    print("\n1. MessageBroker oluşturuluyor...")
    broker = MessageBroker(min_delay=0.01, max_delay=0.05)  # Hızlı test için kısa delay
    print("✓ MessageBroker oluşturuldu")
    
    # 2. Node'ları kaydet
    print("\n2. Node'lar kaydediliyor...")
    node_ids = ['node1', 'node2', 'node3', 'node4']
    for node_id in node_ids:
        broker.register_node(node_id)
        print(f"✓ {node_id} kaydedildi")
    
    stats = broker.get_stats()
    print(f"\nKayıtlı node sayısı: {stats['registered_nodes']}")
    
    # 3. Tek bir node'a mesaj gönder
    print("\n3. node1'den node2'ye mesaj gönderiliyor...")
    await broker.send_message(
        sender_id='node1',
        receiver_id='node2',
        message_type='test_message',
        content={'data': 'Hello node2!'}
    )
    print("✓ Mesaj gönderildi (network delay ile)")
    
    # Mesajı kontrol et
    messages = broker.peek_messages_for_node('node2')
    print(f"node2'nin kuyruğunda {len(messages)} mesaj var")
    if messages:
        msg = messages[0]
        print(f"  - Gönderen: {msg.sender_id}")
        print(f"  - Tip: {msg.message_type}")
        print(f"  - İçerik: {msg.content}")
    
    # 4. Broadcast mesajı
    print("\n4. node1'den tüm node'lara broadcast...")
    await broker.broadcast(
        sender_id='node1',
        message_type='broadcast_test',
        content={'data': 'Hello everyone!'},
        exclude_sender=True
    )
    print("✓ Broadcast tamamlandı")
    
    # Her node'un kuyruğunu kontrol et
    print("\nHer node'un kuyruk durumu:")
    for node_id in node_ids:
        queue_size = broker.get_queue_size(node_id)
        print(f"  {node_id}: {queue_size} mesaj")
    
    # 5. Mesajları al
    print("\n5. node2 mesajlarını alıyor...")
    messages = broker.get_messages_for_node('node2')
    print(f"✓ {len(messages)} mesaj alındı")
    for i, msg in enumerate(messages):
        print(f"  Mesaj {i+1}: {msg.message_type} - {msg.content['data']}")
    
    # Kuyruk temizlendi mi?
    queue_size = broker.get_queue_size('node2')
    print(f"node2'nin kuyruğu temizlendi: {queue_size} mesaj kaldı")
    
    # 6. Tip filtrelemesi
    print("\n6. Tip filtreli mesaj alma...")
    # Önce farklı tipte mesajlar gönder
    await broker.send_message('node1', 'node3', 'type_a', {'msg': 'A1'})
    await broker.send_message('node1', 'node3', 'type_b', {'msg': 'B1'})
    await broker.send_message('node1', 'node3', 'type_a', {'msg': 'A2'})
    
    print("node3'e 3 mesaj gönderildi (2 type_a, 1 type_b)")
    
    # Sadece type_a'ları al
    type_a_messages = broker.get_messages_for_node('node3', message_type='type_a')
    print(f"✓ type_a mesajları alındı: {len(type_a_messages)} adet")
    
    # type_b hala kuyrukta mı?
    remaining = broker.get_queue_size('node3')
    print(f"node3'te kalan mesaj: {remaining} adet")
    
    # 7. İstatistikler
    print("\n7. Son İstatistikler:")
    stats = broker.get_stats()
    print(f"  Toplam gönderilen mesaj: {stats['total_messages_sent']}")
    print(f"  Toplam broadcast: {stats['total_broadcasts']}")
    print(f"  Kayıtlı node: {stats['registered_nodes']}")
    print(f"  Bekleyen mesaj: {stats['total_pending_messages']}")
    
    # 8. Tüm mesajları görüntüle
    print("\n8. Tüm bekleyen mesajlar:")
    all_messages = broker.get_all_messages()
    for msg in all_messages:
        print(f"  [{msg['in_queue_of']}] {msg['message_type']} from {msg['sender_id']}")
    
    # 9. Temizlik
    print("\n9. Tüm kuyruklar temizleniyor...")
    broker.clear_all_queues()
    stats = broker.get_stats()
    print(f"✓ Temizlendi. Bekleyen mesaj: {stats['total_pending_messages']}")
    
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)


async def test_network_delay():
    """Network delay simülasyonu testi"""
    
    print("\n" + "=" * 60)
    print("NETWORK DELAY TEST")
    print("=" * 60)
    
    broker = MessageBroker(min_delay=0.1, max_delay=0.3)
    
    # Node'ları kaydet
    for i in range(5):
        broker.register_node(f'node{i}')
    
    print("\n5 node'a broadcast gönderiliyor...")
    print("Network delay: 0.1-0.3 saniye")
    
    import time
    start = time.time()
    
    await broker.broadcast(
        sender_id='node0',
        message_type='test',
        content={'data': 'test'},
        exclude_sender=True
    )
    
    end = time.time()
    elapsed = end - start
    
    print(f"✓ Broadcast tamamlandı")
    print(f"Geçen süre: {elapsed:.3f} saniye")
    print(f"(Beklenen: ~0.1-0.3 saniye - paralel gönderim sayesinde)")
    
    # Her node'a mesaj ulaştı mı?
    print("\nMesaj dağılımı:")
    for i in range(5):
        node_id = f'node{i}'
        count = broker.get_queue_size(node_id)
        print(f"  {node_id}: {count} mesaj")


if __name__ == "__main__":
    # Ana test
    asyncio.run(test_message_broker())
    
    # Network delay testi
    asyncio.run(test_network_delay())
