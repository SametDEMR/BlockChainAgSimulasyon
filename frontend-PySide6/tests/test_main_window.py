"""Tests for MainWindow - Updated for Milestone 2.4."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, MagicMock
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
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.is_connected = Mock(return_value=True)
    client.start_simulator = Mock(return_value={'status': 'started'})
    client.stop_simulator = Mock(return_value={'status': 'stopped'})
    client.reset_simulator = Mock(return_value={'status': 'reset'})
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    manager = Mock()
    manager.connection_error = Mock()
    manager.connection_error.connect = Mock()
    manager.clear_cache = Mock()
    manager.nodes_updated = Mock()
    manager.nodes_updated.connect = Mock()
    manager.metrics_updated = Mock()
    manager.metrics_updated.connect = Mock()
    return manager


@pytest.fixture
def mock_updater():
    """Create mock updater."""
    updater = Mock()
    updater.update_completed = Mock()
    updater.update_completed.connect = Mock()
    updater.start_updating = Mock()
    updater.stop_updating = Mock()
    return updater


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """Create MainWindow instance."""
    window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
    return window


# ============ Previous Tests (Milestone 1) ============

def test_main_window_creation(main_window):
    """Test main window is created."""
    assert main_window is not None


def test_toolbar_buttons_exist(main_window):
    """Test toolbar buttons exist."""
    assert main_window.btn_start is not None
    assert main_window.btn_stop is not None
    assert main_window.btn_reset is not None


def test_tabs_exist(main_window):
    """Test tab widget and pages exist."""
    assert main_window.tabs is not None
    assert main_window.dashboard_page is not None
    assert main_window.nodes_page is not None


# ============ Milestone 2.4 Tests (Metrics Dock) ============

def test_metrics_dock_exists(main_window):
    """Test metrics dock widget is created."""
    assert hasattr(main_window, 'metrics_dock')
    assert main_window.metrics_dock is not None


def test_metrics_widget_exists(main_window):
    """Test metrics widget is created."""
    assert hasattr(main_window, 'metrics_widget')
    assert main_window.metrics_widget is not None


def test_metrics_dock_on_right_side(main_window):
    """Test metrics dock is on right side."""
    from PySide6.QtCore import Qt
    
    # Check dock is added
    docks = main_window.findChildren(type(main_window.metrics_dock))
    assert len(docks) >= 1
    
    # Check it's on right side
    area = main_window.dockWidgetArea(main_window.metrics_dock)
    assert area == Qt.RightDockWidgetArea


def test_metrics_widget_has_data_manager(main_window, mock_data_manager):
    """Test metrics widget receives data manager."""
    assert main_window.metrics_widget.data_manager is mock_data_manager


def test_reset_clears_metrics_widget(main_window, mock_api_client):
    """Test reset button clears metrics widget."""
    # Mock clear_display
    main_window.metrics_widget.clear_display = Mock()
    
    # Trigger reset
    main_window._on_reset()
    
    # Verify clear was called
    main_window.metrics_widget.clear_display.assert_called_once()


def test_metrics_dock_can_float(main_window):
    """Test metrics dock can be floated."""
    # Dock should allow floating
    features = main_window.metrics_dock.features()
    from PySide6.QtWidgets import QDockWidget
    
    assert features & QDockWidget.DockWidgetFloatable


def test_metrics_dock_can_be_moved(main_window):
    """Test metrics dock can be moved."""
    from PySide6.QtCore import Qt
    
    allowed = main_window.metrics_dock.allowedAreas()
    
    # Should allow right and left
    assert allowed & Qt.RightDockWidgetArea
    assert allowed & Qt.LeftDockWidgetArea


def test_dock_widget_title(main_window):
    """Test dock widget has correct title."""
    title = main_window.metrics_dock.windowTitle()
    assert "Metrics" in title or "Dashboard" in title
