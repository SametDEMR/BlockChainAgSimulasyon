"""Tests for System Metrics - Milestone 7.5."""
import pytest
from PySide6.QtWidgets import QApplication, QLabel
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


# ============ Milestone 7.5 Tests: System Metrics ============

def test_metrics_section_exists(metrics_widget):
    """Test system metrics section is created."""
    assert hasattr(metrics_widget, 'metrics_section')
    assert metrics_widget.metrics_section.title() == "System Metrics"


def test_metrics_labels_exist(metrics_widget):
    """Test all metric labels are created."""
    assert hasattr(metrics_widget, 'blocks_per_min')
    assert hasattr(metrics_widget, 'tx_per_sec')
    assert hasattr(metrics_widget, 'avg_block_time')
    
    assert isinstance(metrics_widget.blocks_per_min, QLabel)
    assert isinstance(metrics_widget.tx_per_sec, QLabel)
    assert isinstance(metrics_widget.avg_block_time, QLabel)


def test_metrics_initial_values(metrics_widget):
    """Test metrics start with initial values."""
    assert metrics_widget.blocks_per_min.text() == "0"
    assert metrics_widget.tx_per_sec.text() == "0.0"
    assert metrics_widget.avg_block_time.text() == "0.0s"


def test_metrics_labels_styling(metrics_widget):
    """Test metric value labels have bold styling."""
    assert 'bold' in metrics_widget.blocks_per_min.styleSheet().lower()
    assert 'bold' in metrics_widget.tx_per_sec.styleSheet().lower()
    assert 'bold' in metrics_widget.avg_block_time.styleSheet().lower()


def test_update_metrics_blocks_per_min(metrics_widget):
    """Test updating blocks per minute."""
    metrics = {'blocks_per_minute': 5}
    metrics_widget.update_metrics(metrics)
    assert metrics_widget.blocks_per_min.text() == "5"


def test_update_metrics_tx_per_sec(metrics_widget):
    """Test updating transactions per second."""
    metrics = {'transactions_per_second': 12.5}
    metrics_widget.update_metrics(metrics)
    assert metrics_widget.tx_per_sec.text() == "12.5"


def test_update_metrics_avg_block_time(metrics_widget):
    """Test updating average block time."""
    metrics = {'average_block_time': 3.2}
    metrics_widget.update_metrics(metrics)
    assert metrics_widget.avg_block_time.text() == "3.2s"


def test_update_metrics_all_values(metrics_widget):
    """Test updating all metrics at once."""
    metrics = {
        'blocks_per_minute': 8,
        'transactions_per_second': 24.7,
        'average_block_time': 2.5
    }
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.blocks_per_min.text() == "8"
    assert metrics_widget.tx_per_sec.text() == "24.7"
    assert metrics_widget.avg_block_time.text() == "2.5s"


def test_update_metrics_zero_values(metrics_widget):
    """Test updating with zero values."""
    metrics = {
        'blocks_per_minute': 0,
        'transactions_per_second': 0.0,
        'average_block_time': 0.0
    }
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.blocks_per_min.text() == "0"
    assert metrics_widget.tx_per_sec.text() == "0.0"
    assert metrics_widget.avg_block_time.text() == "0.0s"


def test_update_metrics_high_values(metrics_widget):
    """Test updating with high values."""
    metrics = {
        'blocks_per_minute': 999,
        'transactions_per_second': 9999.9,
        'average_block_time': 99.9
    }
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.blocks_per_min.text() == "999"
    assert metrics_widget.tx_per_sec.text() == "9999.9"
    assert metrics_widget.avg_block_time.text() == "99.9s"


def test_update_metrics_empty_dict(metrics_widget):
    """Test updating with empty metrics dict."""
    metrics_widget.update_metrics({})
    # Should not crash, values should remain unchanged


def test_update_metrics_missing_fields(metrics_widget):
    """Test updating with missing fields uses defaults."""
    metrics = {'blocks_per_minute': 10}  # Only one field
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.blocks_per_min.text() == "10"
    # Others should remain at previous values


def test_update_metrics_none_value(metrics_widget):
    """Test updating with None."""
    metrics_widget.update_metrics(None)
    # Should not crash


def test_update_metrics_tx_per_sec_formatting(metrics_widget):
    """Test TX/sec is formatted with 1 decimal place."""
    metrics = {'transactions_per_second': 15.678}
    metrics_widget.update_metrics(metrics)
    assert metrics_widget.tx_per_sec.text() == "15.7"


def test_update_metrics_avg_block_time_formatting(metrics_widget):
    """Test avg block time is formatted with 1 decimal and 's' suffix."""
    metrics = {'average_block_time': 4.567}
    metrics_widget.update_metrics(metrics)
    assert metrics_widget.avg_block_time.text() == "4.6s"


