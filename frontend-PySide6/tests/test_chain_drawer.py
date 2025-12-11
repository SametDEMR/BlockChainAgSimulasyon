"""Tests for Chain Drawer."""
import pytest
from PySide6.QtWidgets import QApplication, QGraphicsLineItem
from PySide6.QtGui import QColor
import sys

from ui.widgets.chain_drawer import ChainDrawer


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def drawer():
    """Create ChainDrawer instance."""
    return ChainDrawer()


@pytest.fixture
def simple_blockchain():
    """Create simple blockchain with main chain."""
    return {
        'blocks': [
            {
                'index': 0,
                'hash': 'genesis_hash',
                'previous_hash': '0',
                'miner_id': 'genesis',
                'transaction_count': 0,
                'is_orphan': False,
                'is_malicious': False
            },
            {
                'index': 1,
                'hash': 'block1_hash',
                'previous_hash': 'genesis_hash',
                'miner_id': 'node1',
                'transaction_count': 2,
                'is_orphan': False,
                'is_malicious': False
            },
            {
                'index': 2,
                'hash': 'block2_hash',
                'previous_hash': 'block1_hash',
                'miner_id': 'node2',
                'transaction_count': 3,
                'is_orphan': False,
                'is_malicious': False
            }
        ]
    }


@pytest.fixture
def forked_blockchain():
    """Create blockchain with fork."""
    return {
        'blocks': [
            {
                'index': 0,
                'hash': 'genesis_hash',
                'previous_hash': '0',
                'miner_id': 'genesis',
                'transaction_count': 0,
                'is_orphan': False,
                'is_malicious': False
            },
            {
                'index': 1,
                'hash': 'block1_hash',
                'previous_hash': 'genesis_hash',
                'miner_id': 'node1',
                'transaction_count': 2,
                'is_orphan': False,
                'is_malicious': False
            },
            {
                'index': 2,
                'hash': 'block2_main',
                'previous_hash': 'block1_hash',
                'miner_id': 'node2',
                'transaction_count': 3,
                'is_orphan': False,
                'is_malicious': False
            },
            {
                'index': 2,
                'hash': 'block2_fork',
                'previous_hash': 'block1_hash',
                'miner_id': 'node3',
                'transaction_count': 1,
                'is_orphan': False,
                'is_malicious': False
            }
        ]
    }


