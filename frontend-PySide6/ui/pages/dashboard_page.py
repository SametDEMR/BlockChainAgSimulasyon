"""Dashboard Page - Main overview."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLCDNumber, QListWidget, QProgressBar
)
from PySide6.QtCore import Qt


class DashboardPage(QWidget):
    """Dashboard page showing system overview."""
    
    def __init__(self, data_manager):
        """Initialize dashboard page.
        
        Args:
            data_manager: DataManager instance
        """
        super().__init__()
        
        self.data_manager = data_manager
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # System metrics
        metrics_group = self._create_metrics_group()
        layout.addWidget(metrics_group)
        
        # PBFT status
        pbft_group = self._create_pbft_group()
        layout.addWidget(pbft_group)
        
        # Recent activity
        activity_group = self._create_activity_group()
        layout.addWidget(activity_group, stretch=1)
    
    def _create_metrics_group(self):
        """Create system metrics group."""
        group = QGroupBox("System Overview")
        layout = QHBoxLayout(group)
        
        # Nodes
        self.lcd_nodes = self._create_metric_display("Total Nodes", "10")
        layout.addWidget(self.lcd_nodes)
        
        # Active nodes
        self.lcd_active = self._create_metric_display("Active Nodes", "10")
        layout.addWidget(self.lcd_active)
        
        # Chain length
        self.lcd_chain = self._create_metric_display("Chain Length", "0")
        layout.addWidget(self.lcd_chain)
        
        # Health
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)
        health_layout.addWidget(QLabel("Network Health"))
        self.health_bar = QProgressBar()
        self.health_bar.setMinimum(0)
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(100)
        self.health_bar.setTextVisible(True)
        self.health_bar.setFormat("%v%")
        health_layout.addWidget(self.health_bar)
        layout.addWidget(health_widget)
        
        return group
    
    def _create_metric_display(self, label, initial_value):
        """Create metric display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(label))
        
        lcd = QLCDNumber()
        lcd.setSegmentStyle(QLCDNumber.Flat)
        lcd.setDigitCount(5)
        lcd.display(initial_value)
        lcd.setMinimumHeight(60)
        layout.addWidget(lcd)
        
        return widget
    
    def _create_pbft_group(self):
        """Create PBFT status group."""
        group = QGroupBox("PBFT Consensus")
        layout = QVBoxLayout(group)
        
        info_layout = QHBoxLayout()
        
        self.lbl_primary = QLabel("Primary: N/A")
        self.lbl_view = QLabel("View: N/A")
        self.lbl_consensus = QLabel("Consensus: N/A")
        self.lbl_validators = QLabel("Validators: N/A")
        
        info_layout.addWidget(self.lbl_primary)
        info_layout.addWidget(self.lbl_view)
        info_layout.addWidget(self.lbl_consensus)
        info_layout.addWidget(self.lbl_validators)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        return group
    
    def _create_activity_group(self):
        """Create recent activity group."""
        group = QGroupBox("Recent Activity")
        layout = QVBoxLayout(group)
        
        self.activity_list = QListWidget()
        layout.addWidget(self.activity_list)
        
        return group
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.data_manager.status_updated.connect(self._on_status_updated)
        self.data_manager.nodes_updated.connect(self._on_nodes_updated)
        self.data_manager.blockchain_updated.connect(self._on_blockchain_updated)
        self.data_manager.pbft_updated.connect(self._on_pbft_updated)
    
    def _on_status_updated(self, status):
        """Handle status update."""
        nodes = status.get('total_nodes', 0)
        active = status.get('active_nodes', 0)
        
        self.lcd_nodes.findChild(QLCDNumber).display(nodes)
        self.lcd_active.findChild(QLCDNumber).display(active)
        
        # Calculate health
        if nodes > 0:
            health = int((active / nodes) * 100)
            self.health_bar.setValue(health)
        
        # Add to activity
        if status.get('running'):
            self._add_activity("✓ Simulator running")
    
    def _on_nodes_updated(self, nodes):
        """Handle nodes update."""
        self.lcd_nodes.findChild(QLCDNumber).display(len(nodes))
        
        # Count active nodes
        active_count = sum(1 for n in nodes if n.get('status') == 'healthy')
        self.lcd_active.findChild(QLCDNumber).display(active_count)
    
    def _on_blockchain_updated(self, blockchain):
        """Handle blockchain update."""
        chain_length = blockchain.get('chain_length', 0)
        self.lcd_chain.findChild(QLCDNumber).display(chain_length)
        
        # Add to activity
        if chain_length > 0:
            self._add_activity(f"📦 Block #{chain_length} added")
    
    def _on_pbft_updated(self, pbft):
        """Handle PBFT update."""
        if pbft.get('enabled'):
            primary = pbft.get('primary', 'N/A')
            view = pbft.get('current_view', 'N/A')
            consensus = pbft.get('total_consensus_reached', 'N/A')
            validators = pbft.get('total_validators', 'N/A')
            
            self.lbl_primary.setText(f"Primary: {primary}")
            self.lbl_view.setText(f"View: {view}")
            self.lbl_consensus.setText(f"Consensus: {consensus}")
            self.lbl_validators.setText(f"Validators: {validators}")
            
            # Add to activity
            if consensus and consensus != 'N/A':
                self._add_activity(f"✓ PBFT consensus reached")
    
    def _add_activity(self, message):
        """Add activity message."""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.activity_list.insertItem(0, f"[{timestamp}] {message}")
        
        # Keep only last 20 items
        while self.activity_list.count() > 20:
            self.activity_list.takeItem(self.activity_list.count() - 1)
    
    def clear_display(self):
        """Clear all displays."""
        self.lcd_nodes.findChild(QLCDNumber).display(0)
        self.lcd_active.findChild(QLCDNumber).display(0)
        self.lcd_chain.findChild(QLCDNumber).display(0)
        self.health_bar.setValue(0)
        
        self.lbl_primary.setText("Primary: N/A")
        self.lbl_view.setText("View: N/A")
        self.lbl_consensus.setText("Consensus: N/A")
        self.lbl_validators.setText("Validators: N/A")
        
        self.activity_list.clear()
