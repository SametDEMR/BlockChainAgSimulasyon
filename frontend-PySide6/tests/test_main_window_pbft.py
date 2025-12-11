"""
Tests for MainWindow PBFT Integration (Milestone 8.2)
"""
import pytest
import sys
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from ui.main_window import MainWindow


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_api_client():
    """Mock API client"""
    client = Mock()
    client.is_connected.return_value = True
    client.start_simulator.return_value = {'status': 'started'}
    client.stop_simulator.return_value = {'status': 'stopped'}
    client.reset_simulator.return_value = {'status': 'reset'}
    return client


@pytest.fixture
def mock_data_manager():
    """Mock data manager"""
    manager = Mock()
    
    # Mock signals
    manager.status_updated = Mock()
    manager.nodes_updated = Mock()
    manager.blockchain_updated = Mock()
    manager.pbft_updated = Mock()
    manager.metrics_updated = Mock()
    manager.attacks_updated = Mock()
    manager.messages_updated = Mock()
    manager.fork_status_updated = Mock()
    manager.connection_error = Mock()
    manager.api_error = Mock()
    
    # Add connect methods
    for signal_name in ['status_updated', 'nodes_updated', 'blockchain_updated',
                        'pbft_updated', 'metrics_updated', 'attacks_updated',
                        'messages_updated', 'fork_status_updated', 
                        'connection_error', 'api_error']:
        signal = getattr(manager, signal_name)
        signal.connect = Mock()
        signal.emit = Mock()
    
    return manager


@pytest.fixture
def mock_updater():
    """Mock data updater"""
    updater = Mock()
    updater.update_completed = Mock()
    updater.update_completed.connect = Mock()
    updater.start_updating = Mock()
    updater.stop_updating = Mock()
    return updater


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """MainWindow fixture"""
    # Create actual QWidget instances with mocked methods
    mock_dashboard = QWidget()
    mock_dashboard.clear_display = Mock()
    
    mock_nodes = QWidget()
    mock_nodes.clear_display = Mock()
    
    mock_network = QWidget()
    mock_network.clear_network = Mock()
    
    mock_blockchain = QWidget()
    mock_blockchain.clear_display = Mock()
    
    mock_attack = QWidget()
    mock_attack.update_node_list = Mock()
    mock_attack.clear_active_attacks = Mock()
    mock_attack.add_active_attack = Mock()
    mock_attack.remove_active_attack = Mock()
    mock_attack.attack_triggered = Mock()
    mock_attack.attack_stop_requested = Mock()
    mock_attack.attack_triggered.connect = Mock()
    mock_attack.attack_stop_requested.connect = Mock()
    
    mock_metrics = QWidget()
    mock_metrics.clear_display = Mock()
    
    mock_pbft = QWidget()
    mock_pbft.update_pbft_status = Mock()
    mock_pbft.update_messages = Mock()
    mock_pbft.clear_display = Mock()
    
    with patch('ui.pages.dashboard_page.DashboardPage', return_value=mock_dashboard), \
         patch('ui.pages.nodes_page.NodesPage', return_value=mock_nodes), \
         patch('ui.pages.network_page.NetworkMapPage', return_value=mock_network), \
         patch('ui.pages.blockchain_page.BlockchainExplorerPage', return_value=mock_blockchain), \
         patch('ui.widgets.attack_panel_widget.AttackPanelWidget', return_value=mock_attack), \
         patch('ui.widgets.metrics_widget.MetricsWidget', return_value=mock_metrics), \
         patch('ui.widgets.pbft_widget.PBFTWidget', return_value=mock_pbft):
        
        window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
        window.show()  # Show window for visibility tests
        return window


