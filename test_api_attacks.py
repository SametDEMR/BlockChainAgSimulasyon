"""
API Attack Endpoints Test
Test edilecek manuel olarak çünkü FastAPI server gerekiyor
"""

# Test için kullan:
# 1. API'yi başlat: python backend/main_old_1.py
# 2. Başka terminal'de requests ile test et

import requests
import time

API_BASE = "http://localhost:8000"

print("=" * 60)
print("API ATTACK ENDPOINTS TEST")
print("=" * 60)
print("\nÖnce API'yi başlatın: python backend/main_old_1.py")
print("Sonra bu testi çalıştırın.\n")

try:
    # 1. Health check
    print("1. Health Check")
    r = requests.get(f"{API_BASE}/")
    print(f"   Status: {r.json()}")
    
    # 2. Simulator başlat
    print("\n2. Start Simulator")
    r = requests.post(f"{API_BASE}/start")
    print(f"   {r.json()}")
    
    time.sleep(2)
    
    # 3. Node listesi al
    print("\n3. Get Nodes")
    r = requests.get(f"{API_BASE}/nodes")
    nodes = r.json()['nodes']
    print(f"   Total Nodes: {len(nodes)}")
    target_node = nodes[5]['id']
    print(f"   Target Node: {target_node}")
    
    # 4. İlk metrikler
    print("\n4. Initial Metrics")
    r = requests.get(f"{API_BASE}/metrics/{target_node}")
    metrics = r.json()['metrics']
    print(f"   Response Time: {metrics['response_time']}ms")
    print(f"   CPU Usage: {metrics['cpu_usage']}%")
    print(f"   Status: {r.json()['status']}")
    
    # 5. DDoS saldırısı tetikle
    print("\n5. Trigger DDoS Attack")
    attack_data = {
        "attack_type": "ddos",
        "target_node_id": target_node,
        "parameters": {"intensity": "high"}
    }
    r = requests.post(f"{API_BASE}/attack/trigger", json=attack_data)
    attack_response = r.json()
    print(f"   Attack ID: {attack_response['attack_id']}")
    print(f"   Message: {attack_response['message']}")
    
    # 6. Saldırı sonrası metrikler
    time.sleep(1)
    print("\n6. Metrics During Attack")
    r = requests.get(f"{API_BASE}/metrics/{target_node}")
    metrics = r.json()['metrics']
    print(f"   Response Time: {metrics['response_time']}ms (should be high)")
    print(f"   CPU Usage: {metrics['cpu_usage']}%")
    print(f"   Status: {r.json()['status']}")
    
    # 7. Saldırı durumu
    print("\n7. Attack Status")
    r = requests.get(f"{API_BASE}/attack/status")
    status = r.json()
    print(f"   Active Attacks: {len(status['active_attacks'])}")
    print(f"   Statistics: {status['statistics']}")
    
    # 8. Tüm node metrikleri
    print("\n8. All Node Metrics")
    r = requests.get(f"{API_BASE}/metrics")
    all_metrics = r.json()
    for m in all_metrics['metrics'][:3]:
        print(f"   {m['node_id']}: Status={m['status']}, RT={m['metrics']['response_time']}ms")
    
    print("\n" + "=" * 60)
    print("✅ TEST TAMAMLANDI")
    print("=" * 60)
    print("\nSaldırı otomatik iyileşecek (20s + 5s recovery)")
    
except requests.exceptions.ConnectionError:
    print("\n❌ HATA: API'ye bağlanılamıyor!")
    print("Önce API'yi başlatın: python backend/main_old_1.py")
except Exception as e:
    print(f"\n❌ HATA: {e}")
