"""Blockchain Graph Widget - Custom QGraphicsView for blockchain visualization."""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QWheelEvent, QColor, QBrush


class BlockchainGraphWidget(QGraphicsView):
    """Custom graphics view for blockchain visualization."""
    
    # Signals
    block_clicked = Signal(dict)  # Emits block data when clicked
    block_double_clicked = Signal(dict)  # Emits block data when double-clicked
    
    def __init__(self, parent=None):
        """Initialize blockchain graph widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # View settings
        self._setup_view()
        
        # Zoom settings
        self._zoom_factor = 1.0
        self._min_zoom = 0.3
        self._max_zoom = 3.0
        self._zoom_step = 0.1
        
        # Pan settings
        self._is_panning = False
        self._pan_start_pos = None
    
    def _setup_view(self):
        """Setup view properties."""
        # Enable antialiasing
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Horizontal scrolling only, no vertical
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Drag mode - allow panning with hand drag
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Transform anchor - keep center when zooming
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # Scene rect - fixed height, wide width for horizontal scrolling
        self.setSceneRect(0, -300, 2000, 600)  # Centered vertically
        
        # Background color
        self.setBackgroundBrush(QBrush(QColor("#F5F5F5")))
        
        # Disable vertical scrolling programmatically
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel - convert to horizontal scrolling.
        
        Args:
            event: Wheel event
        """
        # Convert vertical wheel movement to horizontal scroll
        delta = event.angleDelta().y()
        
        # Get horizontal scrollbar
        h_scrollbar = self.horizontalScrollBar()
        
        # Scroll horizontally (negative delta = right, positive = left)
        h_scrollbar.setValue(h_scrollbar.value() - delta)
        
        # Accept event to prevent default behavior
        event.accept()
    
    def zoom_in(self):
        """Zoom in the view."""
        new_zoom = self._zoom_factor * (1.0 + self._zoom_step)
        if new_zoom <= self._max_zoom:
            factor = 1.0 + self._zoom_step
            self.scale(factor, factor)
            self._zoom_factor = new_zoom
    
    def zoom_out(self):
        """Zoom out the view."""
        new_zoom = self._zoom_factor * (1.0 - self._zoom_step)
        if new_zoom >= self._min_zoom:
            factor = 1.0 - self._zoom_step
            self.scale(factor, factor)
            self._zoom_factor = new_zoom
    
    def reset_zoom(self):
        """Reset zoom to 1.0."""
        # Calculate scale factor needed to reset
        reset_factor = 1.0 / self._zoom_factor
        self.scale(reset_factor, reset_factor)
        self._zoom_factor = 1.0
    
    def fit_view(self):
        """Fit all items in view."""
        # Get scene bounding rect
        scene_rect = self.scene.itemsBoundingRect()
        
        if not scene_rect.isEmpty():
            # Add some padding
            padding = 50
            scene_rect.adjust(-padding, -padding, padding, padding)
            
            # Fit rect in view
            self.fitInView(scene_rect, Qt.KeepAspectRatio)
            
            # Update zoom factor
            transform = self.transform()
            self._zoom_factor = transform.m11()  # Get x-axis scale
    
    def clear_blocks(self):
        """Clear all blocks from scene."""
        self.scene.clear()
        self._zoom_factor = 1.0
        self.resetTransform()
    
    def add_block_item(self, block_item):
        """Add a block item to the scene.
        
        Args:
            block_item: BlockItem to add
        """
        self.scene.addItem(block_item)
        
        # Connect block signals
        if hasattr(block_item, 'clicked'):
            block_item.clicked.connect(self.block_clicked.emit)
        if hasattr(block_item, 'double_clicked'):
            block_item.double_clicked.connect(self.block_double_clicked.emit)
    
    def add_connection_line(self, line_item):
        """Add a connection line to the scene.
        
        Args:
            line_item: QGraphicsLineItem to add
        """
        self.scene.addItem(line_item)
    
    def update_scene_rect(self, blocks_count=0):
        """Update scene rect based on number of blocks - centered vertically.
        
        Args:
            blocks_count: Number of blocks to accommodate
        """
        if blocks_count > 0:
            # Each block is ~170px wide (140px + 30px spacing)
            width = max(2000, blocks_count * 170 + 200)
            # Fixed height, centered at 0
            self.setSceneRect(0, -300, width, 600)
        else:
            self.setSceneRect(0, -300, 2000, 600)
    
    def get_zoom_level(self):
        """Get current zoom level.
        
        Returns:
            float: Current zoom factor
        """
        return self._zoom_factor
    
    def set_zoom_level(self, zoom_level):
        """Set zoom level.
        
        Args:
            zoom_level: Zoom factor to set
        """
        if self._min_zoom <= zoom_level <= self._max_zoom:
            # Reset first
            self.reset_zoom()
            # Apply new zoom
            self.scale(zoom_level, zoom_level)
            self._zoom_factor = zoom_level
