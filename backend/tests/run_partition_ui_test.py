"""
Test Network Partition UI Integration (7.3)
API endpoint'leri ve UI integration testi
"""
import asyncio
import sys
import os
import requests
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = "http://localhost:8000"


def test_partition_api():
    """Network Partition API endpoint'lerini test et"""
    print("\n" + "=" * 60)
    print("TEST: Network Partition API Integration")
    print("=" * 60)
    
    try:
        # Test 1: API health
        print("\n[Test 1] API health check...")
        response = requests.get(f"{API_BASE}/")
        assert response.status_code == 200
        print("✓ API online")
        
        # Test 2: Simulator status
        print("\n[Test 2] Simulator status...")
        response = requests.get(f"{API_BASE}/status")
        status = response.json()
        total_nodes = status['total_nodes']
        print(f"✓ Total nodes: {total_nodes}")
        
        # Test 3: Trigger partition
        print("\n[Test 3] Trigger partition attack...")
        response = requests.post(f"{API_BASE}/attack/partition/trigger")
        assert response.status_code == 200
        result = response.json()
        attack_id = result['attack_id']
        print(f"✓ Attack ID: {attack_id}")
        
        time.sleep(1)
        
        # Test 4: Partition status
        print("\n[Test 4] Partition status...")
        response = requests.get(f"{API_BASE}/attack/partition/status")
        assert response.status_code == 200
        status = response.json()
        
        print(f"  Active: {status['active']}")
        print(f"  Group A: {status['group_a_size']} nodes")
        print(f"  Group B: {status['group_b_size']} nodes")
        
        assert status['active'] == True
        assert status['group_a_size'] > 0
        assert status['group_b_size'] > 0
        print("✓ Partition active")
        
        # Test 5: MessageBroker partition
        print("\n[Test 5] MessageBroker partition...")
        broker = status.get('message_broker_partition', {})
        print(f"  Broker active: {broker.get('active', False)}")
        print(f"  Blocked messages: {broker.get('blocked_messages', 0)}")
        assert broker.get('active', False) == True
        print("✓ MessageBroker partition active")
        
        # Test 6: Group node lists
        print("\n[Test 6] Node groups...")
        group_a_ids = status.get('group_a_ids', [])
        group_b_ids = status.get('group_b_ids', [])
        
        print(f"  Group A IDs: {len(group_a_ids)}")
        print(f"  Group B IDs: {len(group_b_ids)}")
        
        assert len(group_a_ids) > 0
        assert len(group_b_ids) > 0
        print("✓ Node groups formed")
        
        # Test 7: Stop partition
        print("\n[Test 7] Stop partition...")
        response = requests.post(f"{API_BASE}/attack/partition/stop")
        assert response.status_code == 200
        print("✓ Stop command sent")
        
        time.sleep(2)
        
        # Test 8: Verify cleanup
        print("\n[Test 8] Verify cleanup...")
        response = requests.get(f"{API_BASE}/attack/partition/status")
        final_status = response.json()
        
        print(f"  Partition active: {final_status['active']}")
        assert final_status['active'] == False
        print("✓ Partition deactivated")
        
        # Test 9: MessageBroker cleanup
        final_broker = final_status.get('message_broker_partition', {})
        print(f"  Broker active: {final_broker.get('active', False)}")
        assert final_broker.get('active', False) == False
        print("✓ MessageBroker cleanup done")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        raise
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to API at {API_BASE}")
        print("   Make sure backend is running: python backend/main.py")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Ana fonksiyon"""
    print("\n🚀 Network Partition UI Integration Test")
    print("   Prerequisite: Backend must be running!")
    
    try:
        test_partition_api()
        print("\n✅ Test completed successfully!")
        print("\nUI Test Steps:")
        print("1. Start frontend-streamlit: streamlit run frontend-streamlit/main.py")
        print("2. Go to Attack Panel")
        print("3. Select 'Network Partition' attack type")
        print("4. Click 'Trigger Attack'")
        print("5. Verify partition status appears")
        print("6. Check Network Map for partition visualization")
        print("7. Click 'Stop Partition' button")
        sys.exit(0)
    except Exception:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
