"""Main Window for PySide6 Blockchain Simulator."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QTabWidget
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
        self.setFixedSize(1200, 800)
        
        self._setup_ui()
        self._setup_connections()
        self._check_connection()
    
    def _setup_ui(self):
        """Setup UI components."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab Widget (no toolbar)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add pages as tabs
        from ui.pages.dashboard_page import DashboardPage
        from ui.pages.nodes_page import NodesPage
        from ui.pages.network_page import NetworkMapPage
        from ui.pages.blockchain_page import BlockchainExplorerPage
        from ui.pages.pbft_page import PBFTPage
        from ui.widgets.attack_panel_widget import AttackPanelWidget
        from ui.widgets.metrics_widget import MetricsWidget
        from ui.widgets.pbft_widget import PBFTWidget
        
        # Create widgets that will be used in dashboard
        self.attack_panel_widget = AttackPanelWidget()
        self.metrics_widget = MetricsWidget(self.data_manager)
        self.pbft_widget = PBFTWidget()
        
        # Create dashboard with widgets
        self.dashboard_page = DashboardPage(
            self.data_manager,
            self.attack_panel_widget,
            self.metrics_widget,
            self.pbft_widget
        )
        self.nodes_page = NodesPage(self.data_manager)
        self.network_page = NetworkMapPage(self.data_manager)
        self.blockchain_page = BlockchainExplorerPage(self.data_manager)
        self.pbft_page = PBFTPage(self.pbft_widget)
        
        self.tabs.addTab(self.dashboard_page, "📊 Dashboard")
        self.tabs.addTab(self.nodes_page, "🖥️ Nodes")
        self.tabs.addTab(self.network_page, "🗺️ Network Map")
        self.tabs.addTab(self.blockchain_page, "⛓️ Blockchain")
        self.tabs.addTab(self.pbft_page, "📨 PBFT Messages")
        
        # Connect dashboard button signals
        self.dashboard_page.start_clicked.connect(self._on_start)
        self.dashboard_page.stop_clicked.connect(self._on_stop)
        self.dashboard_page.reset_clicked.connect(self._on_reset)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_label = QLabel("🔴 Disconnected")
        self.update_label = QLabel("Last update: Never")
        
        self.status_bar.addPermanentWidget(self.connection_label)
        self.status_bar.addPermanentWidget(self.update_label)
    
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.data_manager.connection_error.connect(self._on_connection_error)
        self.updater.update_completed.connect(self._on_update_completed)
        
        # Attack panel connections
        self.attack_panel_widget.attack_triggered.connect(self._on_attack_triggered)
        
        # Node list updates
        self.data_manager.nodes_updated.connect(self.attack_panel_widget.update_node_list)
        
        # PBFT updates
        self.data_manager.pbft_updated.connect(self.pbft_widget.update_pbft_status)
        self.data_manager.messages_updated.connect(self.pbft_widget.update_messages)
    
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
            self.dashboard_page.btn_start.setEnabled(False)
            self.dashboard_page.btn_stop.setEnabled(True)
            self.status_bar.showMessage("Simulator started", 3000)
            self.updater.start_updating()
        else:
            self.status_bar.showMessage("Failed to start simulator", 3000)
    
    def _on_stop(self):
        """Handle stop button."""
        result = self.api_client.stop_simulator()
        if result and 'error' not in result:
            self.dashboard_page.btn_start.setEnabled(True)
            self.dashboard_page.btn_stop.setEnabled(False)
            self.status_bar.showMessage("Simulator stopped", 3000)
            self.updater.stop_updating()
        else:
            self.status_bar.showMessage("Failed to stop simulator", 3000)
    
    def _on_reset(self):
        """Handle reset button."""
        result = self.api_client.reset_simulator()
        if result and 'error' not in result:
            self.dashboard_page.btn_start.setEnabled(True)
            self.dashboard_page.btn_stop.setEnabled(False)
            self.status_bar.showMessage("Simulator reset", 3000)
            
            self.updater.stop_updating()
            self.data_manager.clear_cache()
            self.dashboard_page.clear_display()
            self.nodes_page.clear_display()
            self.network_page.clear_network()
            self.blockchain_page.clear_display()
            self.metrics_widget.clear_display()
            self.pbft_page.clear_display()
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
        target = params.get('target')
        result = self.api_client.trigger_attack(attack_type, target, params)
        
        if result and 'error' not in result:
            self.status_bar.showMessage(f"{attack_type.upper()} attack started", 3000)
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Connection error'
            self.status_bar.showMessage(f"Failed to trigger attack: {error_msg}", 5000)
    
    def closeEvent(self, event):
        """Handle window close."""
        self.updater.stop_updating()
        event.accept()