class TestMainWindowPBFTIntegration:
    """Test suite for MainWindow PBFT Integration (8.2)"""
    
    def test_pbft_dock_exists(self, main_window):
        """Test PBFT dock widget is created"""
        assert hasattr(main_window, 'pbft_dock')
        assert main_window.pbft_dock is not None
    
    def test_pbft_widget_exists(self, main_window):
        """Test PBFT widget is created"""
        assert hasattr(main_window, 'pbft_widget')
        assert main_window.pbft_widget is not None
    
    def test_pbft_dock_title(self, main_window):
        """Test PBFT dock has correct title"""
        assert main_window.pbft_dock.windowTitle() == "PBFT Consensus Status"
    
    def test_pbft_dock_area(self, main_window):
        """Test PBFT dock is in bottom area"""
        assert main_window.pbft_dock.widget() is not None
    
    def test_pbft_dock_allowed_areas(self, main_window):
        """Test PBFT dock allowed areas"""
        allowed_areas = main_window.pbft_dock.allowedAreas()
        assert allowed_areas & Qt.BottomDockWidgetArea
        assert allowed_areas & Qt.TopDockWidgetArea
    
    def test_pbft_signal_connections(self, main_window, mock_data_manager):
        """Test PBFT signals are connected to data manager"""
        # Verify connect was called for pbft signals
        mock_data_manager.pbft_updated.connect.assert_called()
        mock_data_manager.messages_updated.connect.assert_called()
    
    def test_pbft_dock_widget_content(self, main_window):
        """Test PBFT dock contains PBFT widget"""
        assert main_window.pbft_dock.widget() == main_window.pbft_widget
    
    def test_pbft_widget_initialization(self, main_window):
        """Test PBFT widget is properly initialized"""
        assert isinstance(main_window.pbft_widget, QWidget)
    
    def test_pbft_clear_on_reset(self, main_window):
        """Test PBFT widget is cleared on simulator reset"""
        main_window._on_reset()
        main_window.pbft_widget.clear_display.assert_called_once()
    
    def test_pbft_dock_visibility(self, main_window):
        """Test PBFT dock is visible after window is shown"""
        # Dock should be visible after main window is shown
        assert main_window.pbft_dock.isVisible()
    
    def test_pbft_dock_can_be_hidden(self, main_window):
        """Test PBFT dock can be hidden and shown"""
        # Initially visible
        assert main_window.pbft_dock.isVisible()
        
        # Hide dock
        main_window.pbft_dock.hide()
        assert not main_window.pbft_dock.isVisible()
        
        # Show dock
        main_window.pbft_dock.show()
        assert main_window.pbft_dock.isVisible()
    
    def test_pbft_widget_has_update_methods(self, main_window):
        """Test PBFT widget has required update methods"""
        assert hasattr(main_window.pbft_widget, 'update_pbft_status')
        assert hasattr(main_window.pbft_widget, 'update_messages')
        assert hasattr(main_window.pbft_widget, 'clear_display')
    
    def test_pbft_connection_to_data_manager(self, main_window, mock_data_manager):
        """Test PBFT widget is connected to data manager signals"""
        # Check that connections were made
        connect_calls = mock_data_manager.pbft_updated.connect.call_args_list
        assert len(connect_calls) > 0
        
        message_calls = mock_data_manager.messages_updated.connect.call_args_list
        assert len(message_calls) > 0
    
    def test_main_window_has_pbft_dock_and_widget(self, main_window):
        """Test main window has both pbft_dock and pbft_widget attributes"""
        assert hasattr(main_window, 'pbft_dock')
        assert hasattr(main_window, 'pbft_widget')
        assert main_window.pbft_dock is not None
        assert main_window.pbft_widget is not None
    
    def test_pbft_widget_is_inside_dock(self, main_window):
        """Test PBFT widget is correctly placed inside dock"""
        dock_widget = main_window.pbft_dock.widget()
        assert dock_widget is main_window.pbft_widget
    
    def test_reset_calls_all_clear_methods(self, main_window):
        """Test reset calls clear_display on all widgets including PBFT"""
        main_window._on_reset()
        
        # Verify all widgets had clear called
        main_window.dashboard_page.clear_display.assert_called_once()
        main_window.nodes_page.clear_display.assert_called_once()
        main_window.network_page.clear_network.assert_called_once()
        main_window.blockchain_page.clear_display.assert_called_once()
        main_window.metrics_widget.clear_display.assert_called_once()
        main_window.pbft_widget.clear_display.assert_called_once()
        main_window.attack_panel_widget.clear_active_attacks.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
