"""Dashboard Page - 3 Panel Layout."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QSplitter,
    QLabel, QLCDNumber, QProgressBar, QScrollArea, QPushButton, QGridLayout
)
from PySide6.QtCore import Qt, Signal


class DashboardPage(QWidget):
    """Dashboard page with 3-panel layout."""
    
    # Signals for button clicks
    start_clicked = Signal()
    stop_clicked = Signal()
    reset_clicked = Signal()
    
    def __init__(self, data_manager, attack_panel_widget, metrics_widget, pbft_widget):
        """Initialize dashboard page.
        
        Args:
            data_manager: DataManager instance
            attack_panel_widget: Attack control panel widget
            metrics_widget: Metrics widget
            pbft_widget: PBFT widget
        """
        super().__init__()
        
        self.data_manager = data_manager
        self.attack_panel_widget = attack_panel_widget
        self.metrics_widget = metrics_widget
        self.pbft_widget = pbft_widget
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup 3-panel layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # LEFT PANEL (260px) - Attack Controls
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)
        
        # CENTER PANEL (600px) - Graph + Cards
        center_panel = self._create_center_panel()
        main_layout.addWidget(center_panel, stretch=1)
        
        # RIGHT PANEL (300px) - Overview + Metrics
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)
    
    def _create_left_panel(self):
        """Create left panel with attack controls."""
        panel = QWidget()
        panel.setFixedWidth(260)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add attack panel widget in scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.attack_panel_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addWidget(scroll)
        
        return panel
    
    def _create_center_panel(self):
        """Create center panel with graph and cards."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Splitter for graph (top) and cards (bottom)
        splitter = QSplitter(Qt.Vertical)
        
        # TOP: Response Time Graph (from metrics_widget)
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(5, 5, 5, 5)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start")
        self.btn_stop = QPushButton("⏸ Stop")
        self.btn_reset = QPushButton("🔄 Reset")
        
        self.btn_start.setMinimumWidth(100)
        self.btn_stop.setMinimumWidth(100)
        self.btn_reset.setMinimumWidth(100)
        self.btn_stop.setEnabled(False)
        
        # Connect buttons to signals
        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
        
        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_stop)
        buttons_layout.addWidget(self.btn_reset)
        buttons_layout.addStretch()
        
        graph_layout.addLayout(buttons_layout)
        
        graph_label = QLabel("Response Time (Real-time)")
        graph_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        graph_layout.addWidget(graph_label)
        
        # Add plot widget from metrics
        if hasattr(self.metrics_widget, 'plot_widget'):
            graph_layout.addWidget(self.metrics_widget.plot_widget)

        splitter.addWidget(graph_widget)

        # BOTTOM: Node Status Cards (from metrics_widget)
        # Create scroll area for cards
        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(5, 5, 5, 5)

        cards_label = QLabel("Node Status Cards")
        cards_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        cards_layout.addWidget(cards_label)

        # Add cards grid from metrics widget directly to layout
        if hasattr(self.metrics_widget, 'cards_grid'):
            # Add the grid layout directly, don't try to setLayout
            cards_layout.addLayout(self.metrics_widget.cards_grid)
        cards_layout.addStretch()

        cards_scroll.setWidget(cards_container)
        splitter.addWidget(cards_scroll)

        # Set initial sizes (50-50 split)
        splitter.setSizes([350, 350])

        layout.addWidget(splitter)

        return panel

    def _create_right_panel(self):
        """Create right panel with overview and metrics."""
        panel = QWidget()
        panel.setFixedWidth(300)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Overview Cards
        overview_group = self._create_overview_group()
        layout.addWidget(overview_group)

        # Network Health (from metrics_widget)
        if hasattr(self.metrics_widget, 'health_section'):
            layout.addWidget(self.metrics_widget.health_section)

        # System Metrics (from metrics_widget)
        if hasattr(self.metrics_widget, 'metrics_section'):
            layout.addWidget(self.metrics_widget.metrics_section)
        
        layout.addStretch()

        scroll.setWidget(content)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)

        return panel

    def _create_overview_group(self):
        """Create overview cards (Total Nodes, Active Nodes, Chain Length)."""
        group = QGroupBox("Overview")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        # Total Nodes
        total_widget = QWidget()
        total_layout = QVBoxLayout(total_widget)
        total_layout.setContentsMargins(5, 2, 5, 2)
        total_label = QLabel("Total Nodes")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("font-size: 11px;")
        self.lcd_total_nodes = QLCDNumber()
        self.lcd_total_nodes.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_total_nodes.setDigitCount(3)
        self.lcd_total_nodes.setFixedHeight(35)
        self.lcd_total_nodes.display(0)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.lcd_total_nodes)
        layout.addWidget(total_widget)

        # Active Nodes
        active_widget = QWidget()
        active_layout = QVBoxLayout(active_widget)
        active_layout.setContentsMargins(5, 2, 5, 2)
        active_label = QLabel("Active Nodes")
        active_label.setAlignment(Qt.AlignCenter)
        active_label.setStyleSheet("font-size: 11px;")
        self.lcd_active_nodes = QLCDNumber()
        self.lcd_active_nodes.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_active_nodes.setDigitCount(3)
        self.lcd_active_nodes.setFixedHeight(35)
        self.lcd_active_nodes.display(0)
        active_layout.addWidget(active_label)
        active_layout.addWidget(self.lcd_active_nodes)
        layout.addWidget(active_widget)

        # Chain Length
        chain_widget = QWidget()
        chain_layout = QVBoxLayout(chain_widget)
        chain_layout.setContentsMargins(5, 2, 5, 2)
        chain_label = QLabel("Chain Length")
        chain_label.setAlignment(Qt.AlignCenter)
        chain_label.setStyleSheet("font-size: 11px;")
        self.lcd_chain_length = QLCDNumber()
        self.lcd_chain_length.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_chain_length.setDigitCount(3)
        self.lcd_chain_length.setFixedHeight(35)
        self.lcd_chain_length.display(0)
        chain_layout.addWidget(chain_label)
        chain_layout.addWidget(self.lcd_chain_length)
        layout.addWidget(chain_widget)

        return group

    def _setup_connections(self):
        """Setup signal connections."""
        self.data_manager.status_updated.connect(self._on_status_updated)
        self.data_manager.nodes_updated.connect(self._on_nodes_updated)
        self.data_manager.blockchain_updated.connect(self._on_blockchain_updated)
        self.data_manager.pbft_updated.connect(self._on_pbft_updated)

    def _on_status_updated(self, status):
        """Handle status update."""
        total_nodes = status.get('total_nodes', 0)
        active_nodes = status.get('active_nodes', 0)

        self.lcd_total_nodes.display(total_nodes)
        self.lcd_active_nodes.display(active_nodes)

    def _on_nodes_updated(self, nodes):
        """Handle nodes update."""
        if not nodes:
            return

        total = len(nodes)
        active = sum(1 for n in nodes if n.get('status') == 'healthy')

        self.lcd_total_nodes.display(total)
        self.lcd_active_nodes.display(active)

    def _on_blockchain_updated(self, blockchain):
        """Handle blockchain update."""
        chain_length = blockchain.get('chain_length', 0)
        self.lcd_chain_length.display(chain_length)

    def _on_pbft_updated(self, pbft):
        """Handle PBFT update - removed, now in separate tab."""
        pass

    def clear_display(self):
        """Clear all displays."""
        self.lcd_total_nodes.display(0)
        self.lcd_active_nodes.display(0)
        self.lcd_chain_length.display(0)
