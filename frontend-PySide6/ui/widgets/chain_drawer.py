"""Chain Drawing Logic - Handles blockchain visualization layout and connections."""
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import Qt, QLineF
from PySide6.QtGui import QPen, QColor


class ChainDrawer:
    """Handles blockchain chain drawing and layout."""
    
    # Layout constants
    BLOCK_WIDTH = 140  # Updated from 100 to 140
    BLOCK_HEIGHT = 120  # Updated from 80 to 120
    HORIZONTAL_SPACING = 30  # Increased spacing for bigger blocks
    VERTICAL_SPACING = 130  # Increased for fork clarity
    BASE_Y = 0  # Center position (scene is -300 to 300)
    
    # Line colors
    MAIN_CHAIN_COLOR = QColor('#4CAF50')      # Green
    WINNER_CHAIN_COLOR = QColor('#4CAF50')    # Green
    ORPHAN_CHAIN_COLOR = QColor('#757575')    # Gray
    ACTIVE_FORK_COLOR = QColor('#FF9800')     # Orange
    
    def __init__(self):
        """Initialize chain drawer."""
        self.blocks = []
        self.connections = []
        self.fork_branches = []
    
    def calculate_layout(self, blockchain_data):
        """Calculate positions for all blocks with fork visualization.
        
        Args:
            blockchain_data: Dictionary containing blockchain and fork information
            
        Returns:
            dict: Layout information with block positions and connections
        """
        blocks = blockchain_data.get('blocks', [])
        if not blocks:
            return {'blocks': [], 'connections': []}
        
        # Get fork branches from blockchain data
        fork_status = blockchain_data.get('fork_status', {})
        fork_branches = fork_status.get('fork_branches', [])

        # Build block index map
        block_map = {block['hash']: block for block in blocks}

        # Process fork branches for visualization
        branch_info = self._process_fork_branches(fork_branches, blocks)

        # Calculate positions
        positions = self._calculate_positions_with_forks(blocks, branch_info)

        # Calculate connections
        connections = self._calculate_connections_with_forks(blocks, positions, block_map, branch_info)

        return {
            'blocks': [
                {
                    'data': block,
                    'position': positions.get(block['hash'], (0, 0)),
                    'branch_status': branch_info.get(block['hash'], {}).get('status', 'main')
                }
                for block in blocks
            ],
            'connections': connections,
            'fork_branches': fork_branches
        }

    def _process_fork_branches(self, fork_branches, blocks):
        """Process fork branches to assign blocks to branches.

        Args:
            fork_branches: List of fork branch data from backend
            blocks: List of all blocks

        Returns:
            dict: Block hash to branch info mapping
        """
        branch_info = {}

        for branch_idx, branch in enumerate(fork_branches):
            # Support both 'chain' and 'recent_blocks' from backend
            branch_chain = branch.get('chain', branch.get('recent_blocks', []))
            # Use branch-level status (not individual block status)
            branch_status = branch.get('status', 'active')  # 'active', 'orphaned', 'winner'
            is_main = branch.get('is_main', False)
            fork_point = branch.get('fork_point', 0)

            # Determine actual status for visualization
            if is_main:
                status = 'winner'  # Main chain = winner (green)
            elif branch_status == 'orphaned':
                status = 'orphaned'  # Orphaned = gray dashed
            else:
                status = 'active'  # Active fork = orange

            # Assign Y-level based on branch index
            y_offset = branch_idx - (len(fork_branches) - 1) / 2

            for block in branch_chain:
                block_hash = block.get('hash')
                if block_hash:
                    branch_info[block_hash] = {
                        'status': status,
                        'fork_point': fork_point,
                        'y_offset': y_offset,
                        'branch_idx': branch_idx,
                        'is_main': is_main
                    }

        return branch_info

    def _calculate_positions_with_forks(self, blocks, branch_info):
        """Calculate X,Y positions for blocks with fork branches.

        Args:
            blocks: List of blocks
            branch_info: Branch assignment info

        Returns:
            dict: Hash to (x, y) position mapping
        """
        positions = {}

        for block in blocks:
            block_hash = block['hash']
            index = block.get('index', 0)

            # X position based on index
            x = index * (self.BLOCK_WIDTH + self.HORIZONTAL_SPACING)

            # Y position based on branch
            if block_hash in branch_info:
                info = branch_info[block_hash]
                y_offset = info['y_offset']
                y = self.BASE_Y + (y_offset * self.VERTICAL_SPACING)
            else:
                # Main chain (no fork data)
                y = self.BASE_Y

            positions[block_hash] = (x, y)

        return positions

    def _calculate_connections_with_forks(self, blocks, positions, block_map, branch_info):
        """Calculate connection lines with fork-aware coloring.

        Args:
            blocks: List of blocks
            positions: Position mapping
            block_map: Hash to block mapping
            branch_info: Branch assignment info

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

            # Adjust for block dimensions
            from_x = from_pos[0] + self.BLOCK_WIDTH
            from_y = from_pos[1] + self.BLOCK_HEIGHT / 2
            to_x = to_pos[0]
            to_y = to_pos[1] + self.BLOCK_HEIGHT / 2

            # Determine line color and style based on branch status
            status = branch_info.get(curr_hash, {}).get('status', 'main')

            if status == 'orphaned':
                color = self.ORPHAN_CHAIN_COLOR
                style = Qt.PenStyle.DashLine
            elif status == 'winner':
                color = self.WINNER_CHAIN_COLOR
                style = Qt.PenStyle.SolidLine
            elif status == 'active':
                color = self.ACTIVE_FORK_COLOR
                style = Qt.PenStyle.SolidLine
            else:
                color = self.MAIN_CHAIN_COLOR
                style = Qt.PenStyle.SolidLine

            connections.append({
                'from': (from_x, from_y),
                'to': (to_x, to_y),
                'color': color,
                'style': style,
                'from_hash': prev_hash,
                'to_hash': curr_hash,
                'status': status
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
        style = connection_info.get('style', Qt.PenStyle.SolidLine)

        line = QGraphicsLineItem(
            from_pos[0], from_pos[1],
            to_pos[0], to_pos[1]
        )

        pen = QPen(color, 2)
        pen.setStyle(style)
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
        padding = 100
        return (
            min_x - padding,
            min_y - padding,
            max_x + padding,
            max_y + padding
        )