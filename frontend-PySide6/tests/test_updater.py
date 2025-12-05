"""Tests for Data Updater."""
import pytest
from unittest.mock import Mock
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.updater import DataUpdater


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.is_connected.return_value = True
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    dm = Mock()
    dm.update_all_data = Mock()
    return dm


@pytest.fixture
def updater(mock_api_client, mock_data_manager):
    """Create updater instance."""
    return DataUpdater(mock_api_client, mock_data_manager, interval_ms=100)


class TestDataUpdater:
    """Test DataUpdater class."""
    
    def test_init(self, updater):
        """Test initialization."""
        assert updater.api_client is not None
        assert updater.data_manager is not None
        assert updater.interval_ms == 100
        assert updater._running is False
    
    def test_set_interval(self, updater):
        """Test interval setting."""
        updater.set_interval(500)
        assert updater.interval_ms == 500
    
    def test_is_updating_initially_false(self, updater):
        """Test updater not running initially."""
        assert updater.is_updating() is False
    
    def test_start_stop_updating(self, updater):
        """Test starting and stopping updater."""
        # Start
        updater.start_updating()
        time.sleep(0.05)  # Short wait
        assert updater.is_updating() is True
        
        # Stop
        updater.stop_updating()
        assert updater.is_updating() is False
    
    def test_update_cycle(self, updater, mock_data_manager):
        """Test update cycle calls data manager."""
        # Start updater
        updater.start_updating()
        
        # Wait for at least one update cycle
        time.sleep(0.2)
        
        # Verify update_all_data was called
        assert mock_data_manager.update_all_data.call_count >= 1
        
        # Stop
        updater.stop_updating()
    
    def test_signals_exist(self, updater):
        """Test all signals are defined."""
        assert hasattr(updater, 'update_started')
        assert hasattr(updater, 'update_completed')
        assert hasattr(updater, 'update_error')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
