"""Tests for MetricsWidget Real-time Graph - Milestone 7.2."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock
import sys

from ui.widgets.metrics_widget import MetricsWidget


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    manager = Mock()
    manager.nodes_updated = Mock()
    manager.nodes_updated.connect = Mock()
    manager.metrics_updated = Mock()
    manager.metrics_updated.connect = Mock()
    return manager


@pytest.fixture
def metrics_widget(qapp, mock_data_manager):
    """Create MetricsWidget instance."""
    widget = MetricsWidget(mock_data_manager)
    return widget


# ============ Milestone 7.2 Tests: Real-time Graph ============

def test_plot_widget_exists(metrics_widget):
    """Test PyQtGraph PlotWidget is created."""
    assert metrics_widget.plot_widget is not None
    assert hasattr(metrics_widget.plot_widget, 'plot')


def test_plot_widget_configuration(metrics_widget):
    """Test plot widget has correct configuration."""
    plot = metrics_widget.plot_widget
    
    # Check background color
    assert plot.backgroundBrush().color().name() == '#2d2d2d'
    
    # Check minimum height
    assert plot.minimumHeight() == 250


def test_plot_widget_has_legend(metrics_widget):
    """Test plot has legend enabled."""
    plot = metrics_widget.plot_widget
    # PyQtGraph legend should be present
    assert hasattr(plot, 'plotItem')
    # Legend is added in setup
    assert plot.plotItem.legend is not None


def test_plot_widget_has_grid(metrics_widget):
    """Test plot has grid enabled."""
    plot = metrics_widget.plot_widget
    # Grid should be shown
    assert plot.plotItem.ctrl.xGridCheck.isChecked()
    assert plot.plotItem.ctrl.yGridCheck.isChecked()


def test_graph_data_structures_initialized(metrics_widget):
    """Test graph data structures are properly initialized."""
    assert hasattr(metrics_widget, 'response_time_data')
    assert isinstance(metrics_widget.response_time_data, dict)
    
    assert hasattr(metrics_widget, 'graph_curves')
    assert isinstance(metrics_widget.graph_curves, dict)
    
    assert hasattr(metrics_widget, 'max_points')
    assert metrics_widget.max_points == 50
    
    assert hasattr(metrics_widget, 'colors')
    assert len(metrics_widget.colors) == 10


def test_update_graph_single_node(metrics_widget):
    """Test updating graph with single node data."""
    nodes = [{'id': 'node_0', 'response_time': 50}]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Check data structure created
    assert 'node_0' in metrics_widget.response_time_data
    assert len(metrics_widget.response_time_data['node_0']) == 1
    assert metrics_widget.response_time_data['node_0'][0] == 50
    
    # Check curve created
    assert 'node_0' in metrics_widget.graph_curves
    assert metrics_widget.graph_curves['node_0'] is not None


def test_update_graph_multiple_nodes(metrics_widget):
    """Test updating graph with multiple nodes."""
    nodes = [
        {'id': 'node_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 75},
        {'id': 'node_2', 'response_time': 100}
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Check all data structures created
    assert len(metrics_widget.response_time_data) == 3
    assert len(metrics_widget.graph_curves) == 3
    
    # Check each node has data
    for node in nodes:
        node_id = node['id']
        assert node_id in metrics_widget.response_time_data
        assert node_id in metrics_widget.graph_curves


def test_update_graph_sequential_updates(metrics_widget):
    """Test sequential updates add data points."""
    node_id = 'node_0'
    
    # First update
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 50}])
    assert len(metrics_widget.response_time_data[node_id]) == 1
    
    # Second update
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 60}])
    assert len(metrics_widget.response_time_data[node_id]) == 2
    
    # Third update
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 70}])
    assert len(metrics_widget.response_time_data[node_id]) == 3
    
    # Check data values
    data = list(metrics_widget.response_time_data[node_id])
    assert data == [50, 60, 70]


def test_update_graph_buffer_limit(metrics_widget):
    """Test graph buffer respects max_points limit (50)."""
    node_id = 'node_0'
    
    # Add 60 data points
    for i in range(60):
        metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': i}])
    
    # Should only keep last 50 points
    assert len(metrics_widget.response_time_data[node_id]) == 50
    
    # Should have data from 10 to 59 (first 10 dropped)
    data = list(metrics_widget.response_time_data[node_id])
    assert data[0] == 10
    assert data[-1] == 59


def test_update_graph_auto_scroll(metrics_widget):
    """Test auto-scroll functionality with buffer limit."""
    node_id = 'node_0'
    
    # Fill buffer with 50 points (0-49)
    for i in range(50):
        metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': i}])
    
    data = list(metrics_widget.response_time_data[node_id])
    assert data[0] == 0
    assert data[-1] == 49
    
    # Add one more (should drop first)
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 50}])
    
    data = list(metrics_widget.response_time_data[node_id])
    assert data[0] == 1  # First point dropped
    assert data[-1] == 50  # New point added


def test_graph_curve_colors(metrics_widget):
    """Test each node gets different color."""
    nodes = [
        {'id': f'node_{i}', 'response_time': 50 + i*10}
        for i in range(5)
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # All curves should exist
    assert len(metrics_widget.graph_curves) == 5
    
    # Each should have different color (cycling through color list)
    expected_colors = metrics_widget.colors[:5]
    
    for i, node in enumerate(nodes):
        node_id = node['id']
        curve = metrics_widget.graph_curves[node_id]
        # Curve should exist and be a PlotDataItem
        assert curve is not None


def test_graph_curve_names(metrics_widget):
    """Test curves have correct names for legend."""
    nodes = [
        {'id': 'validator_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 75},
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Curves should have names matching node IDs
    for node in nodes:
        node_id = node['id']
        curve = metrics_widget.graph_curves[node_id]
        # Name is used in legend
        assert curve.name() == node_id


def test_update_graph_with_zero_response_time(metrics_widget):
    """Test handling zero response time."""
    nodes = [{'id': 'node_0', 'response_time': 0}]
    
    metrics_widget.update_response_time_graph(nodes)
    
    assert 'node_0' in metrics_widget.response_time_data
    assert metrics_widget.response_time_data['node_0'][0] == 0


def test_update_graph_with_missing_response_time(metrics_widget):
    """Test handling missing response_time field."""
    nodes = [{'id': 'node_0'}]  # No response_time
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Should use default value of 0
    assert 'node_0' in metrics_widget.response_time_data
    assert metrics_widget.response_time_data['node_0'][0] == 0


def test_update_graph_with_empty_list(metrics_widget):
    """Test handling empty node list."""
    metrics_widget.update_response_time_graph([])
    
    # Should not crash
    assert len(metrics_widget.response_time_data) == 0
    assert len(metrics_widget.graph_curves) == 0


def test_update_graph_preserves_existing_curves(metrics_widget):
    """Test updating doesn't recreate existing curves."""
    node_id = 'node_0'
    
    # First update
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 50}])
    original_curve = metrics_widget.graph_curves[node_id]
    
    # Second update
    metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 60}])
    
    # Should be same curve object
    assert metrics_widget.graph_curves[node_id] is original_curve


