"""Main Window for PySide6 Blockchain Simulator."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, api_client, data_manager, updater, backend_thread=None):
        """Initialize main window.
        
        Args:
            api_client: API client instance
            data_manager: Data manager instance
            updater: Data updater instance
            backend_thread: Backend thread instance (None for external backend)
        """
        super().__init__()
        
        self.api_client = api_client
        self.data_manager = data_manager
        self.updater = updater
        self.backend_thread = backend_thread
        self._backend_starting = False
        
        self.setWindowTitle("Blockchain Attack Simulator")
        self.setFixedSize(1200, 800)
        
        self._setup_ui()
        self._setup_connections()
        
        # Backend entegrasyonu varsa başlat
        if self.backend_thread:
            self._start_embedded_backend()
        else:
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
        
        self.status_bar.addPermanentWidget(self.connection_label)
    
    
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
        
        # Backend thread signals (if embedded)
        if self.backend_thread:
            self.backend_thread.started.connect(self._on_backend_started)
            self.backend_thread.error.connect(self._on_backend_error)
            self.backend_thread.stopped.connect(self._on_backend_stopped)
    
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
            
            # Reset sonrası butonları enable et (hiçbir aktif attack yok)
            self.attack_panel_widget.update_button_states(False)
        else:
            self.status_bar.showMessage("Failed to reset simulator", 3000)
    
    def _on_connection_error(self, error):
        """Handle connection error."""
        self.connection_label.setText("🔴 Connection Error")
        self.connection_label.setStyleSheet("color: red;")
        self.status_bar.showMessage(f"Error: {error}", 5000)
    
    def _on_update_completed(self):
        """Handle update completion."""
        self._check_connection()
        # Her update'te button state'lerini kontrol et
        self._update_attack_button_states()
    
    def _update_attack_button_states(self):
        """
        Aktif attack durumuna göre attack panel butonlarını güncelle.
        API'dan active attacks bilgisini çekerek butonları enable/disable eder.
        """
        # API'dan tüm attack status'unu çek
        attack_status = self.api_client.get_all_attacks_status()
        
        if attack_status and 'error' not in attack_status:
            active_attacks = attack_status.get('active_attacks', [])
            has_active = len(active_attacks) > 0
            
            # Attack panel'in butonlarını güncelle
            self.attack_panel_widget.update_button_states(has_active)
        else:
            # Hata durumunda butonları enable et (varsayılan)
            self.attack_panel_widget.update_button_states(False)
    
    def _on_attack_triggered(self, attack_type: str, params: dict):
        """Handle attack trigger request."""
        target = params.get('target')
        result = self.api_client.trigger_attack(attack_type, target, params)
        
        if result and 'error' not in result:
            self.status_bar.showMessage(f"{attack_type.upper()} attack started", 3000)
            # Buton state'lerini güncelle
            self._update_attack_button_states()
        else:
            # Hata durumu - 409 Conflict için özel mesaj
            if result and result.get('error') == 'conflict':
                conflict_msg = result.get('message', 'An attack is already active')
                self.status_bar.showMessage(f"⚠️ {conflict_msg}", 5000)
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Connection error'
                self.status_bar.showMessage(f"Failed to trigger attack: {error_msg}", 5000)
    
    def _start_embedded_backend(self):
        """Start embedded backend in thread."""
        if self._backend_starting:
            return
        
        self._backend_starting = True
        self.status_bar.showMessage("Starting embedded backend...", 0)
        self.connection_label.setText("🟡 Starting Backend...")
        self.connection_label.setStyleSheet("color: orange;")
        
        # Backend thread'ini başlat
        self.backend_thread.start()
    
    @Slot(int)
    def _on_backend_started(self, port: int):
        """Handle backend started signal."""
        self._backend_starting = False
        
        # API client'ın base URL'ini güncelle
        base_url = f"http://127.0.0.1:{port}"
        self.api_client.set_base_url(base_url)
        
        # Data manager'ı da güncelle (api_client referansı)
        self.data_manager.api_client = self.api_client
        
        self.status_bar.showMessage(f"✅ Backend started on port {port}", 5000)
        self.connection_label.setText("🟢 Backend Ready")
        self.connection_label.setStyleSheet("color: green;")
        
        # Connection check
        self._check_connection()
    
    @Slot(str)
    def _on_backend_error(self, error: str):
        """Handle backend error signal."""
        self._backend_starting = False
        
        self.status_bar.showMessage(f"❌ Backend error: {error}", 0)
        self.connection_label.setText("🔴 Backend Error")
        self.connection_label.setStyleSheet("color: red;")
        
        # Hata mesajı göster
        QMessageBox.critical(
            self,
            "Backend Error",
            f"Failed to start embedded backend:\n\n{error}\n\nThe application will close."
        )
        
        self.close()
    
    @Slot()
    def _on_backend_stopped(self):
        """Handle backend stopped signal."""
        self.status_bar.showMessage("Backend stopped", 3000)
        self.connection_label.setText("🔴 Backend Stopped")
        self.connection_label.setStyleSheet("color: red;")
    
    def closeEvent(self, event):
        """Handle window close."""
        # Data updater'ı durdur
        self.updater.stop_updating()
        
        # Embedded backend varsa onu da durdur
        if self.backend_thread and self.backend_thread.isRunning():
            self.status_bar.showMessage("Stopping backend...")
            self.backend_thread.stop()
            self.backend_thread.wait(5000)  # Max 5 saniye bekle
        
        event.accept()