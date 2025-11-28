"""
API Test Script
API endpoint'lerini test eder
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Health check testi"""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200


def test_status():
    """Status endpoint testi"""
    print("\n" + "=" * 60)
    print("TEST: Get Status")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response:")
    print(f"  Total Nodes: {data['total_nodes']}")
    print(f"  Active Nodes: {data['active_nodes']}")
    print(f"  Validators: {data['validator_nodes']}")
    print(f"  Running: {data['is_running']}")
    assert response.status_code == 200


def test_nodes():
    """Nodes endpoint testi"""
    print("\n" + "=" * 60)
    print("TEST: Get Nodes")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/nodes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total Nodes: {data['total_nodes']}")
    print(f"First 3 nodes:")
    for node in data['nodes'][:3]:
        print(f"  - {node['id']} ({node['role']}) - {node['status']}")
    assert response.status_code == 200


def test_blockchain():
    """Blockchain endpoint testi"""
    print("\n" + "=" * 60)
    print("TEST: Get Blockchain")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/blockchain")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Chain Length: {data['chain_length']}")
    print(f"Difficulty: {data['chain']['difficulty']}")
    assert response.status_code == 200


def test_start_stop():
    """Start/Stop testi"""
    print("\n" + "=" * 60)
    print("TEST: Start/Stop Simulator")
    print("=" * 60)
    
    # Start
    response = requests.post(f"{BASE_URL}/start")
    print(f"Start Status: {response.status_code}")
    data = response.json()
    print(f"  Running: {data['is_running']}")
    assert data['is_running'] == True
    
    time.sleep(1)
    
    # Stop
    response = requests.post(f"{BASE_URL}/stop")
    print(f"Stop Status: {response.status_code}")
    data = response.json()
    print(f"  Running: {data['is_running']}")
    assert data['is_running'] == False


def test_reset():
    """Reset testi"""
    print("\n" + "=" * 60)
    print("TEST: Reset Simulator")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/reset")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Message: {data['message']}")
    print(f"Total Nodes: {data['total_nodes']}")
    assert response.status_code == 200


def main():
    print("\n" + "*" * 60)
    print("API ENDPOINTS TEST")
    print("*" * 60)
    print("\nMake sure API server is running:")
    print("  python backend/main.py")
    print("\n" + "*" * 60)
    
    try:
        test_health_check()
        test_status()
        test_nodes()
        test_blockchain()
        test_start_stop()
        test_reset()
        
        print("\n" + "=" * 60)
        print("✅ ALL API TESTS PASSED!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Please start the server first:")
        print("  python backend/main.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")


if __name__ == "__main__":
    main()
