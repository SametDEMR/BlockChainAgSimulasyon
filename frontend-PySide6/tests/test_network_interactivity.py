"""
Tests for Network Graph Widget Interactivity (Milestone 4.6)
Tests for hover effects and node drag with edge updates
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication, QGraphicsSceneHoverEvent, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QMouseEvent, QColor
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
    """Sample node data for testing"""
    return [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy', 'response_time': 48, 'trust_score': 88},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy', 'response_time': 55},
    ]


class TestNodeHoverEffects:
    """Test suite for node hover effects"""
    
    def test_node_accepts_hover_events(self, qapp):
        """Test that NodeItem accepts hover events"""
        node = NodeItem('test_node', 0, 0)
        assert node.acceptHoverEvents()
    
    def test_hover_enter_increases_border_width(self, qapp):
        """Test border width increases on hover enter"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Get initial border width
        initial_width = node.pen().width()
        
        # Simulate hover enter
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        # Border should be thicker on hover
        hover_width = node.pen().width()
        assert hover_width > initial_width
    
    def test_hover_leave_restores_border_width(self, qapp):
        """Test border width restores on hover leave"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Get initial width
        initial_width = node.pen().width()
        
        # Hover enter then leave
        enter_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(enter_event)
        
        leave_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverLeave)
        node.hoverLeaveEvent(leave_event)
        
        # Should return to initial width
        final_width = node.pen().width()
        assert final_width == initial_width
    
    def test_hover_enter_changes_border_color(self, qapp):
        """Test border color changes on hover enter"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Get initial color
        initial_color = node.pen().color()
        
        # Simulate hover enter
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        # Color should change (lighter/brighter)
        hover_color = node.pen().color()
        assert hover_color != initial_color
    
    def test_hover_leave_restores_border_color(self, qapp):
        """Test border color restores on hover leave"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Get initial color
        initial_color = node.pen().color().name()
        
        # Hover enter then leave
        enter_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(enter_event)
        
        leave_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverLeave)
        node.hoverLeaveEvent(leave_event)
        
        # Should return to initial color
        final_color = node.pen().color().name()
        assert final_color == initial_color
    
    def test_hover_effect_validator_node(self, qapp):
        """Test hover effect works on validator nodes"""
        node = NodeItem('validator', 0, 0)
        node_data = {'id': 'validator', 'role': 'validator', 'status': 'healthy'}
        node.update_style(node_data)
        
        initial_width = node.pen().width()
        
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        assert node.pen().width() > initial_width
    
    def test_hover_effect_sybil_node(self, qapp):
        """Test hover effect works on sybil nodes"""
        node = NodeItem('sybil', 0, 0)
        node_data = {'id': 'sybil', 'role': 'regular', 'status': 'healthy', 'is_sybil': True}
        node.update_style(node_data)
        
        initial_width = node.pen().width()
        
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        assert node.pen().width() > initial_width
    
    def test_hover_effect_under_attack_node(self, qapp):
        """Test hover effect works on nodes under attack"""
        node = NodeItem('attacked', 0, 0)
        node_data = {'id': 'attacked', 'role': 'regular', 'status': 'under_attack'}
        node.update_style(node_data)
        
        initial_width = node.pen().width()
        
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        assert node.pen().width() > initial_width
    
    def test_multiple_hover_cycles(self, qapp):
        """Test multiple hover enter/leave cycles"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        initial_width = node.pen().width()
        
        # Multiple hover cycles
        for _ in range(3):
            enter_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
            node.hoverEnterEvent(enter_event)
            
            leave_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverLeave)
            node.hoverLeaveEvent(leave_event)
        
        # Should still return to initial width
        assert node.pen().width() == initial_width
    
    def test_hover_with_selection(self, qapp):
        """Test hover effect works when node is selected"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Select node
        node.setSelected(True)
        node.update_style(node_data)
        
        selected_width = node.pen().width()
        
        # Hover should still increase width
        event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(event)
        
        hover_width = node.pen().width()
        assert hover_width >= selected_width  # Should be at least same or thicker


class TestNodeDragWithEdgeUpdate:
    """Test suite for node dragging with edge updates"""
    
    def test_node_is_movable(self, qapp):
        """Test that NodeItem is movable"""
        node = NodeItem('test_node', 0, 0)
        assert node.flags() & QGraphicsItem.ItemIsMovable
    
    def test_edges_update_on_node_move(self, graph_widget, sample_nodes):
        """Test edges update their positions when node moves"""
        graph_widget.update_graph(sample_nodes)
        
        # Get a node and its initial position
        node_item = graph_widget.node_items['node_0']
        initial_pos = node_item.pos()
        
        # Get initial edge positions
        initial_edge_positions = []
        for edge in graph_widget.edge_items:
            initial_edge_positions.append((edge.line().x1(), edge.line().y1(), 
                                          edge.line().x2(), edge.line().y2()))
        
        # Move node
        new_pos = QPointF(initial_pos.x() + 100, initial_pos.y() + 100)
        node_item.setPos(new_pos)
        
        # Trigger edge update
        graph_widget.update_edges_for_node('node_0')
        
        # Get new edge positions
        new_edge_positions = []
        for edge in graph_widget.edge_items:
            new_edge_positions.append((edge.line().x1(), edge.line().y1(), 
                                      edge.line().x2(), edge.line().y2()))
        
        # At least one edge should have moved
        assert initial_edge_positions != new_edge_positions
    
    def test_only_connected_edges_update(self, graph_widget, sample_nodes):
        """Test only edges connected to moved node update"""
        graph_widget.update_graph(sample_nodes)
        
        # Move node_2 (regular node, only connected to validators)
        node_item = graph_widget.node_items['node_2']
        initial_pos = node_item.pos()
        
        # Get edges connected to node_2
        connected_edges = graph_widget.get_edges_for_node('node_2')
        other_edges = [e for e in graph_widget.edge_items if e not in connected_edges]
        
        # Store other edge positions
        other_edge_positions = []
        for edge in other_edges:
            other_edge_positions.append((edge.line().x1(), edge.line().y1(),
                                        edge.line().x2(), edge.line().y2()))
        
        # Move node
        new_pos = QPointF(initial_pos.x() + 50, initial_pos.y() + 50)
        node_item.setPos(new_pos)
        graph_widget.update_edges_for_node('node_2')
        
        # Check other edges didn't move
        for i, edge in enumerate(other_edges):
            current_pos = (edge.line().x1(), edge.line().y1(),
                          edge.line().x2(), edge.line().y2())
            assert current_pos == other_edge_positions[i]
    
    def test_edge_update_reflects_new_node_position(self, graph_widget):
        """Test edge endpoints match new node position after move"""
        nodes = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v1', 'role': 'validator', 'status': 'healthy'},
        ]
        graph_widget.update_graph(nodes)
        
        # Move v0
        node_item = graph_widget.node_items['v0']
        new_pos = QPointF(200, 200)
        node_item.setPos(new_pos)
        
        # Update edges
        graph_widget.update_edges_for_node('v0')
        
        # Check edge connects to new position
        edge = graph_widget.edge_items[0]
        line = edge.line()
        
        # One end should be at (200, 200)
        assert (line.x1() == 200 and line.y1() == 200) or \
               (line.x2() == 200 and line.y2() == 200)
    
    def test_multiple_node_moves(self, graph_widget, sample_nodes):
        """Test moving multiple nodes updates all affected edges"""
        graph_widget.update_graph(sample_nodes)
        
        # Move two validator nodes
        for node_id in ['node_0', 'node_1']:
            node_item = graph_widget.node_items[node_id]
            current_pos = node_item.pos()
            new_pos = QPointF(current_pos.x() + 75, current_pos.y() + 75)
            node_item.setPos(new_pos)
            graph_widget.update_edges_for_node(node_id)
        
        # All edges should reflect new positions
        for node_id in ['node_0', 'node_1']:
            node_pos = graph_widget.node_items[node_id].pos()
            edges = graph_widget.get_edges_for_node(node_id)
            
            for edge in edges:
                line = edge.line()
                # At least one endpoint should match node position
                matches = (line.x1() == node_pos.x() and line.y1() == node_pos.y()) or \
                         (line.x2() == node_pos.x() and line.y2() == node_pos.y())
                assert matches
    
    def test_edge_update_method_exists(self, graph_widget):
        """Test update_edges_for_node method exists"""
        assert hasattr(graph_widget, 'update_edges_for_node')
    
    def test_get_edges_for_node_method_exists(self, graph_widget):
        """Test get_edges_for_node method exists"""
        assert hasattr(graph_widget, 'get_edges_for_node')
    
    def test_get_edges_for_node_returns_list(self, graph_widget, sample_nodes):
        """Test get_edges_for_node returns list"""
        graph_widget.update_graph(sample_nodes)
        edges = graph_widget.get_edges_for_node('node_0')
        assert isinstance(edges, list)
    
    def test_get_edges_for_validator(self, graph_widget, sample_nodes):
        """Test get edges for validator node (should have multiple edges)"""
        graph_widget.update_graph(sample_nodes)
        edges = graph_widget.get_edges_for_node('node_0')
        # Validator should connect to other validators
        assert len(edges) > 0
    
    def test_get_edges_for_regular_node(self, graph_widget, sample_nodes):
        """Test get edges for regular node"""
        graph_widget.update_graph(sample_nodes)
        edges = graph_widget.get_edges_for_node('node_2')
        # Regular node connects to first validator
        assert len(edges) >= 1
    
    def test_get_edges_nonexistent_node(self, graph_widget, sample_nodes):
        """Test get edges for nonexistent node returns empty list"""
        graph_widget.update_graph(sample_nodes)
        edges = graph_widget.get_edges_for_node('nonexistent')
        assert edges == []
    
    def test_edge_tracking_data_structure(self, graph_widget, sample_nodes):
        """Test widget maintains edge-to-node mapping"""
        graph_widget.update_graph(sample_nodes)
        
        # Widget should track which nodes each edge connects
        assert hasattr(graph_widget, 'edge_connections')
        assert isinstance(graph_widget.edge_connections, dict)
    
    def test_edge_connections_created_on_update(self, graph_widget, sample_nodes):
        """Test edge_connections dict is populated on graph update"""
        graph_widget.update_graph(sample_nodes)
        
        # Should have entries for created edges
        assert len(graph_widget.edge_connections) == len(graph_widget.edge_items)
    
    def test_edge_connection_format(self, graph_widget):
        """Test edge_connections stores node pairs correctly"""
        nodes = [
            {'id': 'v0', 'role': 'validator', 'status': 'healthy'},
            {'id': 'v1', 'role': 'validator', 'status': 'healthy'},
        ]
        graph_widget.update_graph(nodes)
        
        edge = graph_widget.edge_items[0]
        connection = graph_widget.edge_connections[edge]
        
        # Should be tuple of two node IDs
        assert isinstance(connection, tuple)
        assert len(connection) == 2
        assert 'v0' in connection and 'v1' in connection
    
    def test_node_move_triggers_automatic_edge_update(self, graph_widget, sample_nodes):
        """Test that moving node automatically triggers edge update"""
        graph_widget.update_graph(sample_nodes)
        
        node_item = graph_widget.node_items['node_0']
        
        # Get initial edge positions
        edges = graph_widget.get_edges_for_node('node_0')
        initial_positions = [(e.line().x1(), e.line().y1(), e.line().x2(), e.line().y2()) 
                            for e in edges]
        
        # Move node (this should trigger itemChange which updates edges)
        new_pos = QPointF(300, 300)
        node_item.setPos(new_pos)
        
        # Force process events
        QApplication.processEvents()
        
        # Edges should have updated
        new_positions = [(e.line().x1(), e.line().y1(), e.line().x2(), e.line().y2()) 
                        for e in edges]
        
        # At least one edge should have different position
        assert initial_positions != new_positions


class TestInteractivityIntegration:
    """Test suite for integrated interactivity features"""
    
    def test_hover_while_dragging(self, qapp):
        """Test hover effect persists during drag"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Simulate hover
        hover_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(hover_event)
        
        hover_width = node.pen().width()
        
        # Move node
        node.setPos(50, 50)
        
        # Hover effect should still be active
        assert node.pen().width() == hover_width
    
    def test_selection_and_hover_combination(self, qapp):
        """Test selection and hover work together"""
        node = NodeItem('test_node', 0, 0)
        node_data = {'id': 'test_node', 'role': 'regular', 'status': 'healthy'}
        node.update_style(node_data)
        
        # Select node
        node.setSelected(True)
        node.update_style(node_data)
        selected_width = node.pen().width()
        
        # Hover on selected node
        hover_event = QGraphicsSceneHoverEvent(QEvent.GraphicsSceneHoverEnter)
        node.hoverEnterEvent(hover_event)
        
        # Should have hover effect on top of selection
        assert node.pen().width() >= selected_width
    
    def test_clear_graph_resets_edge_connections(self, graph_widget, sample_nodes):
        """Test clearing graph resets edge connection tracking"""
        graph_widget.update_graph(sample_nodes)
        assert len(graph_widget.edge_connections) > 0
        
        graph_widget.clear_graph()
        assert len(graph_widget.edge_connections) == 0
    
    def test_update_graph_recreates_edge_connections(self, graph_widget, sample_nodes):
        """Test updating graph recreates edge connections"""
        graph_widget.update_graph(sample_nodes)
        initial_count = len(graph_widget.edge_connections)
        
        # Update with different nodes
        new_nodes = sample_nodes[:2]
        graph_widget.update_graph(new_nodes)
        
        # Should have new edge connections
        assert len(graph_widget.edge_connections) != initial_count


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
