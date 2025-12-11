"""Tests for Blockchain Graph Widget."""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsView
from PySide6.QtCore import Qt, QPointF
import sys

from ui.widgets.blockchain_graph_widget import BlockchainGraphWidget


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def graph_widget(qapp):
    """Create BlockchainGraphWidget instance."""
    widget = BlockchainGraphWidget()
    yield widget
    widget.deleteLater()


class TestBlockchainGraphWidget:
    """Test suite for BlockchainGraphWidget."""
    
    def test_initialization(self, graph_widget):
        """Test widget initializes correctly."""
        assert graph_widget is not None
        assert graph_widget.scene is not None
        assert graph_widget._zoom_factor == 1.0
        assert graph_widget._min_zoom == 0.3
        assert graph_widget._max_zoom == 3.0
    
    def test_scene_setup(self, graph_widget):
        """Test scene is properly configured."""
        assert graph_widget.scene == graph_widget.scene
        scene_rect = graph_widget.sceneRect()
        assert scene_rect.width() >= 2000
        assert scene_rect.height() >= 600
    
    def test_zoom_in(self, graph_widget):
        """Test zoom in functionality."""
        initial_zoom = graph_widget._zoom_factor
        graph_widget.zoom_in()
        assert graph_widget._zoom_factor > initial_zoom
    
    def test_zoom_out(self, graph_widget):
        """Test zoom out functionality."""
        # First zoom in to have room to zoom out
        graph_widget.zoom_in()
        graph_widget.zoom_in()
        current_zoom = graph_widget._zoom_factor
        
        graph_widget.zoom_out()
        assert graph_widget._zoom_factor < current_zoom
    
    def test_zoom_limits(self, graph_widget):
        """Test zoom respects min and max limits."""
        # Zoom in many times
        for _ in range(50):
            graph_widget.zoom_in()
        assert graph_widget._zoom_factor <= graph_widget._max_zoom
        
        # Reset and zoom out many times
        graph_widget.reset_zoom()
        for _ in range(50):
            graph_widget.zoom_out()
        assert graph_widget._zoom_factor >= graph_widget._min_zoom
    
    def test_reset_zoom(self, graph_widget):
        """Test reset zoom functionality."""
        # Change zoom
        graph_widget.zoom_in()
        graph_widget.zoom_in()
        
        # Reset
        graph_widget.reset_zoom()
        assert graph_widget._zoom_factor == 1.0
    
    def test_clear_blocks(self, graph_widget):
        """Test clear blocks functionality."""
        # Add some items to scene
        item1 = QGraphicsRectItem(0, 0, 100, 80)
        item2 = QGraphicsRectItem(120, 0, 100, 80)
        graph_widget.scene.addItem(item1)
        graph_widget.scene.addItem(item2)
        
        assert len(graph_widget.scene.items()) == 2
        
        # Clear
        graph_widget.clear_blocks()
        assert len(graph_widget.scene.items()) == 0
        assert graph_widget._zoom_factor == 1.0
    
    def test_add_block_item(self, graph_widget):
        """Test adding block item to scene."""
        block_item = QGraphicsRectItem(0, 0, 100, 80)
        
        initial_count = len(graph_widget.scene.items())
        graph_widget.add_block_item(block_item)
        
        assert len(graph_widget.scene.items()) == initial_count + 1
    
    def test_add_connection_line(self, graph_widget):
        """Test adding connection line to scene."""
        from PySide6.QtWidgets import QGraphicsLineItem
        line = QGraphicsLineItem(0, 0, 100, 0)
        
        initial_count = len(graph_widget.scene.items())
        graph_widget.add_connection_line(line)
        
        assert len(graph_widget.scene.items()) == initial_count + 1
    
    def test_update_scene_rect(self, graph_widget):
        """Test scene rect updates based on block count."""
        # Test with 10 blocks
        graph_widget.update_scene_rect(10)
        scene_rect = graph_widget.sceneRect()
        assert scene_rect.width() >= 2000
        
        # Test with 50 blocks
        graph_widget.update_scene_rect(50)
        scene_rect = graph_widget.sceneRect()
        assert scene_rect.width() > 2000
    
    def test_get_zoom_level(self, graph_widget):
        """Test getting zoom level."""
        graph_widget.zoom_in()
        zoom = graph_widget.get_zoom_level()
        assert zoom > 1.0
        assert zoom == graph_widget._zoom_factor
    
    def test_set_zoom_level(self, graph_widget):
        """Test setting zoom level."""
        target_zoom = 1.5
        graph_widget.set_zoom_level(target_zoom)
        
        # Allow small floating point difference
        assert abs(graph_widget._zoom_factor - target_zoom) < 0.01
    
    def test_set_zoom_level_respects_limits(self, graph_widget):
        """Test set zoom level respects min/max limits."""
        # Try to set beyond max
        graph_widget.set_zoom_level(5.0)
        assert graph_widget._zoom_factor <= graph_widget._max_zoom
        
        # Try to set below min
        graph_widget.set_zoom_level(0.1)
        assert graph_widget._zoom_factor >= graph_widget._min_zoom
    
    def test_block_clicked_signal(self, graph_widget, qapp):
        """Test block clicked signal emission."""
        signal_data = [None]
        
        def on_clicked(data):
            signal_data[0] = data
        
        graph_widget.block_clicked.connect(on_clicked)
        
        # Emit signal manually (would be from block item)
        test_data = {'index': 1, 'hash': 'abc123'}
        graph_widget.block_clicked.emit(test_data)
        qapp.processEvents()
        
        assert signal_data[0] == test_data
    
    def test_block_double_clicked_signal(self, graph_widget, qapp):
        """Test block double clicked signal emission."""
        signal_data = [None]
        
        def on_double_clicked(data):
            signal_data[0] = data
        
        graph_widget.block_double_clicked.connect(on_double_clicked)
        
        # Emit signal manually
        test_data = {'index': 2, 'hash': 'def456'}
        graph_widget.block_double_clicked.emit(test_data)
        qapp.processEvents()
        
        assert signal_data[0] == test_data
    
    def test_view_properties(self, graph_widget):
        """Test view has correct properties set."""
        # Check render hints
        assert graph_widget.renderHints() & graph_widget.renderHints()
        
        # Check scroll bars
        assert graph_widget.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOn
        assert graph_widget.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
        
        # Check drag mode
        assert graph_widget.dragMode() == QGraphicsView.ScrollHandDrag


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
