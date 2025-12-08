"""
Tests for Network Map Page
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication, QPushButton, QFrame, QGroupBox
from PySide6.QtCore import Qt
from ui.pages.network_page import NetworkMapPage


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def network_page(qapp):
    """Network page fixture"""
    page = NetworkMapPage()
    return page


class TestNetworkMapPage:
    """Test suite for NetworkMapPage"""
    
    def test_creation(self, network_page):
        """Test page can be created"""
        assert network_page is not None
        assert isinstance(network_page, NetworkMapPage)
    
    def test_control_buttons_exist(self, network_page):
        """Test all control buttons are present"""
        assert network_page.zoom_in_btn is not None
        assert isinstance(network_page.zoom_in_btn, QPushButton)
        assert "Zoom In" in network_page.zoom_in_btn.text()
        
        assert network_page.zoom_out_btn is not None
        assert isinstance(network_page.zoom_out_btn, QPushButton)
        assert "Zoom Out" in network_page.zoom_out_btn.text()
        
        assert network_page.fit_btn is not None
        assert isinstance(network_page.fit_btn, QPushButton)
        assert "Fit" in network_page.fit_btn.text()
        
        assert network_page.reset_btn is not None
        assert isinstance(network_page.reset_btn, QPushButton)
        assert "Reset" in network_page.reset_btn.text()
    
    def test_graph_frame_exists(self, network_page):
        """Test graph frame is present"""
        assert network_page.graph_frame is not None
        assert isinstance(network_page.graph_frame, QFrame)
        assert network_page.graph_frame.minimumHeight() >= 400
    
    def test_legend_exists(self, network_page):
        """Test legend group box exists"""
        # Find legend group box
        legend_found = False
        for child in network_page.children():
            if isinstance(child, QGroupBox) and "Legend" in child.title():
                legend_found = True
                break
        assert legend_found, "Legend group box not found"
    
    def test_zoom_in_button_click(self, network_page, capsys):
        """Test zoom in button can be clicked"""
        network_page.zoom_in_btn.click()
        captured = capsys.readouterr()
        assert "Zoom in clicked" in captured.out
    
    def test_zoom_out_button_click(self, network_page, capsys):
        """Test zoom out button can be clicked"""
        network_page.zoom_out_btn.click()
        captured = capsys.readouterr()
        assert "Zoom out clicked" in captured.out
    
    def test_fit_view_button_click(self, network_page, capsys):
        """Test fit view button can be clicked"""
        network_page.fit_btn.click()
        captured = capsys.readouterr()
        assert "Fit view clicked" in captured.out
    
    def test_reset_button_click(self, network_page, capsys):
        """Test reset button can be clicked"""
        network_page.reset_btn.click()
        captured = capsys.readouterr()
        assert "Reset clicked" in captured.out
    
    def test_update_network(self, network_page, capsys):
        """Test update_network method"""
        test_nodes = [
            {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
        ]
        network_page.update_network(test_nodes)
        captured = capsys.readouterr()
        assert "Network update received: 2 nodes" in captured.out
    
    def test_clear_network(self, network_page, capsys):
        """Test clear_network method"""
        network_page.clear_network()
        captured = capsys.readouterr()
        assert "Network cleared" in captured.out
    
    def test_highlight_node(self, network_page, capsys):
        """Test highlight_node method"""
        network_page.highlight_node("node_0")
        captured = capsys.readouterr()
        assert "Highlighting node: node_0" in captured.out
    
    def test_get_selected_node(self, network_page):
        """Test get_selected_node method"""
        # Should return empty string initially (no graph widget yet)
        selected = network_page.get_selected_node()
        assert selected == ""
    
    def test_node_selected_signal(self, network_page):
        """Test node_selected signal exists"""
        assert hasattr(network_page, 'node_selected')
        # Signal will be tested when NetworkGraphWidget is implemented
    
    def test_buttons_enabled(self, network_page):
        """Test all buttons are enabled by default"""
        assert network_page.zoom_in_btn.isEnabled()
        assert network_page.zoom_out_btn.isEnabled()
        assert network_page.fit_btn.isEnabled()
        assert network_page.reset_btn.isEnabled()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
