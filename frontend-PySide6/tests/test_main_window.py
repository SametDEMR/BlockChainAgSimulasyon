"""Test for Main Window."""
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.is_connected.return_value = True
    client.start_simulator.return_value = {"message": "started"}
    client.stop_simulator.return_value = {"message": "stopped"}
    client.reset_simulator.return_value = {"message": "reset"}
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    from core.data_manager import DataManager
    dm = Mock(spec=DataManager)
    dm.connection_error = Mock()
    dm.clear_cache = Mock()
    return dm


@pytest.fixture
def mock_updater():
    """Create mock updater."""
    from core.updater import DataUpdater
    updater = Mock(spec=DataUpdater)
    updater.update_completed = Mock()
    updater.start_updating = Mock()
    updater.stop_updating = Mock()
    updater.is_updating = Mock(return_value=False)
    return updater


@pytest.fixture
def main_window(qapp, mock_api_client, mock_data_manager, mock_updater):
    """Create main window."""
    window = MainWindow(mock_api_client, mock_data_manager, mock_updater)
    yield window
    window.close()


class TestMainWindow:
    """Test MainWindow class."""
    
    def test_init(self, main_window):
        """Test window initialization."""
        assert main_window.windowTitle() == "Blockchain Attack Simulator"
        assert main_window.minimumWidth() == 1200
        assert main_window.minimumHeight() == 800
    
    def test_buttons_exist(self, main_window):
        """Test control buttons exist."""
        assert main_window.btn_start is not None
        assert main_window.btn_stop is not None
        assert main_window.btn_reset is not None
    
    def test_initial_button_states(self, main_window):
        """Test initial button states."""
        assert main_window.btn_start.isEnabled() is True
        assert main_window.btn_stop.isEnabled() is False
    
    def test_tabs_exist(self, main_window):
        """Test tabs widget exists."""
        assert main_window.tabs is not None
        assert main_window.tabs.count() == 2
    
    def test_dashboard_page_exists(self, main_window):
        """Test dashboard page is created."""
        assert main_window.dashboard_page is not None
    
    def test_nodes_page_exists(self, main_window):
        """Test nodes page is created."""
        assert main_window.nodes_page is not None
    
    def test_start_button_click(self, main_window, mock_api_client, mock_updater):
        """Test start button functionality."""
        main_window.btn_start.click()
        
        mock_api_client.start_simulator.assert_called_once()
        mock_updater.start_updating.assert_called_once()
        
        assert main_window.btn_start.isEnabled() is False
        assert main_window.btn_stop.isEnabled() is True
    
    def test_stop_button_click(self, main_window, mock_api_client, mock_updater):
        """Test stop button functionality."""
        # First start
        main_window.btn_start.click()
        
        # Then stop
        main_window.btn_stop.click()
        
        mock_api_client.stop_simulator.assert_called_once()
        mock_updater.stop_updating.assert_called()
        
        assert main_window.btn_start.isEnabled() is True
        assert main_window.btn_stop.isEnabled() is False
    
    def test_reset_button_click(self, main_window, mock_api_client, mock_updater, mock_data_manager):
        """Test reset button functionality."""
        main_window.btn_reset.click()
        
        mock_api_client.reset_simulator.assert_called_once()
        mock_updater.stop_updating.assert_called_once()
        mock_data_manager.clear_cache.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