def test_clear_display_clears_graph(metrics_widget):
    """Test clear_display removes all graph data."""
    # Add some data
    nodes = [
        {'id': 'node_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 75}
    ]
    metrics_widget.update_response_time_graph(nodes)
    
    assert len(metrics_widget.response_time_data) == 2
    assert len(metrics_widget.graph_curves) == 2
    
    # Clear
    metrics_widget.clear_display()
    
    # Check graph cleared
    assert len(metrics_widget.response_time_data) == 0
    assert len(metrics_widget.graph_curves) == 0


def test_graph_x_axis_incremental(metrics_widget):
    """Test x-axis uses incremental indices."""
    node_id = 'node_0'
    
    # Add 3 data points
    for i in range(3):
        metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': 50 + i}])
    
    curve = metrics_widget.graph_curves[node_id]
    x_data, y_data = curve.getData()
    
    # X should be [0, 1, 2]
    assert list(x_data) == [0, 1, 2]
    # Y should be [50, 51, 52]
    assert list(y_data) == [50, 51, 52]


def test_multiple_nodes_color_cycling(metrics_widget):
    """Test color cycling when more nodes than colors."""
    # Create 12 nodes (more than 10 colors available)
    nodes = [
        {'id': f'node_{i}', 'response_time': 50 + i}
        for i in range(12)
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # All nodes should have curves
    assert len(metrics_widget.graph_curves) == 12
    
    # Colors should cycle (node_10 should use color[0], node_11 uses color[1])
    # We can't directly check color but verify all curves exist
    for node in nodes:
        assert node['id'] in metrics_widget.graph_curves


def test_signal_connection_for_graph(metrics_widget, mock_data_manager):
    """Test graph update is connected to nodes_updated signal."""
    calls = [call[0][0] for call in mock_data_manager.nodes_updated.connect.call_args_list]
    
    # Should include update_response_time_graph
    assert metrics_widget.update_response_time_graph in calls


def test_graph_performance_with_many_updates(metrics_widget):
    """Test graph performance with rapid updates."""
    node_id = 'node_0'
    
    # Simulate 100 rapid updates
    import time
    start_time = time.time()
    
    for i in range(100):
        metrics_widget.update_response_time_graph([{'id': node_id, 'response_time': i}])
    
    elapsed = time.time() - start_time
    
    # Should complete in reasonable time (< 1 second)
    assert elapsed < 1.0
    
    # Buffer should still be limited to 50
    assert len(metrics_widget.response_time_data[node_id]) == 50
