"""Metrics Dashboard Widget - Right Dock."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QProgressBar, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
import pyqtgraph as pg
from collections import deque


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
        
        # Graph data structures
        self.max_points = 50  # Keep last 50 data points
        self.response_time_data = {}  # {node_id: deque([times])}
        self.graph_curves = {}  # {node_id: PlotDataItem}
        self.colors = [
            '#2196F3', '#4CAF50', '#FF9800', '#F44336',
            '#9C27B0', '#00BCD4', '#FFEB3B', '#795548',
            '#E91E63', '#009688'
        ]
        
        # Card widgets
        self.status_cards = {}  # {node_id: NodeStatusCard}
        
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
        
        # 1. Response Time Graph Section - store reference but don't add to layout
        self.graph_section = self._create_graph_section()
        # Don't add: self.content_layout.addWidget(self.graph_section)
        
        # 2. Node Status Cards Section - store reference but don't add to layout  
        self.cards_section = self._create_cards_section()
        # Don't add: self.content_layout.addWidget(self.cards_section)
        
        # 3. Network Health Section
        self.health_section = self._create_health_section()
        self.content_layout.addWidget(self.health_section)
        
        # System Metrics section REMOVED (not important)
        
        self.content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _create_graph_section(self):
        """Create real-time graph section with PyQtGraph."""
        group = QGroupBox("Response Time (Real-time)")
        layout = QVBoxLayout(group)
        
        # Create PyQtGraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2D2D2D')
        self.plot_widget.setMinimumHeight(250)
        
        # Configure plot
        self.plot_widget.setLabel('left', 'Response Time', units='ms')
        self.plot_widget.setLabel('bottom', 'Time', units='updates')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()
        
        # Set axis colors
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#E0E0E0'))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#E0E0E0'))
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color='#E0E0E0'))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color='#E0E0E0'))
        
        layout.addWidget(self.plot_widget)
        
        return group
    
    def _create_cards_section(self):
        """Create node status cards section."""
        # Grid with 4 columns for wide layout (spanning 2 columns in dashboard)
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)
        for i in range(4):
            self.cards_grid.setColumnStretch(i, 1)
        
        self.status_cards = {}
        return None
    
    def _create_health_section(self):
        """Create network health bars section."""
        group = QGroupBox("Network Health")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Overall health
        overall_widget = QWidget()
        overall_layout = QVBoxLayout(overall_widget)
        overall_layout.setContentsMargins(5, 1, 5, 1)
        overall_label = QLabel("Overall")
        overall_label.setAlignment(Qt.AlignCenter)
        overall_label.setStyleSheet("font-size: 10px;")
        self.overall_health = QProgressBar()
        self.overall_health.setRange(0, 100)
        self.overall_health.setValue(0)
        self.overall_health.setFormat("%p%")
        self.overall_health.setFixedHeight(20)  # Reduced height
        overall_layout.addWidget(overall_label)
        overall_layout.addWidget(self.overall_health)
        layout.addWidget(overall_widget)
        
        # Validators health
        validators_widget = QWidget()
        validators_layout = QVBoxLayout(validators_widget)
        validators_layout.setContentsMargins(5, 1, 5, 1)
        validators_label = QLabel("Validators")
        validators_label.setAlignment(Qt.AlignCenter)
        validators_label.setStyleSheet("font-size: 10px;")
        self.validators_health = QProgressBar()
        self.validators_health.setRange(0, 100)
        self.validators_health.setValue(0)
        self.validators_health.setFormat("%p%")
        self.validators_health.setFixedHeight(20)  # Reduced height
        validators_layout.addWidget(validators_label)
        validators_layout.addWidget(self.validators_health)
        layout.addWidget(validators_widget)
        
        # Regular nodes health
        regular_widget = QWidget()
        regular_layout = QVBoxLayout(regular_widget)
        regular_layout.setContentsMargins(5, 1, 5, 1)
        regular_label = QLabel("Regular")
        regular_label.setAlignment(Qt.AlignCenter)
        regular_label.setStyleSheet("font-size: 10px;")
        self.regular_health = QProgressBar()
        self.regular_health.setRange(0, 100)
        self.regular_health.setValue(0)
        self.regular_health.setFormat("%p%")
        self.regular_health.setFixedHeight(20)  # Reduced height
        regular_layout.addWidget(regular_label)
        regular_layout.addWidget(self.regular_health)
        layout.addWidget(regular_widget)
        
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
                height: 25px;
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
            self.data_manager.nodes_updated.connect(self.update_response_time_graph)
            self.data_manager.nodes_updated.connect(self.update_status_cards)
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
        """Update system metrics display - REMOVED (not needed anymore).
        
        Args:
            metrics: Dictionary with system metrics
        """
        # System metrics removed from UI
        pass
    
    @Slot(list)
    def update_response_time_graph(self, nodes):
        """Update real-time response time graph.
        
        Args:
            nodes: List of node dictionaries with response_time
        """
        if not nodes:
            return
        
        for node in nodes:
            node_id = node.get('id')
            response_time = node.get('response_time', 0)
            
            # Initialize data structure for new node
            if node_id not in self.response_time_data:
                self.response_time_data[node_id] = deque(maxlen=self.max_points)
                
                # Create new curve with color
                color_idx = len(self.graph_curves) % len(self.colors)
                color = self.colors[color_idx]
                pen = pg.mkPen(color=color, width=2)
                
                curve = self.plot_widget.plot(
                    [], [], 
                    pen=pen, 
                    name=node_id
                )
                self.graph_curves[node_id] = curve
            
            # Add new data point
            self.response_time_data[node_id].append(response_time)
            
            # Update curve
            x_data = list(range(len(self.response_time_data[node_id])))
            y_data = list(self.response_time_data[node_id])
            self.graph_curves[node_id].setData(x_data, y_data)
    
    @Slot(list)
    def update_status_cards(self, nodes):
        """Update node status cards.
        
        Args:
            nodes: List of node dictionaries
        """
        if not nodes:
            return
        
        from ui.widgets.node_status_card import NodeStatusCard
        
        # Update or create cards
        for i, node in enumerate(nodes):
            node_id = node.get('id')
            
            if node_id not in self.status_cards:
                # Create new card
                card = NodeStatusCard(node_id)
                self.status_cards[node_id] = card
                
                # Add to grid (4 columns for wide layout)
                row = i // 4
                col = i % 4
                self.cards_grid.addWidget(card, row, col)
            
            # Update card data
            self.status_cards[node_id].update_data(node)
    
    def clear_display(self):
        """Clear all metrics display."""
        self.overall_health.setValue(0)
        self.validators_health.setValue(0)
        self.regular_health.setValue(0)
        # System metrics widgets removed
        
        # Clear graph data
        self.response_time_data.clear()
        for curve in self.graph_curves.values():
            curve.clear()
        self.graph_curves.clear()
        
        # Clear status cards
        for card in self.status_cards.values():
            self.cards_grid.removeWidget(card)
            card.deleteLater()
        self.status_cards.clear()
