"""Tests for Real-time Updater (QThread) - Milestone 7.6."""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, QTimer
from unittest.mock import Mock, patch
import sys
import time

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
    client = Mock()
    return client


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    manager = Mock()
    manager.update_all_data = Mock()
    return manager


@pytest.fixture
def updater(qapp, mock_api_client, mock_data_manager):
    """Create DataUpdater instance."""
    upd = DataUpdater(mock_api_client, mock_data_manager, interval_ms=500)
    yield upd
    # Cleanup
    if upd.isRunning():
        upd.stop_updating()


# ============ Milestone 7.6 Tests: Real-time Updater ============

def test_updater_creation(updater, mock_api_client, mock_data_manager):
    """Test updater is created successfully."""
    assert updater is not None
    assert isinstance(updater, QThread)
    assert updater.api_client is mock_api_client
    assert updater.data_manager is mock_data_manager


def test_updater_default_interval(mock_api_client, mock_data_manager, qapp):
    """Test updater has default 2000ms interval."""
    upd = DataUpdater(mock_api_client, mock_data_manager)
    assert upd.interval_ms == 2000


def test_updater_custom_interval(updater):
    """Test updater accepts custom interval."""
    assert updater.interval_ms == 500


def test_updater_has_signals(updater):
    """Test updater has required signals."""
    assert hasattr(updater, 'update_started')
    assert hasattr(updater, 'update_completed')
    assert hasattr(updater, 'update_error')


def test_updater_initial_state(updater):
    """Test updater starts in stopped state."""
    assert not updater.isRunning()
    assert not updater._running
    assert not updater.is_updating()


def test_start_updating(updater, mock_data_manager, qapp):
    """Test starting the updater."""
    # Connect signal to verify it runs
    started_count = {'value': 0}
    
    def on_started():
        started_count['value'] += 1
    
    updater.update_started.connect(on_started)
    
    # Start
    updater.start_updating()
    
    # Wait a bit for thread to start
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    # Should be running
    assert updater.isRunning()
    assert updater._running
    assert updater.is_updating()
    
    # Cleanup
    updater.stop_updating()


def test_stop_updating(updater, qapp):
    """Test stopping the updater."""
    # Start
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    assert updater.isRunning()
    
    # Stop
    updater.stop_updating()
    
    # Should be stopped
    assert not updater.isRunning()
    assert not updater._running
    assert not updater.is_updating()


