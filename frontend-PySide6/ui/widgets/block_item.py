"""Block Item - Custom QGraphicsItem for blockchain block visualization."""
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QRectF, QObject
from PySide6.QtGui import QColor, QBrush, QPen, QFont


class BlockItem(QGraphicsRectItem):
    """Custom graphics item representing a blockchain block."""
    
    # Block type colors
    COLORS = {
        'genesis': QColor('#2196F3'),      # Blue
        'normal': QColor('#4CAF50'),       # Green
        'malicious': QColor('#F44336'),    # Red
        'orphan': QColor('#9E9E9E')        # Gray
    }
    
    def __init__(self, block_data, parent=None):
        """Initialize block item.
        
        Args:
            block_data: Dictionary containing block information
            parent: Parent item
        """
        super().__init__(0, 0, 100, 80, parent)
        
        self.block_data = block_data
        self._signal_proxy = BlockItemSignalProxy()
        
        # Extract block info
        self.index = block_data.get('index', 0)
        self.hash = block_data.get('hash', 'N/A')[:8]  # First 8 chars
        self.miner = block_data.get('miner_id', 'N/A')
        self.tx_count = block_data.get('transaction_count', 0)
        self.block_type = self._determine_block_type(block_data)
        
        # Setup appearance
        self._setup_appearance()
        self._create_content()
        
        # Enable interaction
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Setup tooltip
        self._setup_tooltip()
    
    def _determine_block_type(self, block_data):
        """Determine block type from data.
        
        Args:
            block_data: Block data dictionary
            
        Returns:
            str: Block type (genesis, normal, malicious, orphan)
        """
        if block_data.get('index') == 0:
            return 'genesis'
        elif block_data.get('is_orphan', False):
            return 'orphan'
        elif block_data.get('is_malicious', False):
            return 'malicious'
        else:
            return 'normal'
    
    def _setup_appearance(self):
        """Setup block appearance based on type."""
        # Get color for block type
        color = self.COLORS.get(self.block_type, self.COLORS['normal'])
        
        # Set brush and pen
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
    
    def _create_content(self):
        """Create text content inside block."""
        # Index (large, centered at top)
        self.index_text = QGraphicsTextItem(str(self.index), self)
        font = QFont("Arial", 16, QFont.Bold)
        self.index_text.setFont(font)
        self.index_text.setDefaultTextColor(Qt.white)
        
        # Center index text
        index_rect = self.index_text.boundingRect()
        x = (100 - index_rect.width()) / 2
        self.index_text.setPos(x, 5)
        
        # Hash (smaller, below index)
        self.hash_text = QGraphicsTextItem(f"#{self.hash}", self)
        font = QFont("Courier", 8)
        self.hash_text.setFont(font)
        self.hash_text.setDefaultTextColor(Qt.white)
        
        # Center hash text
        hash_rect = self.hash_text.boundingRect()
        x = (100 - hash_rect.width()) / 2
        self.hash_text.setPos(x, 30)
        
        # Miner (smaller, below hash)
        self.miner_text = QGraphicsTextItem(f"M:{self.miner[:6]}", self)
        font = QFont("Arial", 7)
        self.miner_text.setFont(font)
        self.miner_text.setDefaultTextColor(Qt.white)
        self.miner_text.setPos(5, 50)
        
        # TX count (smaller, bottom right)
        self.tx_text = QGraphicsTextItem(f"TX:{self.tx_count}", self)
        font = QFont("Arial", 7)
        self.tx_text.setFont(font)
        self.tx_text.setDefaultTextColor(Qt.white)
        
        # Right align TX count
        tx_rect = self.tx_text.boundingRect()
        x = 95 - tx_rect.width()
        self.tx_text.setPos(x, 50)
    
    def _setup_tooltip(self):
        """Setup hover tooltip with full block details."""
        tooltip_lines = [
            f"Block #{self.index}",
            f"Hash: {self.block_data.get('hash', 'N/A')}",
            f"Previous: {self.block_data.get('previous_hash', 'N/A')[:16]}...",
            f"Miner: {self.miner}",
            f"Transactions: {self.tx_count}",
            f"Timestamp: {self.block_data.get('timestamp', 'N/A')}",
            f"Type: {self.block_type.capitalize()}"
        ]
        self.setToolTip("\n".join(tooltip_lines))
    
    def hoverEnterEvent(self, event):
        """Handle hover enter - highlight block.
        
        Args:
            event: Hover event
        """
        # Make border thicker
        self.setPen(QPen(Qt.yellow, 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave - remove highlight.
        
        Args:
            event: Hover event
        """
        # Reset border
        self.setPen(QPen(Qt.black, 2))
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press - single click.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._signal_proxy.clicked.emit(self.block_data)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle mouse double click - open detail dialog.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._signal_proxy.double_clicked.emit(self.block_data)
        super().mouseDoubleClickEvent(event)
    
    def get_block_data(self):
        """Get block data.
        
        Returns:
            dict: Block data dictionary
        """
        return self.block_data
    
    def update_data(self, block_data):
        """Update block data and refresh display.
        
        Args:
            block_data: New block data
        """
        self.block_data = block_data
        self.index = block_data.get('index', 0)
        self.hash = block_data.get('hash', 'N/A')[:8]
        self.miner = block_data.get('miner_id', 'N/A')
        self.tx_count = block_data.get('transaction_count', 0)
        self.block_type = self._determine_block_type(block_data)
        
        # Update appearance
        self._setup_appearance()
        
        # Update text content
        self.index_text.setPlainText(str(self.index))
        self.hash_text.setPlainText(f"#{self.hash}")
        self.miner_text.setPlainText(f"M:{self.miner[:6]}")
        self.tx_text.setPlainText(f"TX:{self.tx_count}")
        
        # Update tooltip
        self._setup_tooltip()


class BlockItemSignalProxy(QObject):
    """Proxy class to emit signals from QGraphicsItem."""
    
    clicked = Signal(dict)
    double_clicked = Signal(dict)
