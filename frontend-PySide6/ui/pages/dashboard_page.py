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
        """Setup 3x2 grid layout."""
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        # ROW 1: Attack Panel | Response Graph | Overview+Health
        # Column 0: Attack Panel (fixed width)
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 0, 0)

        # Column 1: Response Time Graph (expandable)
        graph_panel = self._create_graph_panel()
        main_layout.addWidget(graph_panel, 0, 1)

        # Column 2: Overview + Health (fixed width)
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 0, 2)

        # ROW 2: Active Attacks | Node Status Cards (wide)
        # Column 0: Active Attacks from attack panel
        if hasattr(self.attack_panel_widget, 'active_attacks_group'):
            main_layout.addWidget(self.attack_panel_widget.active_attacks_group, 1, 0)

        # Column 1-2: Node Status Cards (spanning 2 columns)
        cards_panel = self._create_cards_panel()
        main_layout.addWidget(cards_panel, 1, 1, 1, 2)  # row, col, rowspan, colspan

        # Column stretches
        main_layout.setColumnStretch(0, 0)  # Fixed width
        main_layout.setColumnStretch(1, 2)  # Expandable
        main_layout.setColumnStretch(2, 0)  # Fixed width

        # Row stretches - İki satır daha dengeli olacak
        main_layout.setRowStretch(0, 1)  # Top row
        main_layout.setRowStretch(1, 1)  # Bottom row

    def _create_left_panel(self):
        """Create left panel with attack controls (without active attacks)."""
        panel = QWidget()
        panel.setFixedWidth(240)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add attack panel toolbox only (active attacks moved to bottom)
        scroll = QScrollArea()
        scroll.setWidget(self.attack_panel_widget.toolbox)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        layout.addWidget(scroll)

        return panel

    def _create_graph_panel(self):
        """Create graph panel with response time graph and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)

        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        self.btn_start = QPushButton("▶ Start")
        self.btn_stop = QPushButton("⏸ Stop")
        self.btn_reset = QPushButton("🔄 Reset")

        self.btn_start.setFixedHeight(30)
        self.btn_stop.setFixedHeight(30)
        self.btn_reset.setFixedHeight(30)

        self.btn_start.setMinimumWidth(80)
        self.btn_stop.setMinimumWidth(80)
        self.btn_reset.setMinimumWidth(80)
        self.btn_stop.setEnabled(False)

        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)

        buttons_layout.addWidget(self.btn_start)
        buttons_layout.addWidget(self.btn_stop)
        buttons_layout.addWidget(self.btn_reset)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Graph label
        graph_label = QLabel("Response Time (Real-time)")
        graph_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(graph_label)

        # Plot widget
        if hasattr(self.metrics_widget, 'plot_widget'):
            layout.addWidget(self.metrics_widget.plot_widget, 1)

        return panel

    def _create_cards_panel(self):
        """Create node status cards panel (wide, 3-4 columns)."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)

        # Header
        cards_label = QLabel("Node Status Cards")
        cards_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(cards_label)

        # Cards container - Scroll sadece gerekirse
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(2)

        # Add cards grid
        if hasattr(self.metrics_widget, 'cards_grid'):
            cards_layout.addLayout(self.metrics_widget.cards_grid)
        cards_layout.addStretch()

        scroll.setWidget(cards_container)
        layout.addWidget(scroll, 1)

        return panel

    def _create_right_panel(self):
        """Create right panel with overview and health."""
        panel = QWidget()
        panel.setFixedWidth(220)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Overview Cards
        overview_group = self._create_overview_group()
        layout.addWidget(overview_group)

        # Network Health
        if hasattr(self.metrics_widget, 'health_section'):
            layout.addWidget(self.metrics_widget.health_section)

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
        layout.setSpacing(3)
        layout.setContentsMargins(3, 5, 3, 3)

        # Total Nodes
        total_widget = QWidget()
        total_layout = QVBoxLayout(total_widget)
        total_layout.setContentsMargins(2, 0, 2, 0)
        total_layout.setSpacing(1)

        total_label = QLabel("Total Nodes")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("font-size: 9px;")

        self.lcd_total_nodes = QLCDNumber()
        self.lcd_total_nodes.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_total_nodes.setDigitCount(3)
        self.lcd_total_nodes.setFixedHeight(24)
        self.lcd_total_nodes.display(0)

        total_layout.addWidget(total_label)
        total_layout.addWidget(self.lcd_total_nodes)
        layout.addWidget(total_widget)

        # Active Nodes
        active_widget = QWidget()
        active_layout = QVBoxLayout(active_widget)
        active_layout.setContentsMargins(2, 0, 2, 0)
        active_layout.setSpacing(1)

        active_label = QLabel("Active Nodes")
        active_label.setAlignment(Qt.AlignCenter)
        active_label.setStyleSheet("font-size: 9px;")

        self.lcd_active_nodes = QLCDNumber()
        self.lcd_active_nodes.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_active_nodes.setDigitCount(3)
        self.lcd_active_nodes.setFixedHeight(24)
        self.lcd_active_nodes.display(0)

        active_layout.addWidget(active_label)
        active_layout.addWidget(self.lcd_active_nodes)
        layout.addWidget(active_widget)

        # Chain Length
        chain_widget = QWidget()
        chain_layout = QVBoxLayout(chain_widget)
        chain_layout.setContentsMargins(2, 0, 2, 0)
        chain_layout.setSpacing(1)

        chain_label = QLabel("Chain Length")
        chain_label.setAlignment(Qt.AlignCenter)
        chain_label.setStyleSheet("font-size: 9px;")

        self.lcd_chain_length = QLCDNumber()
        self.lcd_chain_length.setSegmentStyle(QLCDNumber.Flat)
        self.lcd_chain_length.setDigitCount(3)
        self.lcd_chain_length.setFixedHeight(24)
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