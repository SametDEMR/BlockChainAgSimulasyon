"""
Network Map Page
Displays network topology with interactive controls
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QLabel
)
from PySide6.QtCore import Signal, Slot
from typing import List, Dict
from ui.widgets.network_graph_widget import NetworkGraphWidget


class NetworkMapPage(QWidget):
    """Network map page showing node topology"""
    
    # Signals
    node_selected = Signal(str)  # node_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        # Zoom buttons
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.fit_btn = QPushButton("⊡ Fit View")
        self.reset_btn = QPushButton("↺ Reset")
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.fit_btn)
        controls_layout.addWidget(self.reset_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Graph widget
        self.graph_widget = NetworkGraphWidget()
        self.graph_widget.setMinimumHeight(400)
        layout.addWidget(self.graph_widget)
        
        # Legend section
        legend_group = QGroupBox("Legend")
        legend_layout = QVBoxLayout(legend_group)
        
        # Create legend items
        legends = [
            ("🔷", "Validator Node", "#2196F3"),
            ("🟢", "Regular Node", "#4CAF50"),
            ("🔴", "Sybil Node", "#F44336"),
            ("🟠", "Byzantine Node", "#FF9800"),
            ("🟡", "Under Attack", "#FFC107")
        ]
        
        for icon, text, color in legends:
            item_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            text_label = QLabel(text)
            text_label.setStyleSheet(f"color: {color};")
            item_layout.addWidget(icon_label)
            item_layout.addWidget(text_label)
            item_layout.addStretch()
            legend_layout.addLayout(item_layout)
        
        layout.addWidget(legend_group)
        
    def _connect_signals(self):
        """Connect internal signals"""
        self.zoom_in_btn.clicked.connect(self.graph_widget.zoom_in)
        self.zoom_out_btn.clicked.connect(self.graph_widget.zoom_out)
        self.fit_btn.clicked.connect(self.graph_widget.fit_view)
        self.reset_btn.clicked.connect(self.graph_widget.reset_view)
        
        # Forward graph widget signals
        self.graph_widget.node_clicked.connect(self.node_selected.emit)
    
    # Public methods for data updates
    @Slot(list)
    def update_network(self, nodes: List[Dict]):
        """
        Update network visualization with new node data
        
        Args:
            nodes: List of node dictionaries
        """
        self.graph_widget.update_graph(nodes)
    
    def clear_network(self):
        """Clear network visualization"""
        self.graph_widget.clear_graph()
    
    def get_selected_node(self) -> str:
        """Get currently selected node ID"""
        return self.graph_widget.get_selected_node() or ""
    
    def highlight_node(self, node_id: str):
        """Highlight specific node"""
        self.graph_widget.highlight_node(node_id)
