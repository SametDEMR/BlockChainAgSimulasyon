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
        from ui.pages.network_page import NetworkMapPage
        from ui.pages.blockchain_page import BlockchainExplorerPage
        
        self.dashboard_page = DashboardPage(self.data_manager)
        self.nodes_page = NodesPage(self.data_manager)
        self.network_page = NetworkMapPage(self.data_manager)
        self.blockchain_page = BlockchainExplorerPage(self.data_manager)
        
        self.tabs.addTab(self.dashboard_page, "📊 Dashboard")
        self.tabs.addTab(self.nodes_page, "🖥️ Nodes")
        self.tabs.addTab(self.network_page, "🗺️ Network Map")
        self.tabs.addTab(self.blockchain_page, "⛓️ Blockchain")
        
        # Dock Widgets
        self._create_attack_panel_dock()
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
    
    def _create_attack_panel_dock(self):
        """Create attack control panel as left dock widget."""
        from ui.widgets.attack_panel_widget import AttackPanelWidget
        
        # Create dock widget
        self.attack_panel_dock = QDockWidget("Attack Control Panel", self)
        self.attack_panel_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create attack panel widget
        self.attack_panel_widget = AttackPanelWidget()
        
        # Add to dock
        self.attack_panel_dock.setWidget(self.attack_panel_widget)
        
        # Add dock to main window (left side)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.attack_panel_dock)
    
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
        
        # Attack panel connections
        self.attack_panel_widget.attack_triggered.connect(self._on_attack_triggered)
        self.attack_panel_widget.attack_stop_requested.connect(self._on_attack_stop_requested)
        
        # Node list updates
        self.data_manager.nodes_updated.connect(self.attack_panel_widget.update_node_list)
    
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
            self.network_page.clear_network()
            self.blockchain_page.clear_display()
            self.metrics_widget.clear_display()
            self.attack_panel_widget.clear_active_attacks()
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
    
    def _on_attack_triggered(self, attack_type: str, params: dict):
        """Handle attack trigger request."""
        # Extract target if it exists
        target = params.get('target')
        # Pass parameters properly
        result = self.api_client.trigger_attack(attack_type, target, params)
        
        if result and 'error' not in result:
            # Attack successfully triggered
            attack_id = result.get('attack_id', '')
            if attack_id:
                # Add to active attacks display
                attack_data = {
                    'id': attack_id,
                    'type': attack_type,
                    'target': params.get('target', 'N/A'),
                    'progress': 0.0,
                    'remaining_time': result.get('duration', 30)
                }
                self.attack_panel_widget.add_active_attack(attack_data)
                self.status_bar.showMessage(f"{attack_type.upper()} attack started", 3000)
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Connection error'
            self.status_bar.showMessage(f"Failed to trigger attack: {error_msg}", 5000)
    
    def _on_attack_stop_requested(self, attack_id: str):
        """Handle attack stop request."""
        result = self.api_client.stop_attack(attack_id)
        
        if result and 'error' not in result:
            # Attack stopped successfully
            self.attack_panel_widget.remove_active_attack(attack_id)
            self.status_bar.showMessage(f"Attack stopped", 3000)
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Connection error'
            self.status_bar.showMessage(f"Failed to stop attack: {error_msg}", 5000)
    
    def closeEvent(self, event):
        """Handle window close."""
        self.updater.stop_updating()
        event.accept()
