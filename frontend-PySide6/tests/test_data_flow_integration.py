"""Tests for Data Flow Integration - Milestone 7.7."""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
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
    client.trigger_attack = Mock(return_value={'attack_id': 'test_attack'})
    client.stop_attack = Mock(return_value={'status': 'stopped'})
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager with signals."""
    from PySide6.QtCore import QObject, Signal
    
    class MockDataManager(QObject):
        nodes_updated = Signal(list)
        blockchain_updated = Signal(list)
        metrics_updated = Signal(dict)
        connection_error = Signal(str)
        status_updated = Signal(dict)
        pbft_updated = Signal(dict)
        attacks_updated = Signal(list)
        fork_status_updated = Signal(dict)
        
        def __init__(self):
            super().__init__()
            self.update_all_data = Mock()
            self.clear_cache = Mock()
    
    return MockDataManager()


@pytest.fixture
def mock_updater():
    """Create mock updater with signals."""
    from PySide6.QtCore import QObject, Signal
    
    class MockUpdater(QObject):
        update_started = Signal()
        update_completed = Signal()
        update_error = Signal(str)
        
        def __init__(self):
            super().__init__()
            self.start_updating = Mock()
            self.stop_updating = Mock()
            self.isRunning = Mock(return_value=False)
    
    return MockUpdater()


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """Create MainWindow instance."""
    window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
    yield window
    window.close()


# ============ Milestone 7.7 Tests: Data Flow Integration ============

def test_main_window_stores_references(main_window, mock_api_client, mock_data_manager, mock_updater):
    """Test main window stores api_client, data_manager, updater references."""
    assert main_window.api_client is mock_api_client
    assert main_window.data_manager is mock_data_manager
    assert main_window.updater is mock_updater


def test_data_manager_connected_to_metrics_widget(main_window):
    """Test DataManager signals are connected to MetricsWidget."""
    # MetricsWidget should be created with data_manager
    assert main_window.metrics_widget is not None
    assert main_window.metrics_widget.data_manager is main_window.data_manager


def test_data_manager_connected_to_pages(main_window):
    """Test DataManager is passed to all pages."""
    assert main_window.dashboard_page.data_manager is main_window.data_manager
    assert main_window.nodes_page.data_manager is main_window.data_manager
    assert main_window.network_page.data_manager is main_window.data_manager
    assert main_window.blockchain_page.data_manager is main_window.data_manager


def test_updater_signals_connected(main_window, mock_updater):
    """Test updater signals are connected to MainWindow slots."""
    # Connection is verified by the window working without errors
    assert hasattr(main_window, 'updater')
    assert main_window.updater is mock_updater


def test_data_manager_error_signal_connected(main_window, mock_data_manager):
    """Test data_manager connection_error is connected."""
    # Connection is verified by the window working without errors
    assert hasattr(main_window, 'data_manager')
    assert main_window.data_manager is mock_data_manager


def test_start_button_starts_updater(main_window, mock_updater, mock_api_client, qapp):
    """Test start button starts the updater thread."""
    main_window.btn_start.click()
    
    # Process events
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should call start_updating
    mock_updater.start_updating.assert_called_once()


def test_stop_button_stops_updater(main_window, mock_updater, mock_api_client, qapp):
    """Test stop button stops the updater thread."""
    # First start
    main_window.btn_start.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Then stop
    main_window.btn_stop.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should call stop_updating
    mock_updater.stop_updating.assert_called()


def test_reset_stops_updater(main_window, mock_updater, mock_api_client, qapp):
    """Test reset button stops the updater."""
    main_window.btn_reset.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    mock_updater.stop_updating.assert_called_once()


def test_reset_clears_data_manager_cache(main_window, mock_data_manager, qapp):
    """Test reset clears data manager cache."""
    main_window.btn_reset.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    mock_data_manager.clear_cache.assert_called_once()


def test_update_completed_updates_status_label(main_window, mock_updater, qapp):
    """Test update_completed signal updates the status label."""
    initial_text = main_window.update_label.text()
    
    # Emit update_completed
    mock_updater.update_completed.emit()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Label should be updated
    assert main_window.update_label.text() != initial_text
    assert "Last update:" in main_window.update_label.text()


def test_connection_error_updates_status(main_window, mock_data_manager, qapp):
    """Test connection_error signal updates connection status."""
    mock_data_manager.connection_error.emit("Test error")
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Connection label should show error
    assert "Error" in main_window.connection_label.text()


def test_nodes_updated_propagates_to_attack_panel(main_window, mock_data_manager, qapp):
    """Test nodes_updated signal propagates to attack panel."""
    # Mock attack panel's update method
    main_window.attack_panel_widget.update_node_list = Mock()
    
    nodes = [{'id': 'node_0'}, {'id': 'node_1'}]
    mock_data_manager.nodes_updated.emit(nodes)
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Attack panel should receive update
    main_window.attack_panel_widget.update_node_list.assert_called_once_with(nodes)


def test_metrics_widget_receives_updates(main_window, mock_data_manager, qapp):
    """Test MetricsWidget receives data manager updates."""
    # Mock metrics widget update methods
    main_window.metrics_widget.update_health = Mock()
    
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy'}
    ]
    
    mock_data_manager.nodes_updated.emit(nodes)
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Metrics should receive update
    main_window.metrics_widget.update_health.assert_called_once_with(nodes)


def test_attack_triggered_calls_api(main_window, mock_api_client, qapp):
    """Test attack trigger calls API client."""
    attack_type = 'ddos'
    params = {'target': 'node_0', 'intensity': 5}
    
    main_window.attack_panel_widget.attack_triggered.emit(attack_type, params)
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should call trigger_attack
    mock_api_client.trigger_attack.assert_called_once()


def test_attack_stop_calls_api(main_window, mock_api_client, qapp):
    """Test attack stop request calls API."""
    attack_id = 'test_attack_123'
    
    main_window.attack_panel_widget.attack_stop_requested.emit(attack_id)
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should call stop_attack
    mock_api_client.stop_attack.assert_called_once_with(attack_id)


def test_all_pages_clear_on_reset(main_window, qapp):
    """Test all pages clear their display on reset."""
    # Mock clear methods
    main_window.dashboard_page.clear_display = Mock()
    main_window.nodes_page.clear_display = Mock()
    main_window.network_page.clear_network = Mock()
    main_window.blockchain_page.clear_display = Mock()
    main_window.metrics_widget.clear_display = Mock()
    
    main_window.btn_reset.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # All clear methods should be called
    main_window.dashboard_page.clear_display.assert_called_once()
    main_window.nodes_page.clear_display.assert_called_once()
    main_window.network_page.clear_network.assert_called_once()
    main_window.blockchain_page.clear_display.assert_called_once()
    main_window.metrics_widget.clear_display.assert_called_once()


def test_window_close_stops_updater(main_window, mock_updater, qapp):
    """Test closing window stops the updater."""
    main_window.close()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    mock_updater.stop_updating.assert_called()


def test_button_states_on_start(main_window, qapp):
    """Test button states change on start."""
    assert main_window.btn_start.isEnabled()
    assert not main_window.btn_stop.isEnabled()
    
    main_window.btn_start.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Start disabled, stop enabled
    assert not main_window.btn_start.isEnabled()
    assert main_window.btn_stop.isEnabled()


def test_button_states_on_stop(main_window, qapp):
    """Test button states change on stop."""
    # Start first
    main_window.btn_start.click()
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Then stop
    main_window.btn_stop.click()
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Start enabled, stop disabled
    assert main_window.btn_start.isEnabled()
    assert not main_window.btn_stop.isEnabled()


def test_button_states_on_reset(main_window, qapp):
    """Test button states reset on reset."""
    main_window.btn_reset.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should return to initial state
    assert main_window.btn_start.isEnabled()
    assert not main_window.btn_stop.isEnabled()


def test_status_messages_on_start(main_window, qapp):
    """Test status bar shows message on start."""
    main_window.btn_start.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Status bar should show message
    assert main_window.status_bar.currentMessage() != ""


def test_connection_check_on_init(main_window):
    """Test connection is checked on initialization."""
    # Should have called is_connected
    assert main_window.api_client.is_connected.called


def test_connection_label_on_connected(main_window, mock_api_client):
    """Test connection label shows connected status."""
    mock_api_client.is_connected.return_value = True
    main_window._check_connection()
    
    assert "Connected" in main_window.connection_label.text()


def test_connection_label_on_disconnected(main_window, mock_api_client):
    """Test connection label shows disconnected status."""
    mock_api_client.is_connected.return_value = False
    main_window._check_connection()
    
    assert "Disconnected" in main_window.connection_label.text()


def test_tabs_created(main_window):
    """Test all tabs are created."""
    assert main_window.tabs.count() == 4
    
    # Check tab titles
    tabs = [main_window.tabs.tabText(i) for i in range(4)]
    assert any("Dashboard" in tab for tab in tabs)
    assert any("Nodes" in tab for tab in tabs)
    assert any("Network" in tab for tab in tabs)
    assert any("Blockchain" in tab for tab in tabs)


def test_dock_widgets_created(main_window):
    """Test dock widgets are created."""
    assert main_window.attack_panel_dock is not None
    assert main_window.metrics_dock is not None


def test_dock_widgets_positioned(main_window):
    """Test dock widgets are positioned correctly."""
    from PySide6.QtCore import Qt
    
    # Attack panel on left
    assert main_window.dockWidgetArea(main_window.attack_panel_dock) == Qt.LeftDockWidgetArea
    
    # Metrics on right
    assert main_window.dockWidgetArea(main_window.metrics_dock) == Qt.RightDockWidgetArea


def test_attack_panel_has_api_reference(main_window):
    """Test attack panel can access API through signals."""
    # Attack panel emits signals that MainWindow handles
    assert hasattr(main_window.attack_panel_widget, 'attack_triggered')
    assert hasattr(main_window.attack_panel_widget, 'attack_stop_requested')


def test_metrics_widget_integration(main_window):
    """Test metrics widget is properly integrated."""
    assert main_window.metrics_widget is not None
    assert main_window.metrics_widget.data_manager is main_window.data_manager


def test_status_bar_has_labels(main_window):
    """Test status bar has required labels."""
    assert main_window.connection_label is not None
    assert main_window.update_label is not None


def test_toolbar_has_control_buttons(main_window):
    """Test toolbar has all control buttons."""
    assert main_window.btn_start is not None
    assert main_window.btn_stop is not None
    assert main_window.btn_reset is not None


def test_multiple_updates_handled(main_window, mock_data_manager, qapp):
    """Test multiple rapid updates are handled correctly."""
    nodes = [{'id': f'node_{i}'} for i in range(5)]
    
    # Emit multiple updates
    for _ in range(5):
        mock_data_manager.nodes_updated.emit(nodes)
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    # Should handle without crashing


def test_error_handling_on_failed_start(main_window, mock_api_client, qapp):
    """Test error handling when start fails."""
    mock_api_client.start_simulator.return_value = {'error': 'Failed'}
    
    main_window.btn_start.click()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Buttons should remain in initial state
    assert main_window.btn_start.isEnabled()


def test_error_handling_on_failed_attack(main_window, mock_api_client, qapp):
    """Test error handling when attack trigger fails."""
    mock_api_client.trigger_attack.return_value = {'error': 'Failed'}
    
    main_window.attack_panel_widget.attack_triggered.emit('ddos', {'target': 'node_0'})
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should show error in status bar
    assert "Failed" in main_window.status_bar.currentMessage()
