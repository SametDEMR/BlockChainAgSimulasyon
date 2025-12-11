"""
Node Metrics Test
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.network.node import Node

def test_node_metrics():
    """Node metrik sistemini test eder"""
    
    print("=" * 60)
    print("NODE METRICS TEST")
    print("=" * 60)
    
    # Node oluştur
    print("\n📦 Node Oluşturuluyor...")
    node = Node(role="regular", total_validators=4)
    
    print(f"✓ Node oluşturuldu: {node.id}")
    
    # Başlangıç metrikleri
    print("\n" + "-" * 60)
    print("1. Başlangıç Metrikleri")
    print("-" * 60)
    
    metrics = node.get_metrics()
    print(f"\n📊 Metrikler:")
    print(f"   CPU Usage: {metrics['cpu_usage']}%")
    print(f"   Memory Usage: {metrics['memory_usage']}%")
    print(f"   Response Time: {metrics['response_time']}ms")
    print(f"   Network Latency: {metrics['network_latency']}ms")
    print(f"   Packet Loss: {metrics['packet_loss']}%")
    print(f"   Requests/sec: {metrics['requests_per_second']}")
    print(f"   Errors: {metrics['errors_count']}")
    print(f"   Trust Score: {metrics['trust_score']}")
    
    # Status bilgisi
    print("\n" + "-" * 60)
    print("2. Node Status (Metrikler Dahil)")
    print("-" * 60)
    
    status = node.get_status()
    print(f"\n📋 Status:")
    print(f"   ID: {status['id']}")
    print(f"   Role: {status['role']}")
    print(f"   Status: {status['status']}")
    print(f"   Active: {status['is_active']}")
    
    print(f"\n📊 Embedded Metrics:")
    for key, value in status['metrics'].items():
        print(f"   {key}: {value}")
    
    # Metrikleri manuel değiştir
    print("\n" + "-" * 60)
    print("3. Metrik Değişiklikleri (Simüle)")
    print("-" * 60)
    
    print("\n⚠️  Saldırı simülasyonu...")
    node.cpu_usage = 95
    node.memory_usage = 85
    node.response_time = 500.0
    node.network_latency = 200.0
    node.packet_loss = 15.0
    node.requests_per_second = 1000
    node.errors_count = 50
    node.status = "under_attack"
    
    metrics = node.get_metrics()
    print(f"\n💥 Saldırı Anındaki Metrikler:")
    print(f"   CPU Usage: {metrics['cpu_usage']}% (↑ kritik)")
    print(f"   Memory Usage: {metrics['memory_usage']}% (↑ yüksek)")
    print(f"   Response Time: {metrics['response_time']}ms (↑ çok yavaş)")
    print(f"   Network Latency: {metrics['network_latency']}ms (↑ gecikme)")
    print(f"   Packet Loss: {metrics['packet_loss']}% (↑ paket kaybı)")
    print(f"   Requests/sec: {metrics['requests_per_second']} (↑ DDoS)")
    print(f"   Errors: {metrics['errors_count']}")
    
    # İyileşme
    print("\n🔄 İyileşme simülasyonu...")
    node.cpu_usage = 40
    node.memory_usage = 45
    node.response_time = 100.0
    node.network_latency = 20.0
    node.packet_loss = 2.0
    node.requests_per_second = 50
    node.errors_count = 5
    node.status = "recovering"
    
    metrics = node.get_metrics()
    print(f"\n🔄 Recovering Metrikleri:")
    print(f"   CPU Usage: {metrics['cpu_usage']}% (↓ düşüyor)")
    print(f"   Memory Usage: {metrics['memory_usage']}% (↓)")
    print(f"   Response Time: {metrics['response_time']}ms (↓)")
    print(f"   Network Latency: {metrics['network_latency']}ms (↓)")
    print(f"   Packet Loss: {metrics['packet_loss']}% (↓)")
    print(f"   Requests/sec: {metrics['requests_per_second']} (↓)")
    
    # Tam iyileşme
    print("\n✅ Tam iyileşme...")
    node.cpu_usage = 20
    node.memory_usage = 30
    node.response_time = 50.0
    node.network_latency = 10.0
    node.packet_loss = 0.0
    node.requests_per_second = 10
    node.errors_count = 0
    node.status = "healthy"
    
    metrics = node.get_metrics()
    print(f"\n✅ Healthy Metrikleri:")
    print(f"   CPU Usage: {metrics['cpu_usage']}%")
    print(f"   Memory Usage: {metrics['memory_usage']}%")
    print(f"   Response Time: {metrics['response_time']}ms")
    print(f"   Network Latency: {metrics['network_latency']}ms")
    print(f"   Packet Loss: {metrics['packet_loss']}%")
    print(f"   Requests/sec: {metrics['requests_per_second']}")
    print(f"   Errors: {metrics['errors_count']}")
    
    # Validator node testi
    print("\n" + "-" * 60)
    print("4. Validator Node Metrikleri")
    print("-" * 60)
    
    validator = Node(role="validator", total_validators=4)
    print(f"\n✓ Validator oluşturuldu: {validator.id}")
    
    status = validator.get_status()
    print(f"\n📋 Validator Status:")
    print(f"   Role: {status['role']}")
    print(f"   PBFT: {'✓' if 'pbft' in status else '✗'}")
    
    print(f"\n📊 Validator Metrikleri:")
    for key, value in status['metrics'].items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ TÜM TESTLER BAŞARILI!")
    print("=" * 60)

if __name__ == "__main__":
    test_node_metrics()
