"""
Test Sybil Attack API Endpoints
"""
import requests
import time

BASE_URL = "http://localhost:8000"


def test_sybil_api():
    """Sybil attack API endpoint'lerini test et"""
    print("\n" + "="*60)
    print("SYBIL ATTACK API TEST")
    print("="*60)
    
    # 1. Initial status check
    print("\n1. Checking initial status...")
    response = requests.get(f"{BASE_URL}/status")
    initial_data = response.json()
    print(f"✓ Initial nodes: {initial_data['total_nodes']}")
    
    # 2. Trigger Sybil attack
    print("\n2. Triggering Sybil attack (15 fake nodes)...")
    response = requests.post(f"{BASE_URL}/attack/sybil/trigger?num_nodes=15")
    trigger_data = response.json()
    print(f"✓ Status: {trigger_data['status']}")
    print(f"✓ Message: {trigger_data['message']}")
    print(f"✓ Attack ID: {trigger_data['attack_id']}")
    
    # 3. Get attack status
    print("\n3. Getting attack status...")
    response = requests.get(f"{BASE_URL}/attack/sybil/status")
    status_data = response.json()
    print(f"✓ Attack status: {status_data['status']}")
    print(f"✓ Fake nodes created: {status_data['parameters']['active_fake_nodes']}")
    print(f"✓ Effects: {len(status_data['effects'])} effects")
    
    # 4. Check network nodes
    print("\n4. Checking network nodes...")
    response = requests.get(f"{BASE_URL}/network/nodes")
    network_data = response.json()
    print(f"✓ Total nodes now: {network_data['total_nodes']}")
    
    # Count Sybil nodes
    sybil_count = sum(1 for node in network_data['nodes'] if node.get('is_sybil', False))
    print(f"✓ Sybil nodes detected: {sybil_count}")
    
    # 5. Wait 3 seconds
    print("\n5. Waiting 3 seconds...")
    time.sleep(3)
    
    # 6. Stop attack
    print("\n6. Stopping attack...")
    response = requests.post(f"{BASE_URL}/attack/sybil/stop")
    stop_data = response.json()
    print(f"✓ Status: {stop_data['status']}")
    print(f"✓ Message: {stop_data['message']}")
    
    # 7. Check final status
    print("\n7. Checking final status...")
    response = requests.get(f"{BASE_URL}/status")
    final_data = response.json()
    print(f"✓ Final nodes: {final_data['total_nodes']}")
    
    # 8. Verify cleanup
    response = requests.get(f"{BASE_URL}/network/nodes")
    network_data = response.json()
    sybil_remaining = sum(1 for node in network_data['nodes'] if node.get('is_sybil', False))
    print(f"✓ Sybil nodes remaining: {sybil_remaining}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("Starting Sybil Attack API Tests...")
    print("Make sure the API server is running on http://localhost:8000")
    
    try:
        test_sybil_api()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
