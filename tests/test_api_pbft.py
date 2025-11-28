"""
API PBFT Endpoints Test
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def test_api_pbft_endpoints():
    """PBFT endpoint'leri test et"""
    
    print("=" * 60)
    print("API PBFT ENDPOINTS TEST")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Health Check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Status: {response.status_code}")
    print(f"  {response.json()['message']}")
    
    # 2. Status
    print("\n2. Simulator Status...")
    response = requests.get(f"{BASE_URL}/status")
    data = response.json()
    print(f"✓ Running: {data['is_running']}")
    print(f"  Total nodes: {data['total_nodes']}")
    print(f"  Validators: {data['validator_nodes']}")
    if 'pbft' in data:
        print(f"  PBFT Primary: {data['pbft'].get('primary_validator', 'N/A')}")
    
    # 3. Network nodes (YENİ)
    print("\n3. Network Nodes...")
    response = requests.get(f"{BASE_URL}/network/nodes")
    data = response.json()
    print(f"✓ Total: {data['total_nodes']}")
    print(f"  Validators: {data['validator_count']}")
    
    # İlk birkaç validator göster
    for node in data['nodes'][:3]:
        print(f"\n  {node['id']}:")
        print(f"    Role: {node['role']}")
        print(f"    Queue size: {node.get('message_queue_size', 0)}")
        if 'pbft' in node:
            print(f"    PBFT primary: {node['pbft']['is_primary']}")
    
    # 4. Network messages (YENİ)
    print("\n4. Network Messages...")
    response = requests.get(f"{BASE_URL}/network/messages")
    data = response.json()
    print(f"✓ Total messages: {data['total_messages']}")
    print(f"  PBFT messages: {data['pbft_messages']}")
    print(f"  Message types: {data['message_types']}")
    
    # 5. PBFT status (YENİ)
    print("\n5. PBFT Status...")
    response = requests.get(f"{BASE_URL}/pbft/status")
    data = response.json()
    print(f"✓ Enabled: {data['enabled']}")
    if data['enabled']:
        print(f"  Primary: {data['primary']}")
        print(f"  View: {data['current_view']}")
        print(f"  Consensus reached: {data['total_consensus_reached']}")
        print(f"  Validators: {data['total_validators']}")
    
    # 6. Start simulator
    print("\n6. Starting Simulator...")
    response = requests.post(f"{BASE_URL}/start")
    data = response.json()
    print(f"✓ {data['message']}")
    print(f"  Background tasks: {data.get('background_tasks', 0)}")
    
    # 7. Wait and check messages
    print("\n7. Waiting 3 seconds for PBFT activity...")
    time.sleep(3)
    
    response = requests.get(f"{BASE_URL}/network/messages")
    data = response.json()
    print(f"✓ PBFT messages after 3s: {data['pbft_messages']}")
    print(f"  Message types: {data['message_types']}")
    
    # 8. PBFT status after running
    print("\n8. PBFT Status after running...")
    response = requests.get(f"{BASE_URL}/pbft/status")
    data = response.json()
    print(f"✓ Consensus reached: {data['total_consensus_reached']}")
    
    # 9. Stop
    print("\n9. Stopping Simulator...")
    response = requests.post(f"{BASE_URL}/stop")
    print(f"✓ {response.json()['message']}")
    
    print("\n" + "=" * 60)
    print("TEST TAMAMLANDI!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_api_pbft_endpoints()
    except requests.exceptions.ConnectionError:
        print("⚠️  API sunucusu çalışmıyor!")
        print("Önce 'python backend/main_old.py' ile sunucuyu başlat")
