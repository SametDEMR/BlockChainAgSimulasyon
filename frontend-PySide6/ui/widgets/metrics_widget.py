"""Metrics Dashboard Widget - Right Dock."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QProgressBar, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Slot


class MetricsWidget(QWidget):
    """Metrics dashboard widget for right dock.
    
    Shows:
    - Real-time response time graph
    - Node status cards
    - Network health bars
    - System metrics
    """
    
    def __init__(self, data_manager=None):
        """Initialize metrics widget.
        
        Args:
            data_manager: DataManager instance for updates
        """
        super().__init__()
        self.data_manager = data_manager
        
        self._setup_ui()
        if self.data_manager:
            self._setup_connections()
    
    def _setup_ui(self):
        """Setup UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Scroll area for metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(10)
        
        # 1. Response Time Graph Section (Placeholder)
        self.graph_section = self._create_graph_section()
        self.content_layout.addWidget(self.graph_section)
        
        # 2. Node Status Cards Section (Placeholder)
        self.cards_section = self._create_cards_section()
        self.content_layout.addWidget(self.cards_section)
        
        # 3. Network Health Section
        self.health_section = self._create_health_section()
        self.content_layout.addWidget(self.health_section)
        
        # 4. System Metrics Section
        self.metrics_section = self._create_metrics_section()
        self.content_layout.addWidget(self.metrics_section)
        
        self.content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _create_graph_section(self):
        """Create real-time graph section (placeholder for 2.2)."""
        group = QGroupBox("Response Time (Real-time)")
        layout = QVBoxLayout(group)
        
        # Placeholder
        placeholder = QLabel("📊 PyQtGraph will be added in step 2.2")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(200)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                border: 2px dashed #3D3D3D;
                border-radius: 8px;
                color: #888;
                font-size: 14px;
            }
        """)
        layout.addWidget(placeholder)
        
        return group
    
    def _create_cards_section(self):
        """Create node status cards section (placeholder for 2.3)."""
        group = QGroupBox("Node Status Cards")
        layout = QVBoxLayout(group)
        
        # Placeholder
        placeholder = QLabel("🎴 Status cards will be added in step 2.3")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(150)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                border: 2px dashed #3D3D3D;
                border-radius: 8px;
                color: #888;
                font-size: 14px;
            }
        """)
        layout.addWidget(placeholder)
        
        return group
    
    def _create_health_section(self):
        """Create network health bars section."""
        group = QGroupBox("Network Health")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Overall health
        overall_layout = QHBoxLayout()
        overall_label = QLabel("Overall:")
        overall_label.setMinimumWidth(100)
        self.overall_health = QProgressBar()
        self.overall_health.setRange(0, 100)
        self.overall_health.setValue(0)
        self.overall_health.setFormat("%p%")
        overall_layout.addWidget(overall_label)
        overall_layout.addWidget(self.overall_health)
        layout.addLayout(overall_layout)
        
        # Validators health
        validators_layout = QHBoxLayout()
        validators_label = QLabel("Validators:")
        validators_label.setMinimumWidth(100)
        self.validators_health = QProgressBar()
        self.validators_health.setRange(0, 100)
        self.validators_health.setValue(0)
        self.validators_health.setFormat("%p%")
        validators_layout.addWidget(validators_label)
        validators_layout.addWidget(self.validators_health)
        layout.addLayout(validators_layout)
        
        # Regular nodes health
        regular_layout = QHBoxLayout()
        regular_label = QLabel("Regular:")
        regular_label.setMinimumWidth(100)
        self.regular_health = QProgressBar()
        self.regular_health.setRange(0, 100)
        self.regular_health.setValue(0)
        self.regular_health.setFormat("%p%")
        regular_layout.addWidget(regular_label)
        regular_layout.addWidget(self.regular_health)
        layout.addLayout(regular_layout)
        
        # Style progress bars
        self._style_progress_bars()
        
        return group
    
    def _create_metrics_section(self):
        """Create system metrics section."""
        group = QGroupBox("System Metrics")
        layout = QVBoxLayout(group)
        
        # Create metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(10)
        
        # Blocks/min
        blocks_label = QLabel("Blocks/min:")
        self.blocks_per_min = QLabel("0")
        self.blocks_per_min.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_grid.addWidget(blocks_label, 0, 0)
        metrics_grid.addWidget(self.blocks_per_min, 0, 1)
        
        # TX/sec
        tx_label = QLabel("TX/sec:")
        self.tx_per_sec = QLabel("0.0")
        self.tx_per_sec.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_grid.addWidget(tx_label, 1, 0)
        metrics_grid.addWidget(self.tx_per_sec, 1, 1)
        
        # Avg Block Time
        block_time_label = QLabel("Avg Block Time:")
        self.avg_block_time = QLabel("0.0s")
        self.avg_block_time.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_grid.addWidget(block_time_label, 2, 0)
        metrics_grid.addWidget(self.avg_block_time, 2, 1)
        
        layout.addLayout(metrics_grid)
        
        return group
    
    def _style_progress_bars(self):
        """Apply styling to progress bars."""
        style = """
            QProgressBar {
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                background-color: #2D2D2D;
                text-align: center;
                color: #E0E0E0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """
        self.overall_health.setStyleSheet(style)
        self.validators_health.setStyleSheet(style)
        self.regular_health.setStyleSheet(style)
    
    def _setup_connections(self):
        """Setup signal connections with data manager."""
        if self.data_manager:
            self.data_manager.nodes_updated.connect(self.update_health)
            self.data_manager.metrics_updated.connect(self.update_metrics)
    
    @Slot(list)
    def update_health(self, nodes):
        """Update health bars based on node data.
        
        Args:
            nodes: List of node dictionaries
        """
        if not nodes:
            return
        
        validators = [n for n in nodes if n.get('role') == 'validator']
        regular = [n for n in nodes if n.get('role') == 'regular']
        
        # Calculate health (based on status)
        def calc_health(node_list):
            if not node_list:
                return 0
            healthy = sum(1 for n in node_list if n.get('status') == 'healthy')
            return int((healthy / len(node_list)) * 100)
        
        validators_health = calc_health(validators)
        regular_health = calc_health(regular)
        overall_health = calc_health(nodes)
        
        self.overall_health.setValue(overall_health)
        self.validators_health.setValue(validators_health)
        self.regular_health.setValue(regular_health)
    
    @Slot(dict)
    def update_metrics(self, metrics):
        """Update system metrics display.
        
        Args:
            metrics: Dictionary with system metrics
        """
        if not metrics:
            return
        
        # Update blocks per minute
        blocks_per_min = metrics.get('blocks_per_minute', 0)
        self.blocks_per_min.setText(str(blocks_per_min))
        
        # Update TX per second
        tx_per_sec = metrics.get('transactions_per_second', 0.0)
        self.tx_per_sec.setText(f"{tx_per_sec:.1f}")
        
        # Update average block time
        avg_block_time = metrics.get('average_block_time', 0.0)
        self.avg_block_time.setText(f"{avg_block_time:.1f}s")
    
    def clear_display(self):
        """Clear all metrics display."""
        self.overall_health.setValue(0)
        self.validators_health.setValue(0)
        self.regular_health.setValue(0)
        self.blocks_per_min.setText("0")
        self.tx_per_sec.setText("0.0")
        self.avg_block_time.setText("0.0s")
