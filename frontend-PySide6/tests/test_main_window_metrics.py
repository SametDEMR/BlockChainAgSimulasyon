"""Tests for MainWindow with MetricsWidget integration."""
import pytest
from PySide6.QtWidgets import QApplication, QDockWidget
from unittest.mock import Mock
import sys

from ui.main_window import MainWindow


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_components():
    """Create mock components."""
    api_client = Mock()
    api_client.is_connected = Mock(return_value=True)
    api_client.start_simulator = Mock(return_value={'status': 'started'})
    api_client.stop_simulator = Mock(return_value={'status': 'stopped'})
    api_client.reset_simulator = Mock(return_value={'status': 'reset'})
    
    data_manager = Mock()
    data_manager.connection_error = Mock()
    data_manager.connection_error.connect = Mock()
    data_manager.nodes_updated = Mock()
    data_manager.nodes_updated.connect = Mock()
    data_manager.metrics_updated = Mock()
    data_manager.metrics_updated.connect = Mock()
    data_manager.clear_cache = Mock()
    
    updater = Mock()
    updater.update_completed = Mock()
    updater.update_completed.connect = Mock()
    updater.start_updating = Mock()
    updater.stop_updating = Mock()
    
    return api_client, data_manager, updater


@pytest.fixture
def main_window(qapp, mock_components):
    """Create MainWindow instance."""
    api_client, data_manager, updater = mock_components
    window = MainWindow(api_client, data_manager, updater)
    return window


def test_metrics_dock_exists(main_window):
    """Test metrics dock widget is created."""
    assert hasattr(main_window, 'metrics_dock')
    assert isinstance(main_window.metrics_dock, QDockWidget)


def test_metrics_widget_exists(main_window):
    """Test metrics widget is created."""
    assert hasattr(main_window, 'metrics_widget')
    assert main_window.metrics_widget is not None


def test_metrics_dock_title(main_window):
    """Test metrics dock has correct title."""
    assert main_window.metrics_dock.windowTitle() == "Metrics Dashboard"


def test_metrics_dock_position(main_window):
    """Test metrics dock is on right side."""
    dock_area = main_window.dockWidgetArea(main_window.metrics_dock)
    from PySide6.QtCore import Qt
    assert dock_area == Qt.RightDockWidgetArea


def test_metrics_dock_features(main_window):
    """Test metrics dock has correct features."""
    features = main_window.metrics_dock.features()
    from PySide6.QtWidgets import QDockWidget
    
    # Should be closable and movable
    assert features & QDockWidget.DockWidgetClosable
    assert features & QDockWidget.DockWidgetMovable


def test_metrics_widget_has_data_manager(main_window):
    """Test metrics widget is connected to data manager."""
    assert main_window.metrics_widget.data_manager is not None
    assert main_window.metrics_widget.data_manager == main_window.data_manager


def test_reset_clears_metrics_widget(main_window, mock_components):
    """Test reset button clears metrics widget."""
    api_client, data_manager, updater = mock_components
    
    # Mock clear_display method
    main_window.metrics_widget.clear_display = Mock()
    
    # Trigger reset
    main_window._on_reset()
    
    # Check clear_display was called
    assert main_window.metrics_widget.clear_display.called


def test_metrics_widget_components_exist(main_window):
    """Test metrics widget has all required components."""
    widget = main_window.metrics_widget
    
    # Check graph
    assert hasattr(widget, 'plot_widget')
    
    # Check cards grid
    assert hasattr(widget, 'cards_grid')
    
    # Check health bars
    assert hasattr(widget, 'overall_health')
    assert hasattr(widget, 'validators_health')
    assert hasattr(widget, 'regular_health')
    
    # Check metrics labels
    assert hasattr(widget, 'blocks_per_min')
    assert hasattr(widget, 'tx_per_sec')
    assert hasattr(widget, 'avg_block_time')


def test_dock_widget_not_floating(main_window):
    """Test dock is not floating by default."""
    assert not main_window.metrics_dock.isFloating()


def test_dock_widget_visible(main_window):
    """Test dock is not hidden by default."""
    assert not main_window.metrics_dock.isHidden()
