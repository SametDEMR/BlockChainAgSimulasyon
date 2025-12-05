"""Data Manager for handling API data and caching."""
from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Optional


class DataManager(QObject):
    """Manages API data, caching, and emits signals on updates."""
    
    # Data update signals
    status_updated = Signal(dict)
    nodes_updated = Signal(list)
    blockchain_updated = Signal(dict)
    pbft_updated = Signal(dict)
    metrics_updated = Signal(dict)
    attacks_updated = Signal(dict)
    messages_updated = Signal(list)
    fork_status_updated = Signal(dict)
    
    # Error signals
    connection_error = Signal(str)
    api_error = Signal(str)
    
    def __init__(self, api_client):
        """Initialize data manager.
        
        Args:
            api_client: APIClient instance
        """
        super().__init__()
        self.api_client = api_client
        
        # Cache
        self._cache = {
            'status': None,
            'nodes': [],
            'blockchain': None,
            'pbft': None,
            'metrics': None,
            'attacks': None,
            'messages': [],
            'fork_status': None
        }
    
    def update_all_data(self):
        """Fetch all data from API and emit signals."""
        try:
            # Check connection first
            if not self.api_client.is_connected():
                self.connection_error.emit("Cannot connect to backend")
                return
            
            # Fetch all data
            status = self.api_client.get_status()
            if status and 'error' not in status:
                self._cache['status'] = status
                self.status_updated.emit(status)
            
            nodes = self.api_client.get_nodes()
            if nodes is not None:
                self._cache['nodes'] = nodes
                self.nodes_updated.emit(nodes)
            
            blockchain = self.api_client.get_blockchain()
            if blockchain and 'error' not in blockchain:
                self._cache['blockchain'] = blockchain
                self.blockchain_updated.emit(blockchain)
            
            pbft = self.api_client.get_pbft_status()
            if pbft and 'error' not in pbft:
                self._cache['pbft'] = pbft
                self.pbft_updated.emit(pbft)
            
            metrics = self.api_client.get_metrics()
            if metrics and 'error' not in metrics:
                self._cache['metrics'] = metrics
                self.metrics_updated.emit(metrics)
            
            attacks = self.api_client.get_attack_status()
            if attacks and 'error' not in attacks:
                self._cache['attacks'] = attacks
                self.attacks_updated.emit(attacks)
            
            messages = self.api_client.get_network_messages()
            if messages and 'error' not in messages:
                msg_list = messages.get('messages', [])
                self._cache['messages'] = msg_list
                self.messages_updated.emit(msg_list)
            
            fork_status = self.api_client.get_fork_status()
            if fork_status and 'error' not in fork_status:
                self._cache['fork_status'] = fork_status
                self.fork_status_updated.emit(fork_status)
                
        except Exception as e:
            self.api_error.emit(f"Data update error: {str(e)}")
    
    def get_cached_status(self) -> Optional[Dict]:
        """Get cached status."""
        return self._cache['status']
    
    def get_cached_nodes(self) -> List:
        """Get cached node list."""
        return self._cache['nodes']
    
    def get_cached_blockchain(self) -> Optional[Dict]:
        """Get cached blockchain."""
        return self._cache['blockchain']
    
    def get_cached_pbft(self) -> Optional[Dict]:
        """Get cached PBFT status."""
        return self._cache['pbft']
    
    def get_cached_metrics(self) -> Optional[Dict]:
        """Get cached metrics."""
        return self._cache['metrics']
    
    def get_cached_attacks(self) -> Optional[Dict]:
        """Get cached attacks."""
        return self._cache['attacks']
    
    def get_cached_messages(self) -> List:
        """Get cached messages."""
        return self._cache['messages']
    
    def get_cached_fork_status(self) -> Optional[Dict]:
        """Get cached fork status."""
        return self._cache['fork_status']
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """Get specific node from cache.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node data or None
        """
        for node in self._cache['nodes']:
            if node.get('id') == node_id:
                return node
        return None
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache = {
            'status': None,
            'nodes': [],
            'blockchain': None,
            'pbft': None,
            'metrics': None,
            'attacks': None,
            'messages': [],
            'fork_status': None
        }
