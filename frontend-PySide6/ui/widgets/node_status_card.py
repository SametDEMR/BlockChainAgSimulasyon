"""Node Status Card Widget."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


class NodeStatusCard(QFrame):
    """Individual node status card widget.
    
    Shows:
    - Status icon (🟢🟡🔴)
    - Node ID
    - Response time
    - Trust score/Balance with progress bar
    """
    
    def __init__(self, node_id, parent=None):
        """Initialize node status card.
        
        Args:
            node_id: Node identifier
            parent: Parent widget
        """
        super().__init__(parent)
        self.node_id = node_id
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setMinimumWidth(160)  # Reduced from 220
        self.setMaximumWidth(200)  # Reduced from 300
        self.setMinimumHeight(110)  # Add height limit
        self.setMaximumHeight(130)
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(3)  # Reduced from 5
        layout.setContentsMargins(8, 8, 8, 8)  # Reduced from 10
        
        # Header: Status icon + Node ID
        header_layout = QHBoxLayout()
        
        self.status_icon = QLabel("🟢")
        self.status_icon.setStyleSheet("font-size: 14px;")  # Reduced from 16
        
        self.node_label = QLabel(self.node_id)
        self.node_label.setStyleSheet("font-weight: bold; font-size: 11px;")  # Reduced from 13
        
        header_layout.addWidget(self.status_icon)
        header_layout.addWidget(self.node_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Response time
        self.response_time = QLabel("RT: 0ms")
        self.response_time.setStyleSheet("font-size: 9px; color: #B0B0B0;")  # Reduced from 11
        layout.addWidget(self.response_time)
        
        # Trust/Balance label
        self.metric_label = QLabel("Trust:")
        self.metric_label.setStyleSheet("font-size: 9px; color: #B0B0B0;")  # Reduced from 11
        layout.addWidget(self.metric_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(6)  # Reduced from 8
        layout.addWidget(self.progress_bar)
        
        # Numeric value
        self.metric_value = QLabel("0")
        self.metric_value.setAlignment(Qt.AlignCenter)
        self.metric_value.setStyleSheet("font-weight: bold; font-size: 10px;")  # Reduced from 12
        layout.addWidget(self.metric_value)
    
    def _apply_style(self):
        """Apply base styling."""
        self.setStyleSheet("""
            NodeStatusCard {
                background-color: #2D2D2D;
                border: 2px solid #3D3D3D;
                border-radius: 8px;
            }
            NodeStatusCard:hover {
                border-color: #2196F3;
            }
            QProgressBar {
                border: 1px solid #3D3D3D;
                border-radius: 3px;
                background-color: #1E1E1E;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
    
    def update_data(self, node_data):
        """Update card with node data.
        
        Args:
            node_data: Dictionary with node information
        """
        # Status icon
        status = node_data.get('status', 'healthy')
        if status == 'healthy':
            self.status_icon.setText("🟢")
            self._update_border_color('#4CAF50')
        elif status == 'under_attack':
            self.status_icon.setText("🔴")
            self._update_border_color('#F44336')
        elif status == 'recovering':
            self.status_icon.setText("🟡")
            self._update_border_color('#FF9800')
        else:
            self.status_icon.setText("⚪")
            self._update_border_color('#9E9E9E')
        
        # Response time
        response_time = node_data.get('response_time', 0)
        self.response_time.setText(f"RT: {response_time}ms")
        
        # Metric (trust_score for validators, balance for regular)
        role = node_data.get('role', 'regular')
        if role == 'validator':
            trust_score = node_data.get('trust_score', 0)
            self.metric_label.setText("Trust:")
            self.progress_bar.setValue(int(trust_score))
            self.metric_value.setText(str(int(trust_score)))
        else:
            balance = node_data.get('balance', 0)
            self.metric_label.setText("Balance:")
            # Scale balance to 0-100 for progress bar (assuming max ~1000)
            scaled = min(int(balance / 10), 100)
            self.progress_bar.setValue(scaled)
            self.metric_value.setText(str(int(balance)))
    
    def _update_border_color(self, color):
        """Update border color based on status.
        
        Args:
            color: Hex color code
        """
        self.setStyleSheet(f"""
            NodeStatusCard {{
                background-color: #2D2D2D;
                border-left: 4px solid {color};
                border-top: 2px solid #3D3D3D;
                border-right: 2px solid #3D3D3D;
                border-bottom: 2px solid #3D3D3D;
                border-radius: 8px;
            }}
            NodeStatusCard:hover {{
                border-top: 2px solid #2196F3;
                border-right: 2px solid #2196F3;
                border-bottom: 2px solid #2196F3;
            }}
            QProgressBar {{
                border: 1px solid #3D3D3D;
                border-radius: 3px;
                background-color: #1E1E1E;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
