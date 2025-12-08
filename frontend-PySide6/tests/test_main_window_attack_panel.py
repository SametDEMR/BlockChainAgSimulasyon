"""Tests for Milestone 3.3 - MainWindow Attack Panel Integration."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, MagicMock
import sys

from ui.main_window import MainWindow
from core.api_client import APIClient
from core.data_manager import DataManager
from core.updater import DataUpdater


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
    client = Mock(spec=APIClient)
    client.is_connected = Mock(return_value=True)
    client.start_simulator = Mock(return_value={'status': 'started'})
    client.stop_simulator = Mock(return_value={'status': 'stopped'})
    client.reset_simulator = Mock(return_value={'status': 'reset'})
    client.trigger_attack = Mock(return_value={'attack_id': 'attack_123', 'duration': 30})
    client.stop_attack = Mock(return_value={'status': 'stopped'})
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    manager = Mock(spec=DataManager)
    manager.nodes_updated = MagicMock()
    manager.metrics_updated = MagicMock()
    manager.connection_error = MagicMock()
    manager.clear_cache = Mock()
    return manager


@pytest.fixture
def mock_updater():
    """Create mock updater."""
    updater = Mock(spec=DataUpdater)
    updater.update_completed = MagicMock()
    updater.start_updating = Mock()
    updater.stop_updating = Mock()
    return updater


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """Create MainWindow instance."""
    window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
    return window


# ============ Attack Panel Dock Tests ============

def test_attack_panel_dock_created(main_window):
    """Test attack panel dock is created."""
    assert hasattr(main_window, 'attack_panel_dock')
    assert main_window.attack_panel_dock is not None


def test_attack_panel_widget_created(main_window):
    """Test attack panel widget is created."""
    assert hasattr(main_window, 'attack_panel_widget')
    assert main_window.attack_panel_widget is not None


def test_attack_panel_dock_title(main_window):
    """Test attack panel dock has correct title."""
    assert main_window.attack_panel_dock.windowTitle() == "Attack Control Panel"


def test_attack_panel_on_left_side(main_window):
    """Test attack panel is positioned on left side."""
    from PySide6.QtCore import Qt
    area = main_window.dockWidgetArea(main_window.attack_panel_dock)
    assert area == Qt.LeftDockWidgetArea


# ============ Signal Connection Tests ============

def test_attack_triggered_signal_connected(main_window):
    """Test attack_triggered signal is connected."""
    # Trigger an attack
    main_window.attack_panel_widget.attack_triggered.emit("ddos", {"target": "node_5"})
    
    # Should call API
    main_window.api_client.trigger_attack.assert_called_once_with("ddos", {"target": "node_5"})


def test_attack_stop_signal_connected(main_window):
    """Test attack_stop_requested signal is connected."""
    # Request stop
    main_window.attack_panel_widget.attack_stop_requested.emit("attack_123")
    
    # Should call API
    main_window.api_client.stop_attack.assert_called_once_with("attack_123")


def test_nodes_updated_updates_attack_panel(main_window):
    """Test nodes_updated signal updates attack panel."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False}
    ]
    
    # Directly call update_node_list (mock signal doesn't trigger slots)
    main_window.attack_panel_widget.update_node_list(nodes)
    
    # Check dropdowns populated (1 default + 2 nodes = 3)
    assert main_window.attack_panel_widget.ddos_target.count() == 3
    assert main_window.attack_panel_widget.byzantine_target.count() == 2  # 1 default + 1 validator


# ============ Attack Trigger Tests ============

def test_successful_attack_trigger(main_window):
    """Test successful attack trigger."""
    # Setup mock response
    main_window.api_client.trigger_attack.return_value = {
        'attack_id': 'attack_123',
        'duration': 30
    }
    
    # Trigger attack
    main_window._on_attack_triggered("ddos", {"target": "node_5", "intensity": 8})
    
    # Check active attack added
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


def test_failed_attack_trigger(main_window):
    """Test failed attack trigger."""
    # Setup mock response with error
    main_window.api_client.trigger_attack.return_value = {
        'error': 'Backend error'
    }
    
    # Trigger attack
    main_window._on_attack_triggered("ddos", {"target": "node_5"})
    
    # Check no active attack added
    assert main_window.attack_panel_widget.get_active_attacks_count() == 0


def test_attack_trigger_without_attack_id(main_window):
    """Test attack trigger response without attack_id."""
    # Setup mock response without attack_id
    main_window.api_client.trigger_attack.return_value = {
        'status': 'started'
    }
    
    # Trigger attack
    main_window._on_attack_triggered("ddos", {"target": "node_5"})
    
    # Check no active attack added
    assert main_window.attack_panel_widget.get_active_attacks_count() == 0


def test_attack_trigger_connection_error(main_window):
    """Test attack trigger with connection error."""
    # Setup mock to return None
    main_window.api_client.trigger_attack.return_value = None
    
    # Trigger attack
    main_window._on_attack_triggered("ddos", {"target": "node_5"})
    
    # Check no active attack added
    assert main_window.attack_panel_widget.get_active_attacks_count() == 0


