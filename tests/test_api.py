"""
API Tests - Pytest Format
Not: Bu testler çalışan bir API sunucusu gerektirir
Sunucuyu başlatın: python backend/main.py
"""
import pytest
import requests
import time


@pytest.mark.api
class TestAPIBasic:
    """Temel API endpoint testleri"""
    
    def test_health_check(self, api_base_url):
        """Health check endpoint"""
        try:
            response = requests.get(f"{api_base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert 'message' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_status_endpoint(self, api_base_url):
        """Status endpoint"""
        try:
            response = requests.get(f"{api_base_url}/status")
            assert response.status_code == 200
            data = response.json()
            assert 'total_nodes' in data
            assert 'is_running' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_nodes_endpoint(self, api_base_url):
        """Nodes endpoint"""
        try:
            response = requests.get(f"{api_base_url}/nodes")
            assert response.status_code == 200
            data = response.json()
            assert 'nodes' in data
            assert 'total_nodes' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


@pytest.mark.api
class TestAPIControl:
    """API kontrol endpoint testleri"""
    
    def test_start_stop(self, api_base_url):
        """Start/Stop simulator"""
        try:
            # Start
            response = requests.post(f"{api_base_url}/start")
            assert response.status_code == 200
            data = response.json()
            assert data['is_running'] is True
            
            time.sleep(1)
            
            # Stop
            response = requests.post(f"{api_base_url}/stop")
            assert response.status_code == 200
            data = response.json()
            assert data['is_running'] is False
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_reset(self, api_base_url):
        """Reset simulator"""
        try:
            response = requests.post(f"{api_base_url}/reset")
            assert response.status_code == 200
            data = response.json()
            assert 'message' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


@pytest.mark.api
class TestAPIPBFT:
    """PBFT API endpoint testleri"""
    
    def test_network_nodes(self, api_base_url):
        """Network nodes endpoint"""
        try:
            response = requests.get(f"{api_base_url}/network/nodes")
            assert response.status_code == 200
            data = response.json()
            assert 'total_nodes' in data
            assert 'nodes' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_network_messages(self, api_base_url):
        """Network messages endpoint"""
        try:
            response = requests.get(f"{api_base_url}/network/messages")
            assert response.status_code == 200
            data = response.json()
            assert 'total_messages' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_pbft_status(self, api_base_url):
        """PBFT status endpoint"""
        try:
            response = requests.get(f"{api_base_url}/pbft/status")
            assert response.status_code == 200
            data = response.json()
            assert 'enabled' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


@pytest.mark.api
class TestAPIAttacks:
    """Attack API endpoint testleri"""
    
    def test_attack_trigger(self, api_base_url):
        """Attack trigger endpoint"""
        try:
            # İlk önce nodes al
            response = requests.get(f"{api_base_url}/nodes")
            nodes = response.json()['nodes']
            if not nodes:
                pytest.skip("No nodes available")
            
            target_node = nodes[0]['id']
            
            # Attack tetikle
            attack_data = {
                "attack_type": "ddos",
                "target_node_id": target_node,
                "parameters": {"intensity": "low"}
            }
            response = requests.post(f"{api_base_url}/attack/trigger", json=attack_data)
            assert response.status_code == 200
            data = response.json()
            assert 'attack_id' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_attack_status(self, api_base_url):
        """Attack status endpoint"""
        try:
            response = requests.get(f"{api_base_url}/attack/status")
            assert response.status_code == 200
            data = response.json()
            assert 'statistics' in data
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
