"""Tests for API Client."""
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api_client import APIClient


@pytest.fixture
def api_client():
    """Create API client instance."""
    return APIClient("http://localhost:8000")


class TestAPIClient:
    """Test APIClient class."""
    
    def test_init(self, api_client):
        """Test initialization."""
        assert api_client.base_url == "http://localhost:8000"
        assert api_client.timeout == 5
        assert api_client._max_retries == 3
    
    def test_init_strips_trailing_slash(self):
        """Test base_url trailing slash is removed."""
        client = APIClient("http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"
    
    @patch('core.api_client.requests.Session.get')
    def test_is_connected_success(self, mock_get, api_client):
        """Test connection check success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert api_client.is_connected() is True
    
    @patch('core.api_client.requests.Session.get')
    def test_is_connected_failure(self, mock_get, api_client):
        """Test connection check failure."""
        mock_get.side_effect = Exception("Connection error")
        assert api_client.is_connected() is False
    
    @patch('core.api_client.requests.Session.request')
    def test_request_success(self, mock_request, api_client):
        """Test successful request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response
        
        result = api_client._request("GET", "/test")
        assert result == {"data": "test"}
    
    @patch('core.api_client.requests.Session.request')
    def test_request_connection_error(self, mock_request, api_client):
        """Test request with connection error."""
        import requests
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        result = api_client._request("GET", "/test")
        assert result is None
        assert mock_request.call_count == 3
    
    @patch('core.api_client.requests.Session.request')
    def test_start_simulator(self, mock_request, api_client):
        """Test start simulator."""
        mock_response = Mock()
        mock_response.json.return_value = {"message": "started"}
        mock_request.return_value = mock_response
        
        result = api_client.start_simulator()
        assert result == {"message": "started"}
    
    @patch('core.api_client.requests.Session.request')
    def test_get_nodes(self, mock_request, api_client):
        """Test get nodes."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "nodes": [
                {"id": "node_0", "role": "validator"},
                {"id": "node_4", "role": "regular"}
            ]
        }
        mock_request.return_value = mock_response
        
        result = api_client.get_nodes()
        assert len(result) == 2
        assert result[0]["id"] == "node_0"
    
    @patch('core.api_client.requests.Session.request')
    def test_trigger_attack(self, mock_request, api_client):
        """Test trigger attack."""
        mock_response = Mock()
        mock_response.json.return_value = {"attack_id": "123"}
        mock_request.return_value = mock_response
        
        result = api_client.trigger_attack(
            "ddos",
            target="node_5",
            parameters={"intensity": 8}
        )
        assert result["attack_id"] == "123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
