"""
Tests for Network Map Page
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication, QPushButton, QGroupBox
from PySide6.QtCore import Qt
from ui.pages.network_page import NetworkMapPage
from ui.widgets.network_graph_widget import NetworkGraphWidget


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_data_manager():
    """Mock data manager fixture"""
    from unittest.mock import Mock
    dm = Mock()
    dm.nodes_updated = Mock()
    dm.nodes_updated.connect = Mock()
    return dm


@pytest.fixture
def network_page(qapp, mock_data_manager):
    """Network page fixture"""
    page = NetworkMapPage(mock_data_manager)
    return page


@pytest.fixture
def sample_nodes():
    """Sample node data"""
    return [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
    ]


class TestNetworkMapPage:
    """Test suite for NetworkMapPage"""
    
    def test_creation(self, network_page):
        """Test page can be created"""
        assert network_page is not None
        assert isinstance(network_page, NetworkMapPage)
    
    def test_has_data_manager(self, network_page, mock_data_manager):
        """Test page has data manager"""
        assert network_page.data_manager is mock_data_manager
    
    def test_data_manager_signal_connected(self, mock_data_manager):
        """Test data manager nodes_updated signal is connected"""
        page = NetworkMapPage(mock_data_manager)
        mock_data_manager.nodes_updated.connect.assert_called_once()
    
    def test_graph_widget_exists(self, network_page):
        """Test graph widget is present"""
        assert network_page.graph_widget is not None
        assert isinstance(network_page.graph_widget, NetworkGraphWidget)
    
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
    
    def test_legend_exists(self, network_page):
        """Test legend group box exists"""
        legend_found = False
        for child in network_page.children():
            if isinstance(child, QGroupBox) and "Legend" in child.title():
                legend_found = True
                break
        assert legend_found, "Legend group box not found"
    
    def test_zoom_in_button_connected(self, network_page):
        """Test zoom in button is connected"""
        initial_zoom = network_page.graph_widget.current_zoom
        network_page.zoom_in_btn.click()
        assert network_page.graph_widget.current_zoom > initial_zoom
    
    def test_zoom_out_button_connected(self, network_page):
        """Test zoom out button is connected"""
        network_page.zoom_in_btn.click()
        initial_zoom = network_page.graph_widget.current_zoom
        network_page.zoom_out_btn.click()
        assert network_page.graph_widget.current_zoom < initial_zoom
    
    def test_fit_view_button_connected(self, network_page, sample_nodes):
        """Test fit view button is connected"""
        network_page.update_network(sample_nodes)
        network_page.zoom_in_btn.click()
        network_page.fit_btn.click()
        assert network_page.graph_widget.current_zoom == 1.0
    
    def test_reset_button_connected(self, network_page, sample_nodes):
        """Test reset button is connected"""
        network_page.update_network(sample_nodes)
        network_page.zoom_in_btn.click()
        network_page.reset_btn.click()
        assert network_page.graph_widget.current_zoom == 1.0
    
    def test_update_network(self, network_page, sample_nodes):
        """Test update_network method"""
        network_page.update_network(sample_nodes)
        assert len(network_page.graph_widget.node_items) == len(sample_nodes)
    
    def test_clear_network(self, network_page, sample_nodes):
        """Test clear_network method"""
        network_page.update_network(sample_nodes)
        assert len(network_page.graph_widget.node_items) > 0
        network_page.clear_network()
        assert len(network_page.graph_widget.node_items) == 0
    
    def test_highlight_node(self, network_page, sample_nodes):
        """Test highlight_node method"""
        network_page.update_network(sample_nodes)
        network_page.highlight_node('node_0')
        selected = network_page.get_selected_node()
        assert selected == 'node_0'
    
    def test_get_selected_node(self, network_page):
        """Test get_selected_node method"""
        selected = network_page.get_selected_node()
        assert selected == ""
    
    def test_node_selected_signal(self, network_page):
        """Test node_selected signal exists"""
        assert hasattr(network_page, 'node_selected')
    
    def test_buttons_enabled(self, network_page):
        """Test all buttons are enabled by default"""
        assert network_page.zoom_in_btn.isEnabled()
        assert network_page.zoom_out_btn.isEnabled()
        assert network_page.fit_btn.isEnabled()
        assert network_page.reset_btn.isEnabled()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