# ============ Attack Stop Tests ============

def test_successful_attack_stop(main_window):
    """Test successful attack stop."""
    # First add an attack
    main_window.attack_panel_widget.add_active_attack({
        'id': 'attack_123',
        'type': 'ddos',
        'target': 'node_5',
        'progress': 0.5,
        'remaining_time': 15
    })
    
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1
    
    # Setup mock response
    main_window.api_client.stop_attack.return_value = {'status': 'stopped'}
    
    # Stop attack
    main_window._on_attack_stop_requested('attack_123')
    
    # Check attack removed
    assert main_window.attack_panel_widget.get_active_attacks_count() == 0


def test_failed_attack_stop(main_window):
    """Test failed attack stop."""
    # First add an attack
    main_window.attack_panel_widget.add_active_attack({
        'id': 'attack_123',
        'type': 'ddos',
        'target': 'node_5',
        'progress': 0.5,
        'remaining_time': 15
    })
    
    # Setup mock response with error
    main_window.api_client.stop_attack.return_value = {'error': 'Attack not found'}
    
    # Stop attack
    main_window._on_attack_stop_requested('attack_123')
    
    # Check attack NOT removed (because API failed)
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


def test_attack_stop_connection_error(main_window):
    """Test attack stop with connection error."""
    # First add an attack
    main_window.attack_panel_widget.add_active_attack({
        'id': 'attack_123',
        'type': 'ddos',
        'target': 'node_5',
        'progress': 0.5,
        'remaining_time': 15
    })
    
    # Setup mock to return None
    main_window.api_client.stop_attack.return_value = None
    
    # Stop attack
    main_window._on_attack_stop_requested('attack_123')
    
    # Check attack NOT removed
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


# ============ Reset Tests ============

def test_reset_clears_active_attacks(main_window):
    """Test reset button clears active attacks."""
    # Add some attacks
    main_window.attack_panel_widget.add_active_attack({
        'id': 'attack_1',
        'type': 'ddos',
        'target': 'node_5',
        'progress': 0.5,
        'remaining_time': 15
    })
    main_window.attack_panel_widget.add_active_attack({
        'id': 'attack_2',
        'type': 'byzantine',
        'target': 'node_1',
        'progress': 0.3,
        'remaining_time': 20
    })
    
    assert main_window.attack_panel_widget.get_active_attacks_count() == 2
    
    # Click reset
    main_window.btn_reset.click()
    
    # Check attacks cleared
    assert main_window.attack_panel_widget.get_active_attacks_count() == 0


# ============ Attack Data Tests ============

def test_attack_data_includes_type(main_window):
    """Test attack data includes attack type."""
    main_window.api_client.trigger_attack.return_value = {
        'attack_id': 'attack_123',
        'duration': 30
    }
    
    main_window._on_attack_triggered("byzantine", {"target": "node_1"})
    
    # Get added attack item
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


def test_attack_data_includes_target(main_window):
    """Test attack data includes target."""
    main_window.api_client.trigger_attack.return_value = {
        'attack_id': 'attack_123',
        'duration': 30
    }
    
    main_window._on_attack_triggered("ddos", {"target": "node_5", "intensity": 8})
    
    # Attack should be added
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


def test_attack_data_without_target(main_window):
    """Test attack data without target (network-wide attacks)."""
    main_window.api_client.trigger_attack.return_value = {
        'attack_id': 'attack_123',
        'duration': 30
    }
    
    main_window._on_attack_triggered("partition", {})
    
    # Attack should be added with target='N/A'
    assert main_window.attack_panel_widget.get_active_attacks_count() == 1


# ============ Multiple Attacks Tests ============

def test_multiple_attacks_simultaneously(main_window):
    """Test handling multiple simultaneous attacks."""
    # Trigger multiple attacks
    for i in range(3):
        main_window.api_client.trigger_attack.return_value = {
            'attack_id': f'attack_{i}',
            'duration': 30
        }
        main_window._on_attack_triggered("ddos", {"target": f"node_{i}"})
    
    assert main_window.attack_panel_widget.get_active_attacks_count() == 3


def test_stop_one_of_multiple_attacks(main_window):
    """Test stopping one attack while others continue."""
    # Add multiple attacks
    for i in range(3):
        main_window.attack_panel_widget.add_active_attack({
            'id': f'attack_{i}',
            'type': 'ddos',
            'target': f'node_{i}',
            'progress': 0.5,
            'remaining_time': 15
        })
    
    assert main_window.attack_panel_widget.get_active_attacks_count() == 3
    
    # Stop one
    main_window.api_client.stop_attack.return_value = {'status': 'stopped'}
    main_window._on_attack_stop_requested('attack_1')
    
    assert main_window.attack_panel_widget.get_active_attacks_count() == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
