"""
Tests for NetworkGraphWidget
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.widgets.network_graph_widget import NetworkGraphWidget, NodeItem


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def graph_widget(qapp):
    """NetworkGraphWidget fixture"""
    widget = NetworkGraphWidget()
    return widget


@pytest.fixture
def sample_nodes():
    """Sample node data"""
    return [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy', 'response_time': 48, 'trust_score': 88},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy', 'response_time': 55},
        {'id': 'node_3', 'role': 'regular', 'status': 'under_attack', 'response_time': 150},
        {'id': 'node_4', 'role': 'regular', 'status': 'healthy', 'is_sybil': True},
        {'id': 'node_5', 'role': 'validator', 'status': 'healthy', 'is_byzantine': True, 'trust_score': 65},
    ]


class TestNetworkGraphWidget:
    """Test suite for NetworkGraphWidget"""
    
    def test_creation(self, graph_widget):
        """Test widget can be created"""
        assert graph_widget is not None
        assert isinstance(graph_widget, NetworkGraphWidget)
        assert graph_widget.scene is not None
    
    def test_initial_state(self, graph_widget):
        """Test initial state"""
        assert len(graph_widget.node_items) == 0
        assert len(graph_widget.edge_items) == 0
        assert len(graph_widget.node_positions) == 0
        assert graph_widget.current_zoom == 1.0
    
    def test_clear_graph(self, graph_widget, sample_nodes):
        """Test clear_graph method"""
        graph_widget.update_graph(sample_nodes)
        assert len(graph_widget.node_items) > 0
        
        graph_widget.clear_graph()
        assert len(graph_widget.node_items) == 0
        assert len(graph_widget.edge_items) == 0
        assert len(graph_widget.node_positions) == 0
    
    def test_update_graph_with_nodes(self, graph_widget, sample_nodes):
        """Test update_graph creates nodes"""
        graph_widget.update_graph(sample_nodes)
        
        assert len(graph_widget.node_items) == len(sample_nodes)
        assert len(graph_widget.node_positions) == len(sample_nodes)
        
        for node in sample_nodes:
            assert node['id'] in graph_widget.node_items
            assert node['id'] in graph_widget.node_positions
    
    def test_update_graph_empty_list(self, graph_widget):
        """Test update_graph with empty list"""
        graph_widget.update_graph([])
        assert len(graph_widget.node_items) == 0
    
    def test_node_item_creation(self, qapp):
        """Test NodeItem creation"""
        node = NodeItem('test_node', 0, 0)
        assert node.node_id == 'test_node'
        assert node.label is not None
    
    def test_node_colors(self, graph_widget, sample_nodes):
        """Test node colors based on type"""
        graph_widget.update_graph(sample_nodes)
        
        # Validator - Blue
        validator = graph_widget.node_items['node_0']
        assert validator.brush().color().name() == '#2196f3'
        
        # Regular - Green
        regular = graph_widget.node_items['node_2']
        assert regular.brush().color().name() == '#4caf50'
        
        # Under attack - Yellow
        under_attack = graph_widget.node_items['node_3']
        assert under_attack.brush().color().name() == '#ffc107'
        
        # Sybil - Red
        sybil = graph_widget.node_items['node_4']
        assert sybil.brush().color().name() == '#f44336'
        
        # Byzantine - Orange
        byzantine = graph_widget.node_items['node_5']
        assert byzantine.brush().color().name() == '#ff9800'
    
    def test_edges_created(self, graph_widget, sample_nodes):
        """Test edges are created between nodes"""
        graph_widget.update_graph(sample_nodes)
        assert len(graph_widget.edge_items) > 0
    
    def test_edge_count_validators_only(self, graph_widget):
        """Test edge count with validators only - complete mesh"""
        # 3 validators = 3*(3-1)/2 = 3 edges
        validators = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v1', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v2', 'role': 'validator', 'status': 'healthy'},
        ]
        graph_widget.update_graph(validators)
        assert len(graph_widget.edge_items) == 3
    
    def test_edge_count_with_regulars(self, graph_widget):
        """Test edge count with validators and regular nodes"""
        nodes = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v1', 'role': 'validator', 'status': 'healthy'},
            {'id': 'r0', 'role': 'regular', 'status': 'healthy'},
            {'id': 'r1', 'role': 'regular', 'status': 'healthy'},
        ]
        graph_widget.update_graph(nodes)
        # 2 validators: 1 edge, 2 regulars to v0: 2 edges = 3 total
        assert len(graph_widget.edge_items) == 3
    
    def test_edge_z_order(self, graph_widget, sample_nodes):
        """Test edges are behind nodes (z-value = -1)"""
        graph_widget.update_graph(sample_nodes)
        for edge in graph_widget.edge_items:
            assert edge.zValue() == -1
    
    def test_edge_style(self, graph_widget, sample_nodes):
        """Test edge pen color and width"""
        graph_widget.update_graph(sample_nodes)
        for edge in graph_widget.edge_items:
            pen = edge.pen()
            assert pen.width() == 1
            assert pen.color().name() == '#3d3d3d'
    
    def test_edges_cleared_on_update(self, graph_widget, sample_nodes):
        """Test old edges are cleared when graph is updated"""
        graph_widget.update_graph(sample_nodes)
        initial_count = len(graph_widget.edge_items)
        
        fewer_nodes = sample_nodes[:3]
        graph_widget.update_graph(fewer_nodes)
        assert len(graph_widget.edge_items) != initial_count
    
    def test_no_edges_single_node(self, graph_widget):
        """Test no edges with single node"""
        single = [{'id': 'solo', 'role': 'validator', 'status': 'healthy'}]
        graph_widget.update_graph(single)
        assert len(graph_widget.edge_items) == 0
    
    def test_edges_in_scene(self, graph_widget, sample_nodes):
        """Test edges are added to scene"""
        graph_widget.update_graph(sample_nodes)
        scene_items = graph_widget.scene.items()
        for edge in graph_widget.edge_items:
            assert edge in scene_items
    
    def test_edges_connect_correct_nodes(self, graph_widget):
        """Test edges connect between correct positions"""
        nodes = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v1', 'role': 'validator', 'status': 'healthy'},
        ]
        graph_widget.update_graph(nodes)
        assert len(graph_widget.edge_items) == 1
        
        edge = graph_widget.edge_items[0]
        line = edge.line()
        v0_pos = graph_widget.node_positions['v0']
        v1_pos = graph_widget.node_positions['v1']
        
        # Edge endpoints match node positions
        assert (line.x1(), line.y1()) == v0_pos
        assert (line.x2(), line.y2()) == v1_pos
    
    def test_validator_mesh_topology(self, graph_widget):
        """Test validators form complete mesh"""
        validators = [
            {'id': f'v{i}', 'role': 'validator', 'status': 'healthy'}
            for i in range(4)
        ]
        graph_widget.update_graph(validators)
        # 4 validators: 4*3/2 = 6 edges
        assert len(graph_widget.edge_items) == 6
    
    def test_regular_to_validator_topology(self, graph_widget):
        """Test regular nodes connect to first validator"""
        nodes = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'r0', 'role': 'regular', 'status': 'healthy'},
            {'id': 'r1', 'role': 'regular', 'status': 'healthy'},
        ]
        graph_widget.update_graph(nodes)
        # 1 validator (0 v-v edges), 2 regulars to v0 = 2 edges
        assert len(graph_widget.edge_items) == 2
    
    def test_no_edges_regulars_only(self, graph_widget):
        """Test no edges when only regular nodes (no validators)"""
        regulars = [
            {'id': 'r0', 'role': 'regular', 'status': 'healthy'},
            {'id': 'r1', 'role': 'regular', 'status': 'healthy'},
        ]
        graph_widget.update_graph(regulars)
        # No validators = no edges
        assert len(graph_widget.edge_items) == 0
    
    def test_zoom_in(self, graph_widget):
        """Test zoom in"""
        initial_zoom = graph_widget.current_zoom
        graph_widget.zoom_in()
        assert graph_widget.current_zoom > initial_zoom
    
    def test_zoom_out(self, graph_widget):
        """Test zoom out"""
        graph_widget.zoom_in()  # Zoom in first
        initial_zoom = graph_widget.current_zoom
        graph_widget.zoom_out()
        assert graph_widget.current_zoom < initial_zoom
    
    def test_zoom_limits(self, graph_widget):
        """Test zoom limits"""
        # Zoom in to max
        for _ in range(20):
            graph_widget.zoom_in()
        assert graph_widget.current_zoom <= graph_widget.max_zoom
        
        # Reset
        graph_widget.reset_view()
        
        # Zoom out to min
        for _ in range(20):
            graph_widget.zoom_out()
        assert graph_widget.current_zoom >= graph_widget.min_zoom
    
    def test_fit_view(self, graph_widget, sample_nodes):
        """Test fit_view method"""
        graph_widget.update_graph(sample_nodes)
        graph_widget.zoom_in()
        graph_widget.fit_view()
        assert graph_widget.current_zoom == 1.0
    
    def test_reset_view(self, graph_widget, sample_nodes):
        """Test reset_view method"""
        graph_widget.update_graph(sample_nodes)
        graph_widget.zoom_in()
        initial_zoom = graph_widget.current_zoom
        graph_widget.reset_view()
        assert graph_widget.current_zoom == 1.0
    
    def test_highlight_node(self, graph_widget, sample_nodes):
        """Test highlight_node method"""
        graph_widget.update_graph(sample_nodes)
        graph_widget.highlight_node('node_0')
        
        selected_node = graph_widget.get_selected_node()
        assert selected_node == 'node_0'
    
    def test_get_selected_node_none(self, graph_widget):
        """Test get_selected_node with no selection"""
        assert graph_widget.get_selected_node() is None
    
    def test_node_clicked_signal(self, graph_widget):
        """Test node_clicked signal exists"""
        assert hasattr(graph_widget, 'node_clicked')
    
    def test_node_double_clicked_signal(self, graph_widget):
        """Test node_double_clicked signal exists"""
        assert hasattr(graph_widget, 'node_double_clicked')
    
    def test_node_tooltip(self, graph_widget, sample_nodes):
        """Test node tooltips contain data"""
        graph_widget.update_graph(sample_nodes)
        
        node_item = graph_widget.node_items['node_0']
        tooltip = node_item.toolTip()
        
        assert 'node_0' in tooltip
        assert 'validator' in tooltip.lower()
        assert 'healthy' in tooltip.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
