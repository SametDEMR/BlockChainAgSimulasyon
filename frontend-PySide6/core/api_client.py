"""API Client for backend communication."""
import requests
from typing import Dict, List, Optional
from urllib.parse import urljoin


class APIClient:
    """Client for communicating with FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.
        
        Args:
            base_url: Backend API base URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 5
        self._max_retries = 3
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self._max_retries):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError:
                if attempt == self._max_retries - 1:
                    return None
            except requests.exceptions.Timeout:
                if attempt == self._max_retries - 1:
                    return None
            except requests.exceptions.HTTPError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": str(e)}
        return None
    
    def is_connected(self) -> bool:
        """Check if backend is accessible.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/", 
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    # Simulator Control
    def start_simulator(self) -> Dict:
        """Start the simulator."""
        return self._request("POST", "/start")
    
    def stop_simulator(self) -> Dict:
        """Stop the simulator."""
        return self._request("POST", "/stop")
    
    def reset_simulator(self) -> Dict:
        """Reset the simulator."""
        return self._request("POST", "/reset")
    
    # Data Fetching
    def get_status(self) -> Dict:
        """Get simulator status."""
        return self._request("GET", "/status")
    
    def get_nodes(self) -> List:
        """Get all nodes."""
        result = self._request("GET", "/nodes")
        return result.get("nodes", []) if result else []
    
    def get_node_detail(self, node_id: str) -> Dict:
        """Get specific node details."""
        return self._request("GET", f"/nodes/{node_id}")
    
    def get_blockchain(self) -> Dict:
        """Get blockchain data."""
        return self._request("GET", "/blockchain")
    
    def get_fork_status(self) -> Dict:
        """Get fork status."""
        return self._request("GET", "/blockchain/fork-status")
    
    def get_pbft_status(self) -> Dict:
        """Get PBFT consensus status."""
        return self._request("GET", "/pbft/status")
    
    def get_network_messages(self, limit: Optional[int] = None) -> Dict:
        """Get network message traffic.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            Network messages data
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        return self._request("GET", "/network/messages", params=params)
    
    def get_metrics(self) -> Dict:
        """Get all node metrics."""
        return self._request("GET", "/metrics")
    
    def get_node_metrics(self, node_id: str) -> Dict:
        """Get specific node metrics."""
        return self._request("GET", f"/metrics/{node_id}")
    
    # Attack Triggers
    def trigger_attack(
        self, 
        attack_type: str, 
        target: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Trigger an attack with appropriate endpoint and payload."""
        attack_type_lower = attack_type.lower()
        
        # Route to specific endpoints based on attack type
        if attack_type_lower == "sybil":
            # Sybil attack has its own endpoint
            fake_node_count = parameters.get("fake_node_count", 10) if parameters else 10
            return self._request(
                "POST", 
                f"/attack/sybil/trigger?num_nodes={fake_node_count}"
            )
        
        elif attack_type_lower == "majority":
            # Majority attack has its own endpoint
            return self._request("POST", "/attack/majority/trigger")
        
        elif attack_type_lower == "partition":
            # Network partition has its own endpoint
            return self._request("POST", "/attack/partition/trigger")
        
        elif attack_type_lower == "selfish_mining":
            # Selfish mining has its own endpoint
            attacker_id = parameters.get("attacker_id") if parameters else target
            if not attacker_id:
                return {"error": "Selfish mining requires attacker_id"}
            return self._request(
                "POST",
                f"/attack/selfish/trigger?target_node_id={attacker_id}"
            )
        
        elif attack_type_lower in ["ddos", "byzantine"]:
            # DDoS and Byzantine use the generic trigger endpoint
            if not target:
                return {"error": f"{attack_type} attack requires target"}
            
            payload = {
                "attack_type": attack_type_lower,
                "target_node_id": target,
                "parameters": parameters or {}
            }
            return self._request("POST", "/attack/trigger", json=payload)
        
        else:
            return {"error": f"Unknown attack type: {attack_type}"}
    
    def stop_attack(self, attack_id: str) -> Dict:
        """Stop an active attack."""
        return self._request("POST", f"/attack/stop/{attack_id}")
    
    def get_attack_status(self) -> Dict:
        """Get attack status."""
        return self._request("GET", "/attack/status")
    
    def get_specific_attack_status(self, attack_id: str) -> Dict:
        """Get specific attack status."""
        return self._request("GET", f"/attack/status/{attack_id}")
