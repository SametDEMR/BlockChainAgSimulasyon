"""Main Window for PySide6 Blockchain Simulator."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QTabWidget, QDockWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, api_client, data_manager, updater):
        """Initialize main window."""
        super().__init__()
        
        self.api_client = api_client
        self.data_manager = data_manager
        self.updater = updater
        
        self.setWindowTitle("Blockchain Attack Simulator")
        self.setMinimumSize(1200, 800)
        
        self._setup_ui()
        self._setup_connections()
        self._check_connection()
    
    def _setup_ui(self):
        """Setup UI components."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        # Toolbar
        toolbar_layout = self._create_toolbar()
        layout.addLayout(toolbar_layout)
        
        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add pages as tabs
        from ui.pages.dashboard_page import DashboardPage
        from ui.pages.nodes_page import NodesPage
        
        self.dashboard_page = DashboardPage(self.data_manager)
        self.nodes_page = NodesPage(self.data_manager)
        
        self.tabs.addTab(self.dashboard_page, "📊 Dashboard")
        self.tabs.addTab(self.nodes_page, "🖥️ Nodes")
        
        # Dock Widgets
        self._create_metrics_dock()
        
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
    
    def _create_metrics_dock(self):
        """Create metrics dashboard as right dock widget."""
        from ui.widgets.metrics_widget import MetricsWidget
        
        # Create dock widget
        self.metrics_dock = QDockWidget("Metrics Dashboard", self)
        self.metrics_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        # Create metrics widget
        self.metrics_widget = MetricsWidget(self.data_manager)
        
        # Add to dock
        self.metrics_dock.setWidget(self.metrics_widget)
        
        # Add dock to main window (right side)
        self.addDockWidget(Qt.RightDockWidgetArea, self.metrics_dock)
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.btn_start.clicked.connect(self._on_start)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_reset.clicked.connect(self._on_reset)
        
        self.data_manager.connection_error.connect(self._on_connection_error)
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
            
            self.updater.stop_updating()
            self.data_manager.clear_cache()
            self.dashboard_page.clear_display()
            self.nodes_page.clear_display()
            self.metrics_widget.clear_display()
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
        self._check_connection()
    
    def closeEvent(self, event):
        """Handle window close."""
        self.updater.stop_updating()
        event.accept()
