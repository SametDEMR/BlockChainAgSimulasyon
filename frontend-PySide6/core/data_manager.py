"""Data Manager for handling API data and caching."""
from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Optional


class DataManager(QObject):
    """Manages API data, caching, and emits signals on updates."""
    
    # Data update signals
    status_updated = Signal(dict)
    attacks_updated = Signal(dict)
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
    
    def _parse_blockchain(self, raw_data: dict) -> dict:
        """Parse backend blockchain data to expected format.
        
        Args:
            raw_data: Raw blockchain data from API
            
        Returns:
            Parsed blockchain data
        """
        # Get nested chain data
        chain_data = raw_data.get('chain', {})
        blocks_raw = chain_data.get('chain', [])
        
        # Parse blocks
        blocks = []
        for block in blocks_raw:
            parsed_block = {
                'index': block.get('index', 0),
                'hash': block.get('hash', ''),
                'previous_hash': block.get('previous_hash', '0'),
                'miner_id': block.get('miner', 'unknown'),
                'transaction_count': len(block.get('transactions', [])),
                'transactions': block.get('transactions', []),
                'timestamp': block.get('timestamp', ''),
                'nonce': block.get('nonce', 0),
                'is_orphan': False,  # Will be set by fork detection
                'is_malicious': False
            }
            blocks.append(parsed_block)
        
        # Get fork status
        fork_status = chain_data.get('fork_status', {})
        
        return {
            'chain_length': chain_data.get('chain_length', 0),
            'pending_transactions': chain_data.get('pending_transactions_count', 0),
            'blocks': blocks,
            'fork_status': fork_status
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
                # Parse blockchain data
                parsed = self._parse_blockchain(blockchain)
                self._cache['blockchain'] = parsed
                self.blockchain_updated.emit(parsed)

            pbft = self.api_client.get_pbft_status()
            if pbft and 'error' not in pbft:
                # Transform to widget format
                transformed_pbft = {
                    'primary': pbft.get('primary', 'N/A'),
                    'view': pbft.get('current_view', 0),
                    'consensus_count': pbft.get('total_consensus_reached', 0),
                    'validator_count': pbft.get('total_validators', 0),
                    'total_messages': pbft.get('total_messages', 0)
                }
                self._cache['pbft'] = transformed_pbft
                self.pbft_updated.emit(transformed_pbft)

            metrics = self.api_client.get_metrics()
            if metrics and 'error' not in metrics:
                self._cache['metrics'] = metrics
                self.metrics_updated.emit(metrics)

            # Attack status güncelle - GÜNCELLENMİŞ BÖLÜM
            attacks = self.api_client.get_attack_status()
            if attacks:  # None kontrolü yeterli, 'error' kontrolüne gerek yok
                self._cache['attacks'] = attacks
                self.attacks_updated.emit(attacks)

            messages = self.api_client.get_network_messages()
            if messages and 'error' not in messages:
                raw_messages = messages.get('recent_messages', [])
                
                # Transform to widget format
                transformed = []
                for msg in raw_messages:
                    # Extract view from content.pbft_message
                    view = 0
                    content = msg.get('content', {})
                    pbft_msg = content.get('pbft_message', {})
                    if pbft_msg:
                        view = pbft_msg.get('view', 0)
                    
                    transformed.append({
                        'timestamp': msg.get('timestamp', ''),
                        'sender': msg.get('sender_id', ''),
                        'receiver': msg.get('receiver_id', ''),
                        'type': msg.get('message_type', '').upper(),  # Uppercase for display
                        'view': view
                    })
                
                self._cache['messages'] = transformed
                self.messages_updated.emit(transformed)

            fork_status = self.api_client.get_fork_status()
            if fork_status and 'error' not in fork_status:
                print("🔍 DEBUG - Fork Status Alındı:", fork_status)  # EKLE
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
    
    def fetch_pbft_status(self) -> Optional[Dict]:
        """Fetch PBFT status from API.
        
        Returns:
            PBFT status data with transformed keys
        """
        try:
            pbft = self.api_client.get_pbft_status()
            if pbft and 'error' not in pbft:
                # Transform API response to standard format
                transformed = {
                    'primary': pbft.get('primary_validator', 'N/A'),
                    'view': pbft.get('current_view', 0),
                    'consensus_count': pbft.get('consensus_achieved_count', 0),
                    'validator_count': pbft.get('total_validators', 0),
                    'total_messages': pbft.get('total_messages', 0)
                }
                return transformed
            return None
        except Exception as e:
            self.api_error.emit(f"PBFT fetch error: {str(e)}")
            return None
    
    def fetch_messages(self, limit: int = 100) -> Optional[Dict]:
        """Fetch network messages from API.
        
        Args:
            limit: Maximum number of messages to fetch
            
        Returns:
            Messages data (dict or list)
        """
        try:
            messages = self.api_client.get_network_messages()
            if messages and 'error' not in messages:
                # Get message list
                msg_list = messages.get('messages', [])
                
                # Apply limit
                if len(msg_list) > limit:
                    msg_list = msg_list[-limit:]  # Get last N messages
                
                # Transform to standard format
                transformed = []
                for msg in msg_list:
                    transformed.append({
                        'timestamp': msg.get('timestamp', ''),
                        'sender': msg.get('sender_id', ''),
                        'receiver': msg.get('receiver_id', ''),
                        'type': msg.get('message_type', ''),
                        'view': msg.get('view_number', 0)
                    })
                
                return {'messages': transformed}
            return None
        except Exception as e:
            self.api_error.emit(f"Messages fetch error: {str(e)}")
            return None
    
    def get_cached_fork_status(self) -> Optional[Dict]:
        """Get cached fork status."""
        return self._cache['fork_status']
    
    def get_fork_status(self) -> Optional[Dict]:
        """Get fork status (alias for get_cached_fork_status)."""
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
