"""Tests for Network Health Bars - Milestone 7.4."""
import pytest
from PySide6.QtWidgets import QApplication, QProgressBar
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


# ============ Milestone 7.4 Tests: Network Health Bars ============

def test_health_bars_exist(metrics_widget):
    """Test all three health bars are created."""
    assert hasattr(metrics_widget, 'overall_health')
    assert hasattr(metrics_widget, 'validators_health')
    assert hasattr(metrics_widget, 'regular_health')
    
    assert isinstance(metrics_widget.overall_health, QProgressBar)
    assert isinstance(metrics_widget.validators_health, QProgressBar)
    assert isinstance(metrics_widget.regular_health, QProgressBar)


def test_health_bars_range(metrics_widget):
    """Test health bars have 0-100 range."""
    assert metrics_widget.overall_health.minimum() == 0
    assert metrics_widget.overall_health.maximum() == 100
    
    assert metrics_widget.validators_health.minimum() == 0
    assert metrics_widget.validators_health.maximum() == 100
    
    assert metrics_widget.regular_health.minimum() == 0
    assert metrics_widget.regular_health.maximum() == 100


def test_health_bars_initial_value(metrics_widget):
    """Test health bars start at 0."""
    assert metrics_widget.overall_health.value() == 0
    assert metrics_widget.validators_health.value() == 0
    assert metrics_widget.regular_health.value() == 0


def test_health_bars_format(metrics_widget):
    """Test health bars show percentage format."""
    assert metrics_widget.overall_health.format() == "%p%"
    assert metrics_widget.validators_health.format() == "%p%"
    assert metrics_widget.regular_health.format() == "%p%"


def test_update_health_all_healthy(metrics_widget):
    """Test health bars with all nodes healthy."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_3', 'role': 'regular', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    assert metrics_widget.overall_health.value() == 100
    assert metrics_widget.validators_health.value() == 100
    assert metrics_widget.regular_health.value() == 100


def test_update_health_partial_healthy(metrics_widget):
    """Test health bars with some unhealthy nodes."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_3', 'role': 'regular', 'status': 'under_attack'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Overall: 2/4 = 50%
    assert metrics_widget.overall_health.value() == 50
    # Validators: 1/2 = 50%
    assert metrics_widget.validators_health.value() == 50
    # Regular: 1/2 = 50%
    assert metrics_widget.regular_health.value() == 50


def test_update_health_all_under_attack(metrics_widget):
    """Test health bars with all nodes under attack."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'node_1', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'node_2', 'role': 'regular', 'status': 'under_attack'},
    ]
    
    metrics_widget.update_health(nodes)
    
    assert metrics_widget.overall_health.value() == 0
    assert metrics_widget.validators_health.value() == 0
    assert metrics_widget.regular_health.value() == 0


def test_update_health_only_validators(metrics_widget):
    """Test health bars with only validator nodes."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'validator', 'status': 'under_attack'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Overall: 2/3 = 66%
    assert metrics_widget.overall_health.value() == 66
    # Validators: 2/3 = 66%
    assert metrics_widget.validators_health.value() == 66
    # Regular: 0 nodes = 0%
    assert metrics_widget.regular_health.value() == 0


