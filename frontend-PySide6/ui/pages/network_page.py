"""
Network Map Page
Displays network topology with interactive controls
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QLabel, QFrame
)
from PySide6.QtCore import Signal, Slot
from typing import List, Dict


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
        
        # Graph area (placeholder for now)
        self.graph_frame = QFrame()
        self.graph_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.graph_frame.setMinimumHeight(400)
        
        graph_layout = QVBoxLayout(self.graph_frame)
        placeholder_label = QLabel("Network Graph Widget\n(Will be implemented in next step)")
        placeholder_label.setStyleSheet("color: #888; font-size: 14px;")
        graph_layout.addWidget(placeholder_label)
        
        layout.addWidget(self.graph_frame)
        
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
        self.zoom_in_btn.clicked.connect(self._on_zoom_in)
        self.zoom_out_btn.clicked.connect(self._on_zoom_out)
        self.fit_btn.clicked.connect(self._on_fit_view)
        self.reset_btn.clicked.connect(self._on_reset)
    
    # Control slots
    def _on_zoom_in(self):
        """Handle zoom in button click"""
        # Will be implemented with NetworkGraphWidget
        print("Zoom in clicked")
    
    def _on_zoom_out(self):
        """Handle zoom out button click"""
        # Will be implemented with NetworkGraphWidget
        print("Zoom out clicked")
    
    def _on_fit_view(self):
        """Handle fit view button click"""
        # Will be implemented with NetworkGraphWidget
        print("Fit view clicked")
    
    def _on_reset(self):
        """Handle reset button click"""
        # Will be implemented with NetworkGraphWidget
        print("Reset clicked")
    
    # Public methods for data updates
    @Slot(list)
    def update_network(self, nodes: List[Dict]):
        """
        Update network visualization with new node data
        
        Args:
            nodes: List of node dictionaries with structure:
                {
                    'id': str,
                    'role': 'validator' | 'regular',
                    'status': 'healthy' | 'under_attack' | 'recovering',
                    'is_sybil': bool,
                    'is_byzantine': bool,
                    ...
                }
        """
        # Will be implemented with NetworkGraphWidget
        print(f"Network update received: {len(nodes)} nodes")
    
    def clear_network(self):
        """Clear network visualization"""
        # Will be implemented with NetworkGraphWidget
        print("Network cleared")
    
    def get_selected_node(self) -> str:
        """Get currently selected node ID"""
        # Will be implemented with NetworkGraphWidget
        return ""
    
    def highlight_node(self, node_id: str):
        """Highlight specific node"""
        # Will be implemented with NetworkGraphWidget
        print(f"Highlighting node: {node_id}")
