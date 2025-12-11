"""Chain Drawing Logic - Handles blockchain visualization layout and connections."""
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import Qt, QLineF
from PySide6.QtGui import QPen, QColor


class ChainDrawer:
    """Handles blockchain chain drawing and layout."""
    
    # Layout constants
    BLOCK_WIDTH = 100
    BLOCK_HEIGHT = 80
    HORIZONTAL_SPACING = 20
    VERTICAL_SPACING = 100
    BASE_Y = 50
    
    # Line colors
    MAIN_CHAIN_COLOR = QColor('#4CAF50')      # Green
    FORK_CHAIN_COLOR = QColor('#FF9800')      # Orange
    ORPHAN_LINE_COLOR = QColor('#9E9E9E')     # Gray
    
    def __init__(self):
        """Initialize chain drawer."""
        self.blocks = []
        self.connections = []
        self.fork_levels = {}  # Track Y-offset for each fork
    
    def calculate_layout(self, blockchain_data):
        """Calculate positions for all blocks.
        
        Args:
            blockchain_data: Dictionary containing blockchain information
            
        Returns:
            dict: Layout information with block positions and connections
        """
        blocks = blockchain_data.get('blocks', [])
        if not blocks:
            return {'blocks': [], 'connections': []}
        
        # Build block index map
        block_map = {block['hash']: block for block in blocks}
        
        # Identify main chain
        main_chain = self._identify_main_chain(blocks)
        
        # Identify forks
        forks = self._identify_forks(blocks, main_chain, block_map)
        
        # Calculate positions
        positions = self._calculate_positions(blocks, main_chain, forks)
        
        # Calculate connections
        connections = self._calculate_connections(blocks, positions, block_map)
        
        return {
            'blocks': [
                {
                    'data': block,
                    'position': positions[block['hash']],
                    'is_main_chain': block['hash'] in main_chain,
                    'fork_id': forks.get(block['hash'])
                }
                for block in blocks
            ],
            'connections': connections
        }
    
    def _identify_main_chain(self, blocks):
        """Identify main chain (longest chain).
        
        Args:
            blocks: List of blocks
            
        Returns:
            set: Set of block hashes in main chain
        """
        if not blocks:
            return set()
        
        # Find block with highest index
        max_index_block = max(blocks, key=lambda b: b.get('index', 0))
        
        # Trace back to genesis
        main_chain = set()
        current_hash = max_index_block['hash']
        block_map = {block['hash']: block for block in blocks}
        
        while current_hash in block_map:
            block = block_map[current_hash]
            main_chain.add(current_hash)
            
            # Move to previous block
            prev_hash = block.get('previous_hash')
            if prev_hash == '0' or prev_hash not in block_map:
                break
            current_hash = prev_hash
        
        return main_chain
    
    def _identify_forks(self, blocks, main_chain, block_map):
        """Identify fork branches.
        
        Args:
            blocks: List of blocks
            main_chain: Set of main chain block hashes
            block_map: Hash to block mapping
            
        Returns:
            dict: Block hash to fork_id mapping
        """
        forks = {}
        fork_id = 0
        
        for block in blocks:
            block_hash = block['hash']
            
            # Skip if in main chain or orphan
            if block_hash in main_chain or block.get('is_orphan'):
                continue
            
            # This is a fork block
            forks[block_hash] = fork_id
            
            # Trace back until we hit main chain or genesis
            current_hash = block.get('previous_hash')
            while current_hash and current_hash not in main_chain:
                if current_hash in block_map:
                    forks[current_hash] = fork_id
                    current_hash = block_map[current_hash].get('previous_hash')
                else:
                    break
            
            fork_id += 1
        
        return forks
    
    def _calculate_positions(self, blocks, main_chain, forks):
        """Calculate X,Y positions for all blocks.
        
        Args:
            blocks: List of blocks
            main_chain: Set of main chain hashes
            forks: Fork mapping
            
        Returns:
            dict: Hash to (x, y) position mapping
        """
        positions = {}
        fork_offsets = {}
        
        for block in blocks:
            block_hash = block['hash']
            index = block.get('index', 0)
            
            # X position based on index
            x = index * (self.BLOCK_WIDTH + self.HORIZONTAL_SPACING)
            
            # Y position based on chain type
            if block_hash in main_chain:
                # Main chain at base level
                y = self.BASE_Y
            elif block.get('is_orphan'):
                # Orphan blocks below main chain
                y = self.BASE_Y + self.VERTICAL_SPACING * 2
            else:
                # Fork blocks above main chain
                fork_id = forks.get(block_hash, 0)
                if fork_id not in fork_offsets:
                    fork_offsets[fork_id] = len(fork_offsets) + 1
                y = self.BASE_Y - self.VERTICAL_SPACING * fork_offsets[fork_id]
            
            positions[block_hash] = (x, y)
        
        return positions
    
    def _calculate_connections(self, blocks, positions, block_map):
        """Calculate connection lines between blocks.
        
        Args:
            blocks: List of blocks
            positions: Position mapping
            block_map: Hash to block mapping
            
        Returns:
            list: List of connection line definitions
        """
        connections = []
        
        for block in blocks:
            prev_hash = block.get('previous_hash')
            
            # Skip if no previous or genesis
            if not prev_hash or prev_hash == '0':
                continue
            
            # Skip if previous block doesn't exist
            if prev_hash not in positions:
                continue
            
            # Get positions
            curr_hash = block['hash']
            from_pos = positions[prev_hash]
            to_pos = positions[curr_hash]
            
            # Adjust for block dimensions (connect right edge to left edge)
            from_x = from_pos[0] + self.BLOCK_WIDTH
            from_y = from_pos[1] + self.BLOCK_HEIGHT / 2
            to_x = to_pos[0]
            to_y = to_pos[1] + self.BLOCK_HEIGHT / 2
            
            # Determine line color
            if block.get('is_orphan'):
                color = self.ORPHAN_LINE_COLOR
            elif curr_hash in positions and prev_hash in positions:
                # Check if both blocks are at same Y level (main chain)
                if abs(from_pos[1] - to_pos[1]) < 10:
                    color = self.MAIN_CHAIN_COLOR
                else:
                    color = self.FORK_CHAIN_COLOR
            else:
                color = self.MAIN_CHAIN_COLOR
            
            connections.append({
                'from': (from_x, from_y),
                'to': (to_x, to_y),
                'color': color,
                'from_hash': prev_hash,
                'to_hash': curr_hash
            })
        
        return connections
    
    def create_connection_line(self, connection_info):
        """Create QGraphicsLineItem from connection info.
        
        Args:
            connection_info: Connection dictionary
            
        Returns:
            QGraphicsLineItem: Line item
        """
        from_pos = connection_info['from']
        to_pos = connection_info['to']
        color = connection_info['color']
        
        line = QGraphicsLineItem(
            from_pos[0], from_pos[1],
            to_pos[0], to_pos[1]
        )
        
        pen = QPen(color, 2)
        line.setPen(pen)
        line.setZValue(-1)  # Draw behind blocks
        
        return line
    
    def get_scene_bounds(self, layout):
        """Calculate scene bounding box.
        
        Args:
            layout: Layout dictionary
            
        Returns:
            tuple: (min_x, min_y, max_x, max_y)
        """
        if not layout['blocks']:
            return (0, 0, 2000, 600)
        
        positions = [b['position'] for b in layout['blocks']]
        
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions) + self.BLOCK_WIDTH
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions) + self.BLOCK_HEIGHT
        
        # Add padding
        padding = 50
        return (
            min_x - padding,
            min_y - padding,
            max_x + padding,
            max_y + padding
        )
