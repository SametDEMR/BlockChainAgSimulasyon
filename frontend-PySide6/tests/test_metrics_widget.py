"""Tests for MetricsWidget."""
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


def test_update_health_with_empty_nodes(metrics_widget):
    """Test update_health with empty node list."""
    metrics_widget.update_health([])
    # Should not crash
    assert metrics_widget.overall_health.value() == 0


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
    
    # Overall: 5/6 = 83%
    assert metrics_widget.overall_health.value() == 83
    
    # Validators: 3/4 = 75%
    assert metrics_widget.validators_health.value() == 75
    
    # Regular: 2/2 = 100%
    assert metrics_widget.regular_health.value() == 100


def test_update_metrics_with_empty_data(metrics_widget):
    """Test update_metrics with empty data."""
    metrics_widget.update_metrics({})
    # Should not crash, labels should show default
    assert metrics_widget.blocks_per_min.text() == "0"


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


def test_clear_display(metrics_widget):
    """Test clear_display resets all values."""
    # Set some values
    metrics_widget.overall_health.setValue(50)
    metrics_widget.blocks_per_min.setText("10")
    
    # Clear
    metrics_widget.clear_display()
    
    # Check all reset
    assert metrics_widget.overall_health.value() == 0
    assert metrics_widget.validators_health.value() == 0
    assert metrics_widget.regular_health.value() == 0
    assert metrics_widget.blocks_per_min.text() == "0"
    assert metrics_widget.tx_per_sec.text() == "0.0"
    assert metrics_widget.avg_block_time.text() == "0.0s"


def test_widget_without_data_manager(qapp):
    """Test widget can be created without data manager."""
    widget = MetricsWidget(data_manager=None)
    assert widget is not None
    assert widget.data_manager is None


def test_signal_connections_setup(metrics_widget, mock_data_manager):
    """Test signals are connected to data manager."""
    # Verify connect was called
    assert mock_data_manager.nodes_updated.connect.called
    assert mock_data_manager.metrics_updated.connect.called