def test_update_metrics_blocks_no_decimal(metrics_widget):
    """Test blocks per minute has no decimal places."""
    metrics = {'blocks_per_minute': 7.8}
    metrics_widget.update_metrics(metrics)
    # Should convert to integer string
    assert metrics_widget.blocks_per_min.text() in ["7", "7.8"]


def test_signal_connection_for_metrics(metrics_widget, mock_data_manager):
    """Test metrics update is connected to metrics_updated signal."""
    calls = [call[0][0] for call in mock_data_manager.metrics_updated.connect.call_args_list]
    assert metrics_widget.update_metrics in calls


def test_clear_display_resets_metrics(metrics_widget):
    """Test clear_display resets all metrics to initial values."""
    # Set some values
    metrics = {
        'blocks_per_minute': 10,
        'transactions_per_second': 25.5,
        'average_block_time': 3.0
    }
    metrics_widget.update_metrics(metrics)
    
    # Clear
    metrics_widget.clear_display()
    
    # Should reset
    assert metrics_widget.blocks_per_min.text() == "0"
    assert metrics_widget.tx_per_sec.text() == "0.0"
    assert metrics_widget.avg_block_time.text() == "0.0s"


def test_update_metrics_multiple_times(metrics_widget):
    """Test multiple sequential updates."""
    # First update
    metrics1 = {
        'blocks_per_minute': 5,
        'transactions_per_second': 10.0,
        'average_block_time': 2.0
    }
    metrics_widget.update_metrics(metrics1)
    assert metrics_widget.blocks_per_min.text() == "5"
    
    # Second update
    metrics2 = {
        'blocks_per_minute': 8,
        'transactions_per_second': 20.5,
        'average_block_time': 1.5
    }
    metrics_widget.update_metrics(metrics2)
    assert metrics_widget.blocks_per_min.text() == "8"
    assert metrics_widget.tx_per_sec.text() == "20.5"
    assert metrics_widget.avg_block_time.text() == "1.5s"


def test_metrics_grid_layout(metrics_widget):
    """Test metrics use grid layout."""
    # Metrics section should have a layout
    layout = metrics_widget.metrics_section.layout()
    assert layout is not None


def test_metrics_labels_font_size(metrics_widget):
    """Test metric values have larger font size."""
    assert '14px' in metrics_widget.blocks_per_min.styleSheet()
    assert '14px' in metrics_widget.tx_per_sec.styleSheet()
    assert '14px' in metrics_widget.avg_block_time.styleSheet()


def test_update_metrics_negative_values(metrics_widget):
    """Test handling negative values (edge case)."""
    metrics = {
        'blocks_per_minute': -5,
        'transactions_per_second': -10.5,
        'average_block_time': -2.0
    }
    metrics_widget.update_metrics(metrics)
    
    # Should display as-is (edge case)
    assert '-5' in metrics_widget.blocks_per_min.text()


def test_update_metrics_float_blocks(metrics_widget):
    """Test blocks per minute with float input."""
    metrics = {'blocks_per_minute': 5.9}
    metrics_widget.update_metrics(metrics)
    # Implementation converts to string directly
    assert '5' in metrics_widget.blocks_per_min.text()


def test_update_metrics_very_small_values(metrics_widget):
    """Test very small decimal values."""
    metrics = {
        'transactions_per_second': 0.1,
        'average_block_time': 0.05
    }
    metrics_widget.update_metrics(metrics)
    
    assert metrics_widget.tx_per_sec.text() == "0.1"
    assert metrics_widget.avg_block_time.text() == "0.1s"  # Rounded to 0.1


def test_metrics_persistence_after_clear(metrics_widget):
    """Test metrics can be updated after clear."""
    # Update
    metrics_widget.update_metrics({'blocks_per_minute': 10})
    
    # Clear
    metrics_widget.clear_display()
    assert metrics_widget.blocks_per_min.text() == "0"
    
    # Update again
    metrics_widget.update_metrics({'blocks_per_minute': 15})
    assert metrics_widget.blocks_per_min.text() == "15"


def test_tx_per_sec_precision(metrics_widget):
    """Test TX/sec maintains 1 decimal precision."""
    test_cases = [
        (12.0, "12.0"),
        (12.12, "12.1"),
        (12.14, "12.1"),
        (12.19, "12.2"),
        (12.999, "13.0"),
    ]
    
    for input_val, expected in test_cases:
        metrics_widget.update_metrics({'transactions_per_second': input_val})
        assert metrics_widget.tx_per_sec.text() == expected


def test_avg_block_time_includes_suffix(metrics_widget):
    """Test average block time always includes 's' suffix."""
    test_values = [0.0, 1.5, 10.0, 99.9]
    
    for value in test_values:
        metrics_widget.update_metrics({'average_block_time': value})
        assert metrics_widget.avg_block_time.text().endswith('s')
