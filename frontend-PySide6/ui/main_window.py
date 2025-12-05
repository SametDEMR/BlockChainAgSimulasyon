"""Main Window for PySide6 Blockchain Simulator."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, api_client, data_manager, updater):
        """Initialize main window.
        
        Args:
            api_client: APIClient instance
            data_manager: DataManager instance
            updater: DataUpdater instance
        """
        super().__init__()
        
        self.api_client = api_client
        self.data_manager = data_manager
        self.updater = updater
        
        self.setWindowTitle("Blockchain Attack Simulator")
        self.setMinimumSize(1200, 800)
        
        self._setup_ui()
        self._setup_connections()
        
        # Check backend connection on startup
        self._check_connection()
    
    def _setup_ui(self):
        """Setup UI components."""
        # Central widget with stacked pages
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        # Toolbar
        toolbar_layout = self._create_toolbar()
        layout.addLayout(toolbar_layout)
        
        # Stacked widget for pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Add dashboard page
        from ui.pages.dashboard_page import DashboardPage
        self.dashboard_page = DashboardPage(self.data_manager)
        self.stack.addWidget(self.dashboard_page)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_label = QLabel("🔴 Disconnected")
        self.update_label = QLabel("Last update: Never")
        
        self.status_bar.addPermanentWidget(self.connection_label)
        self.status_bar.addPermanentWidget(self.update_label)
    
    def _create_toolbar(self):
        """Create toolbar with control buttons."""
        layout = QHBoxLayout()
        
        # Control buttons
        self.btn_start = QPushButton("▶ Start")
        self.btn_stop = QPushButton("⏸ Stop")
        self.btn_reset = QPushButton("🔄 Reset")
        
        self.btn_start.setMinimumWidth(100)
        self.btn_stop.setMinimumWidth(100)
        self.btn_reset.setMinimumWidth(100)
        
        self.btn_stop.setEnabled(False)
        
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_reset)
        layout.addStretch()
        
        return layout
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Button connections
        self.btn_start.clicked.connect(self._on_start)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_reset.clicked.connect(self._on_reset)
        
        # Data manager connections - status_updated removed
        self.data_manager.connection_error.connect(self._on_connection_error)
        
        # Updater connections
        self.updater.update_completed.connect(self._on_update_completed)
    
    def _check_connection(self):
        """Check backend connection."""
        if self.api_client.is_connected():
            self.connection_label.setText("🟢 Connected")
            self.connection_label.setStyleSheet("color: green;")
        else:
            self.connection_label.setText("🔴 Disconnected")
            self.connection_label.setStyleSheet("color: red;")
    
    def _on_start(self):
        """Handle start button."""
        result = self.api_client.start_simulator()
        if result and 'error' not in result:
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.status_bar.showMessage("Simulator started", 3000)
            
            # Start updater
            self.updater.start_updating()
        else:
            self.status_bar.showMessage("Failed to start simulator", 3000)
    
    def _on_stop(self):
        """Handle stop button."""
        result = self.api_client.stop_simulator()
        if result and 'error' not in result:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.status_bar.showMessage("Simulator stopped", 3000)
            
            # Stop updater
            self.updater.stop_updating()
        else:
            self.status_bar.showMessage("Failed to stop simulator", 3000)
    
    def _on_reset(self):
        """Handle reset button."""
        result = self.api_client.reset_simulator()
        if result and 'error' not in result:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.status_bar.showMessage("Simulator reset", 3000)
            
            # Stop updater and clear cache
            self.updater.stop_updating()
            self.data_manager.clear_cache()
            self.dashboard_page.clear_display()
        else:
            self.status_bar.showMessage("Failed to reset simulator", 3000)
    
    def _on_connection_error(self, error):
        """Handle connection error."""
        self.connection_label.setText("🔴 Connection Error")
        self.connection_label.setStyleSheet("color: red;")
        self.status_bar.showMessage(f"Error: {error}", 5000)
    
    def _on_update_completed(self):
        """Handle update completion."""
        from datetime import datetime
        self.update_label.setText(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Check connection status
        self._check_connection()
    
    def closeEvent(self, event):
        """Handle window close."""
        self.updater.stop_updating()
        event.accept()
