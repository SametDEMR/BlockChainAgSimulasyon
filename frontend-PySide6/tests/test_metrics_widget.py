"""Tests for MetricsWidget - Updated for Milestone 2.2."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, MagicMock
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


# ============ Milestone 2.1 Tests ============

def test_metrics_widget_creation(metrics_widget):
    """Test widget is created successfully."""
    assert metrics_widget is not None
    assert metrics_widget.data_manager is not None


def test_metrics_widget_has_sections(metrics_widget):
    """Test widget has all required sections."""
    assert metrics_widget.graph_section is not None
    assert metrics_widget.cards_section is not None
    assert metrics_widget.health_section is not None
    assert metrics_widget.metrics_section is not None


def test_health_bars_exist(metrics_widget):
    """Test health progress bars exist."""
    assert metrics_widget.overall_health is not None
    assert metrics_widget.validators_health is not None
    assert metrics_widget.regular_health is not None


def test_metrics_labels_exist(metrics_widget):
    """Test system metrics labels exist."""
    assert metrics_widget.blocks_per_min is not None
    assert metrics_widget.tx_per_sec is not None
    assert metrics_widget.avg_block_time is not None


def test_update_health_with_nodes(metrics_widget):
    """Test update_health with node data."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'node_3', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_4', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_5', 'role': 'regular', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    assert metrics_widget.overall_health.value() == 83
    assert metrics_widget.validators_health.value() == 75
    assert metrics_widget.regular_health.value() == 100


def test_update_metrics_with_data(metrics_widget):
    """Test update_metrics with actual data."""
    metrics = {
        'blocks_per_minute': 12,
        'transactions_per_second': 5.2,
        'average_block_time': 5.1
    }
    
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.blocks_per_min.text() == "12"
    assert metrics_widget.tx_per_sec.text() == "5.2"
    assert metrics_widget.avg_block_time.text() == "5.1s"


# ============ Milestone 2.2 Tests (PyQtGraph) ============

def test_plot_widget_exists(metrics_widget):
    """Test PyQtGraph PlotWidget is created."""
    assert metrics_widget.plot_widget is not None
    assert hasattr(metrics_widget.plot_widget, 'plot')


def test_graph_data_structures(metrics_widget):
    """Test graph data structures are initialized."""
    assert metrics_widget.response_time_data == {}
    assert metrics_widget.graph_curves == {}
    assert metrics_widget.max_points == 50
    assert len(metrics_widget.colors) == 10


def test_update_response_time_single_node(metrics_widget):
    """Test updating response time for a single node."""
    nodes = [
        {'id': 'node_0', 'response_time': 50}
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Check data structure
    assert 'node_0' in metrics_widget.response_time_data
    assert len(metrics_widget.response_time_data['node_0']) == 1
    assert metrics_widget.response_time_data['node_0'][0] == 50
    
    # Check curve created
    assert 'node_0' in metrics_widget.graph_curves


def test_update_response_time_multiple_updates(metrics_widget):
    """Test multiple updates accumulate data."""
    nodes = [{'id': 'node_0', 'response_time': 50}]
    
    # First update
    metrics_widget.update_response_time_graph(nodes)
    
    # Second update
    nodes = [{'id': 'node_0', 'response_time': 60}]
    metrics_widget.update_response_time_graph(nodes)
    
    # Third update
    nodes = [{'id': 'node_0', 'response_time': 55}]
    metrics_widget.update_response_time_graph(nodes)
    
    # Check accumulated data
    assert len(metrics_widget.response_time_data['node_0']) == 3
    assert list(metrics_widget.response_time_data['node_0']) == [50, 60, 55]


def test_update_response_time_multiple_nodes(metrics_widget):
    """Test handling multiple nodes simultaneously."""
    nodes = [
        {'id': 'node_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 45},
        {'id': 'node_2', 'response_time': 70},
    ]
    
    metrics_widget.update_response_time_graph(nodes)
    
    # Check all nodes have data
    assert 'node_0' in metrics_widget.response_time_data
    assert 'node_1' in metrics_widget.response_time_data
    assert 'node_2' in metrics_widget.response_time_data
    
    # Check all nodes have curves
    assert len(metrics_widget.graph_curves) == 3


def test_response_time_max_points_limit(metrics_widget):
    """Test data is limited to max_points (50)."""
    nodes = [{'id': 'node_0', 'response_time': 50}]
    
    # Add 60 data points
    for i in range(60):
        nodes[0]['response_time'] = 50 + i
        metrics_widget.update_response_time_graph(nodes)
    
    # Should only keep last 50
    assert len(metrics_widget.response_time_data['node_0']) == 50
    
    # Should have latest values (10 to 59)
    data_list = list(metrics_widget.response_time_data['node_0'])
    assert data_list[0] == 60  # First value: 50 + 10
    assert data_list[-1] == 109  # Last value: 50 + 59


def test_update_response_time_with_empty_list(metrics_widget):
    """Test handling empty node list."""
    metrics_widget.update_response_time_graph([])
    # Should not crash
    assert len(metrics_widget.response_time_data) == 0


def test_clear_display_clears_graph(metrics_widget):
    """Test clear_display also clears graph data."""
    # Add some data
    nodes = [
        {'id': 'node_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 60}
    ]
    metrics_widget.update_response_time_graph(nodes)
    
    # Clear
    metrics_widget.clear_display()
    
    # Check graph data cleared
    assert len(metrics_widget.response_time_data) == 0
    assert len(metrics_widget.graph_curves) == 0


def test_signal_connections_for_graph(metrics_widget, mock_data_manager):
    """Test graph update is connected to nodes_updated signal."""
    # Verify connect was called for graph update
    calls = [call[0][0] for call in mock_data_manager.nodes_updated.connect.call_args_list]
    
    # Should have both update_health and update_response_time_graph
    assert len(calls) == 2
    assert metrics_widget.update_health in calls
    assert metrics_widget.update_response_time_graph in calls