def test_update_health_only_regular(metrics_widget):
    """Test health bars with only regular nodes."""
    nodes = [
        {'id': 'node_0', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'regular', 'status': 'under_attack'},
        {'id': 'node_3', 'role': 'regular', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Overall: 3/4 = 75%
    assert metrics_widget.overall_health.value() == 75
    # Validators: 0 nodes = 0%
    assert metrics_widget.validators_health.value() == 0
    # Regular: 3/4 = 75%
    assert metrics_widget.regular_health.value() == 75


def test_update_health_recovering_status(metrics_widget):
    """Test recovering status is counted as unhealthy."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'recovering'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Recovering is not healthy, so 1/2 = 50%
    assert metrics_widget.validators_health.value() == 50


def test_update_health_empty_list(metrics_widget):
    """Test handling empty node list."""
    metrics_widget.update_health([])
    
    # Should not crash, values should remain at previous state
    # Since initial state is 0, they should stay 0
    assert metrics_widget.overall_health.value() == 0


def test_update_health_missing_status(metrics_widget):
    """Test nodes without status field."""
    nodes = [
        {'id': 'node_0', 'role': 'validator'},  # Missing status
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Only one node has healthy status, 1/2 = 50%
    assert metrics_widget.validators_health.value() == 50


def test_update_health_missing_role(metrics_widget):
    """Test nodes without role field."""
    nodes = [
        {'id': 'node_0', 'status': 'healthy'},  # Missing role (defaults to regular)
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Overall should be 100% (both healthy)
    assert metrics_widget.overall_health.value() == 100


def test_update_health_percentages_rounded(metrics_widget):
    """Test health percentages are properly rounded."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'validator', 'status': 'under_attack'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # 2/3 = 66.666... should round to 66
    assert metrics_widget.validators_health.value() == 66


def test_update_health_one_of_ten(metrics_widget):
    """Test calculation with 1 out of 10 healthy."""
    nodes = [
        {'id': f'node_{i}', 'role': 'regular', 'status': 'under_attack'}
        for i in range(9)
    ]
    nodes.append({'id': 'node_9', 'role': 'regular', 'status': 'healthy'})
    
    metrics_widget.update_health(nodes)
    
    # 1/10 = 10%
    assert metrics_widget.regular_health.value() == 10


def test_update_health_nine_of_ten(metrics_widget):
    """Test calculation with 9 out of 10 healthy."""
    nodes = [
        {'id': f'node_{i}', 'role': 'regular', 'status': 'healthy'}
        for i in range(9)
    ]
    nodes.append({'id': 'node_9', 'role': 'regular', 'status': 'under_attack'})
    
    metrics_widget.update_health(nodes)
    
    # 9/10 = 90%
    assert metrics_widget.regular_health.value() == 90


def test_health_bars_styled(metrics_widget):
    """Test health bars have custom styling applied."""
    # Check that progress bars have custom style
    assert metrics_widget.overall_health.styleSheet() != ""
    assert metrics_widget.validators_health.styleSheet() != ""
    assert metrics_widget.regular_health.styleSheet() != ""


def test_health_bars_background_color(metrics_widget):
    """Test progress bars have dark background."""
    style = metrics_widget.overall_health.styleSheet()
    assert '#2D2D2D' in style  # Dark background


def test_health_bars_chunk_color(metrics_widget):
    """Test progress bars have green chunk color."""
    style = metrics_widget.overall_health.styleSheet()
    assert '#4CAF50' in style  # Green chunk


def test_health_bars_border(metrics_widget):
    """Test progress bars have border styling."""
    style = metrics_widget.overall_health.styleSheet()
    assert 'border' in style.lower()


def test_health_bars_border_radius(metrics_widget):
    """Test progress bars have rounded corners."""
    style = metrics_widget.overall_health.styleSheet()
    assert 'border-radius' in style.lower()


def test_health_bars_height(metrics_widget):
    """Test progress bars have specified height."""
    style = metrics_widget.overall_health.styleSheet()
    assert 'height' in style.lower()


def test_signal_connection_for_health(metrics_widget, mock_data_manager):
    """Test health update is connected to nodes_updated signal."""
    calls = [call[0][0] for call in mock_data_manager.nodes_updated.connect.call_args_list]
    assert metrics_widget.update_health in calls


def test_clear_display_resets_health_bars(metrics_widget):
    """Test clear_display resets health bars to 0."""
    # Set some values
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
    ]
    metrics_widget.update_health(nodes)
    
    assert metrics_widget.overall_health.value() == 100
    
    # Clear
    metrics_widget.clear_display()
    
    # Should reset to 0
    assert metrics_widget.overall_health.value() == 0
    assert metrics_widget.validators_health.value() == 0
    assert metrics_widget.regular_health.value() == 0


def test_update_health_multiple_times(metrics_widget):
    """Test multiple updates to health bars."""
    # First update - all healthy
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
    ]
    metrics_widget.update_health(nodes)
    assert metrics_widget.validators_health.value() == 100
    
    # Second update - one under attack
    nodes[1]['status'] = 'under_attack'
    metrics_widget.update_health(nodes)
    assert metrics_widget.validators_health.value() == 50
    
    # Third update - all under attack
    nodes[0]['status'] = 'under_attack'
    metrics_widget.update_health(nodes)
    assert metrics_widget.validators_health.value() == 0


def test_health_calculation_with_mixed_roles(metrics_widget):
    """Test health calculation with mixed validator and regular nodes."""
    nodes = [
        {'id': 'validator_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'validator_1', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'validator_2', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_0', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy'},
    ]
    
    metrics_widget.update_health(nodes)
    
    # Overall: 5/6 = 83%
    assert metrics_widget.overall_health.value() == 83
    # Validators: 2/3 = 66%
    assert metrics_widget.validators_health.value() == 66
    # Regular: 3/3 = 100%
    assert metrics_widget.regular_health.value() == 100


def test_health_section_groupbox_exists(metrics_widget):
    """Test health section is wrapped in QGroupBox."""
    assert hasattr(metrics_widget, 'health_section')
    assert metrics_widget.health_section.title() == "Network Health"


def test_health_bars_labels_exist(metrics_widget):
    """Test health bars have descriptive labels."""
    # Labels are created in the layout, we can verify by checking
    # the health section has the correct number of widgets
    layout = metrics_widget.health_section.layout()
    assert layout.count() == 3  # Three horizontal layouts for three bars