class TestChainDrawer:
    """Test suite for ChainDrawer."""
    
    def test_initialization(self, drawer):
        """Test drawer initializes correctly."""
        assert drawer is not None
        assert drawer.BLOCK_WIDTH == 100
        assert drawer.BLOCK_HEIGHT == 80
        assert drawer.HORIZONTAL_SPACING == 20
    
    def test_empty_blockchain(self, drawer):
        """Test handling of empty blockchain."""
        result = drawer.calculate_layout({'blocks': []})
        assert result['blocks'] == []
        assert result['connections'] == []
    
    def test_simple_chain_layout(self, drawer, simple_blockchain):
        """Test layout calculation for simple chain."""
        layout = drawer.calculate_layout(simple_blockchain)
        
        assert len(layout['blocks']) == 3
        assert len(layout['connections']) == 2
        
        # Check all blocks have positions
        for block_info in layout['blocks']:
            assert 'position' in block_info
            assert len(block_info['position']) == 2
    
    def test_main_chain_identification(self, drawer, simple_blockchain):
        """Test main chain identification."""
        blocks = simple_blockchain['blocks']
        main_chain = drawer._identify_main_chain(blocks)
        
        assert 'genesis_hash' in main_chain
        assert 'block1_hash' in main_chain
        assert 'block2_hash' in main_chain
        assert len(main_chain) == 3
    
    def test_horizontal_positioning(self, drawer, simple_blockchain):
        """Test blocks are positioned horizontally by index."""
        layout = drawer.calculate_layout(simple_blockchain)
        
        positions = {b['data']['hash']: b['position'] for b in layout['blocks']}
        
        # Genesis at x=0
        assert positions['genesis_hash'][0] == 0
        
        # Block 1 at x=120 (100 + 20)
        assert positions['block1_hash'][0] == 120
        
        # Block 2 at x=240
        assert positions['block2_hash'][0] == 240
    
    def test_main_chain_y_position(self, drawer, simple_blockchain):
        """Test main chain blocks are at base Y."""
        layout = drawer.calculate_layout(simple_blockchain)
        
        for block_info in layout['blocks']:
            if block_info['is_main_chain']:
                assert block_info['position'][1] == drawer.BASE_Y
    
    def test_fork_identification(self, drawer, forked_blockchain):
        """Test fork identification."""
        blocks = forked_blockchain['blocks']
        main_chain = drawer._identify_main_chain(blocks)
        block_map = {b['hash']: b for b in blocks}
        
        forks = drawer._identify_forks(blocks, main_chain, block_map)
        
        # Should identify fork block
        assert 'block2_fork' in forks or len(forks) > 0
    
    def test_fork_y_offset(self, drawer, forked_blockchain):
        """Test fork blocks have different Y position."""
        layout = drawer.calculate_layout(forked_blockchain)
        
        positions = {b['data']['hash']: b['position'] for b in layout['blocks']}
        
        # Main chain and fork should have different Y values
        y_values = set(pos[1] for pos in positions.values())
        assert len(y_values) >= 2
    
    def test_connection_creation(self, drawer, simple_blockchain):
        """Test connection lines are created."""
        layout = drawer.calculate_layout(simple_blockchain)
        
        assert len(layout['connections']) == 2
        
        for conn in layout['connections']:
            assert 'from' in conn
            assert 'to' in conn
            assert 'color' in conn
            assert 'from_hash' in conn
            assert 'to_hash' in conn
    
    def test_connection_line_creation(self, drawer, qapp):
        """Test QGraphicsLineItem creation."""
        conn_info = {
            'from': (100, 50),
            'to': (220, 50),
            'color': QColor('#4CAF50'),
            'from_hash': 'hash1',
            'to_hash': 'hash2'
        }
        
        line = drawer.create_connection_line(conn_info)
        
        assert isinstance(line, QGraphicsLineItem)
        assert line.line().x1() == 100
        assert line.line().y1() == 50
        assert line.line().x2() == 220
        assert line.line().y2() == 50
    
    def test_orphan_block_positioning(self, drawer):
        """Test orphan blocks are positioned below main chain."""
        blockchain = {
            'blocks': [
                {
                    'index': 0,
                    'hash': 'genesis_hash',
                    'previous_hash': '0',
                    'miner_id': 'genesis',
                    'transaction_count': 0,
                    'is_orphan': False,
                    'is_malicious': False
                },
                {
                    'index': 1,
                    'hash': 'orphan_hash',
                    'previous_hash': 'unknown',
                    'miner_id': 'node1',
                    'transaction_count': 1,
                    'is_orphan': True,
                    'is_malicious': False
                }
            ]
        }
        
        layout = drawer.calculate_layout(blockchain)
        positions = {b['data']['hash']: b['position'] for b in layout['blocks']}
        
        # Orphan should be below main chain
        assert positions['orphan_hash'][1] > positions['genesis_hash'][1]
    
    def test_scene_bounds_calculation(self, drawer, simple_blockchain):
        """Test scene bounds calculation."""
        layout = drawer.calculate_layout(simple_blockchain)
        bounds = drawer.get_scene_bounds(layout)
        
        assert len(bounds) == 4
        min_x, min_y, max_x, max_y = bounds
        
        assert min_x < 0  # Has padding
        assert max_x > 240  # Beyond last block
        assert min_y < drawer.BASE_Y
        assert max_y > drawer.BASE_Y + drawer.BLOCK_HEIGHT
    
    def test_empty_bounds(self, drawer):
        """Test scene bounds for empty blockchain."""
        layout = {'blocks': []}
        bounds = drawer.get_scene_bounds(layout)
        
        assert bounds == (0, 0, 2000, 600)
    
    def test_line_colors(self, drawer):
        """Test line color definitions."""
        assert drawer.MAIN_CHAIN_COLOR == QColor('#4CAF50')
        assert drawer.FORK_CHAIN_COLOR == QColor('#FF9800')
        assert drawer.ORPHAN_LINE_COLOR == QColor('#9E9E9E')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
