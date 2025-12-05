"""Real-time data updater thread."""
from PySide6.QtCore import QThread, Signal
import time


class DataUpdater(QThread):
    """Background thread for polling API data."""
    
    # Signals
    update_started = Signal()
    update_completed = Signal()
    update_error = Signal(str)
    
    def __init__(self, api_client, data_manager, interval_ms: int = 2000):
        """Initialize updater.
        
        Args:
            api_client: APIClient instance
            data_manager: DataManager instance
            interval_ms: Update interval in milliseconds
        """
        super().__init__()
        self.api_client = api_client
        self.data_manager = data_manager
        self.interval_ms = interval_ms
        self._running = False
    
    def run(self):
        """Background thread main loop."""
        self._running = True
        
        while self._running:
            try:
                self.update_started.emit()
                
                # Update all data through data manager
                self.data_manager.update_all_data()
                
                self.update_completed.emit()
                
            except Exception as e:
                self.update_error.emit(str(e))
            
            # Sleep for interval (check _running every 100ms)
            elapsed = 0
            while elapsed < self.interval_ms and self._running:
                self.msleep(100)
                elapsed += 100
    
    def start_updating(self):
        """Start the update loop."""
        if not self.isRunning():
            self._running = True
            self.start()
    
    def stop_updating(self):
        """Stop the update loop."""
        self._running = False
        self.wait(3000)  # Wait max 3 seconds
    
    def set_interval(self, interval_ms: int):
        """Set update interval.
        
        Args:
            interval_ms: New interval in milliseconds
        """
        self.interval_ms = interval_ms
    
    def is_updating(self) -> bool:
        """Check if updater is running.
        
        Returns:
            True if running
        """
        return self._running and self.isRunning()