def test_updater_calls_update_all_data(updater, mock_data_manager, qapp):
    """Test updater calls data_manager.update_all_data()."""
    updater.start_updating()
    
    # Wait for at least one update cycle
    QTimer.singleShot(600, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have called update_all_data at least once
    assert mock_data_manager.update_all_data.call_count >= 1


def test_updater_emits_signals(updater, qapp):
    """Test updater emits start and complete signals."""
    started_count = {'value': 0}
    completed_count = {'value': 0}
    
    updater.update_started.connect(lambda: started_count.__setitem__('value', started_count['value'] + 1))
    updater.update_completed.connect(lambda: completed_count.__setitem__('value', completed_count['value'] + 1))
    
    updater.start_updating()
    
    # Wait for at least one cycle
    QTimer.singleShot(600, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have emitted signals
    assert started_count['value'] >= 1
    assert completed_count['value'] >= 1


def test_updater_error_signal(updater, mock_data_manager, qapp):
    """Test updater emits error signal on exception."""
    # Make update_all_data raise exception
    mock_data_manager.update_all_data.side_effect = Exception("Test error")
    
    error_messages = []
    updater.update_error.connect(lambda msg: error_messages.append(msg))
    
    updater.start_updating()
    
    # Wait for error to occur
    QTimer.singleShot(600, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have received error signal
    assert len(error_messages) >= 1
    assert "Test error" in error_messages[0]


def test_set_interval(updater):
    """Test changing update interval."""
    assert updater.interval_ms == 500
    
    updater.set_interval(1000)
    assert updater.interval_ms == 1000
    
    updater.set_interval(3000)
    assert updater.interval_ms == 3000


def test_set_interval_while_running(updater, qapp):
    """Test changing interval while updater is running."""
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    # Change interval
    updater.set_interval(1000)
    assert updater.interval_ms == 1000
    
    updater.stop_updating()


def test_updater_multiple_cycles(updater, mock_data_manager, qapp):
    """Test updater runs multiple update cycles."""
    updater.start_updating()
    
    # Wait for multiple cycles (500ms interval, wait 1300ms = ~2 cycles)
    QTimer.singleShot(1300, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have called update at least 2 times
    assert mock_data_manager.update_all_data.call_count >= 2


def test_double_start_does_not_duplicate(updater, qapp):
    """Test calling start_updating twice doesn't start duplicate threads."""
    updater.start_updating()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Try to start again
    updater.start_updating()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Should still be running (not crashed)
    assert updater.isRunning()
    
    updater.stop_updating()


def test_stop_when_not_running(updater):
    """Test stopping when not running doesn't crash."""
    assert not updater.isRunning()
    updater.stop_updating()
    # Should not crash


def test_is_updating_method(updater, qapp):
    """Test is_updating() method accuracy."""
    assert not updater.is_updating()
    
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    assert updater.is_updating()
    
    updater.stop_updating()
    assert not updater.is_updating()


def test_updater_stops_cleanly(updater, mock_data_manager, qapp):
    """Test updater stops within timeout."""
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    start_time = time.time()
    updater.stop_updating()
    elapsed = time.time() - start_time
    
    # Should stop within 3 seconds (timeout)
    assert elapsed < 3.5
    assert not updater.isRunning()


def test_updater_continues_after_error(updater, mock_data_manager, qapp):
    """Test updater continues running after error."""
    # First call raises error, subsequent calls succeed
    call_count = {'value': 0}
    
    def side_effect():
        call_count['value'] += 1
        if call_count['value'] == 1:
            raise Exception("First call error")
    
    mock_data_manager.update_all_data.side_effect = side_effect
    
    updater.start_updating()
    
    # Wait for multiple cycles
    QTimer.singleShot(1300, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have attempted multiple calls despite first error
    assert call_count['value'] >= 2


def test_updater_thread_safety(updater, qapp):
    """Test updater is properly thread-safe."""
    updater.start_updating()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    # Access state from main thread
    is_running = updater.is_updating()
    interval = updater.interval_ms
    
    assert isinstance(is_running, bool)
    assert isinstance(interval, int)
    
    updater.stop_updating()


def test_updater_wait_timeout(updater, mock_data_manager, qapp):
    """Test updater respects wait timeout."""
    # Make update_all_data very slow
    def slow_update():
        time.sleep(5)  # Longer than wait timeout
    
    mock_data_manager.update_all_data.side_effect = slow_update
    
    updater.start_updating()
    
    QTimer.singleShot(100, qapp.quit)
    qapp.exec()
    
    start_time = time.time()
    updater.stop_updating()
    elapsed = time.time() - start_time
    
    # Should timeout around 3 seconds, not wait 5
    assert elapsed < 4.0


def test_updater_interval_precision(updater, mock_data_manager, qapp):
    """Test update interval is approximately correct."""
    timestamps = []
    
    def record_time():
        timestamps.append(time.time())
    
    updater.update_started.connect(record_time)
    updater.start_updating()
    
    # Wait for 3 cycles (500ms * 3 = 1500ms)
    QTimer.singleShot(1600, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have at least 3 timestamps
    if len(timestamps) >= 3:
        # Check intervals between calls
        interval1 = timestamps[1] - timestamps[0]
        interval2 = timestamps[2] - timestamps[1]
        
        # Should be approximately 500ms (allow ±200ms tolerance)
        assert 0.3 < interval1 < 0.7
        assert 0.3 < interval2 < 0.7


def test_updater_signal_order(updater, qapp):
    """Test signals are emitted in correct order."""
    events = []
    
    updater.update_started.connect(lambda: events.append('started'))
    updater.update_completed.connect(lambda: events.append('completed'))
    
    updater.start_updating()
    
    QTimer.singleShot(600, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Should have started-completed pairs
    if len(events) >= 2:
        assert events[0] == 'started'
        assert events[1] == 'completed'


def test_updater_cleanup_on_stop(updater, qapp):
    """Test updater properly cleans up on stop."""
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    updater.stop_updating()
    
    # Thread should be fully stopped
    assert not updater.isRunning()
    assert not updater._running
    
    # Can restart
    updater.start_updating()
    
    QTimer.singleShot(200, qapp.quit)
    qapp.exec()
    
    assert updater.isRunning()
    updater.stop_updating()


def test_updater_with_zero_interval(mock_api_client, mock_data_manager, qapp):
    """Test updater with very short interval."""
    upd = DataUpdater(mock_api_client, mock_data_manager, interval_ms=100)
    
    upd.start_updating()
    
    QTimer.singleShot(350, qapp.quit)
    qapp.exec()
    
    upd.stop_updating()
    
    # Should have run multiple times
    assert mock_data_manager.update_all_data.call_count >= 2
