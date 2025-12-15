"""Nodes Page - Node list and details."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QLabel, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor


class NodesPage(QWidget):
    """Nodes page showing node list."""
    
    def __init__(self, data_manager):
        """Initialize nodes page."""
        super().__init__()
        
        self.data_manager = data_manager
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Network Nodes")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Create splitter for tree and activity log
        splitter = QSplitter(Qt.Vertical)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Node ID", "Status", "Role", "Trust/Balance", "Response Time"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 120)
        self.tree.setAlternatingRowColors(True)
        self.tree.setMinimumHeight(400)  # Reduced to make room for activity log
        splitter.addWidget(self.tree)
        
        # Recent Activity Log
        activity_group = QWidget()
        activity_layout = QVBoxLayout(activity_group)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        
        activity_header = QLabel("Recent Activity Log")
        activity_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        activity_layout.addWidget(activity_header)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(200)
        self.activity_log.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                color: #E0E0E0;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
            }
        """)
        activity_layout.addWidget(self.activity_log)
        
        splitter.addWidget(activity_group)
        
        # Set splitter sizes (70% tree, 30% log)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.data_manager.nodes_updated.connect(self._on_nodes_updated)
    
    def _on_nodes_updated(self, nodes):
        """Handle nodes update."""
        self.tree.clear()
        
        # Track status changes for activity log
        current_nodes = {n.get('id'): n for n in nodes}
        
        # Check for new nodes or status changes
        if hasattr(self, '_previous_nodes'):
            for node_id, node in current_nodes.items():
                if node_id not in self._previous_nodes:
                    # New node
                    self.add_activity(f"[NEW] Node {node_id} joined network", "#4CAF50")
                else:
                    prev_node = self._previous_nodes[node_id]
                    current_status = node.get('status')
                    prev_status = prev_node.get('status')
                    
                    if current_status != prev_status:
                        if current_status == 'under_attack':
                            self.add_activity(f"[ALERT] Node {node_id} is under attack!", "#F44336")
                        elif current_status == 'recovering':
                            self.add_activity(f"[INFO] Node {node_id} is recovering", "#FF9800")
                        elif current_status == 'healthy' and prev_status in ['under_attack', 'recovering']:
                            self.add_activity(f"[OK] Node {node_id} recovered to healthy", "#4CAF50")
        
        # Store current state
        self._previous_nodes = current_nodes
        
        # Group by role
        validators = [n for n in nodes if n.get('role') == 'validator']
        regulars = [n for n in nodes if n.get('role') == 'regular']
        
        # Add validators
        if validators:
            validator_root = QTreeWidgetItem(self.tree, [f"👑 Validators ({len(validators)})", "", "", "", ""])
            validator_root.setExpanded(True)
            
            for node in validators:
                self._add_node_item(validator_root, node, is_validator=True)
        
        # Add regular nodes
        if regulars:
            regular_root = QTreeWidgetItem(self.tree, [f"Regular Nodes ({len(regulars)})", "", "", "", ""])
            regular_root.setExpanded(True)
            
            for node in regulars:
                self._add_node_item(regular_root, node, is_validator=False)
    
    def _add_node_item(self, parent, node, is_validator):
        """Add node item to tree."""
        node_id = node.get('id', 'N/A')
        status = node.get('status', 'healthy')
        role = node.get('role', 'regular')
        
        # Status icon
        status_icon = self._get_status_icon(status)
        
        # Trust score or balance
        if is_validator:
            trust = node.get('trust_score', 100)
            trust_text = f"Trust: {trust}"
        else:
            balance = node.get('balance', 0)
            trust_text = f"Balance: {balance}"
        
        # Response time
        response_time = node.get('response_time', 50)
        rt_text = f"{response_time}ms"
        
        # Create item
        item = QTreeWidgetItem(parent, [node_id, status_icon, role, trust_text, rt_text])
        
        # Color based on status
        if status == 'under_attack':
            item.setBackground(0, QBrush(QColor(255, 100, 100, 50)))
        elif status == 'recovering':
            item.setBackground(0, QBrush(QColor(255, 200, 100, 50)))
        
        # Mark special nodes
        if node.get('is_malicious'):
            item.setText(1, status_icon + " ⚠️")
        if node.get('is_sybil'):
            item.setText(1, status_icon + " 🚫")
        if node.get('is_byzantine'):
            item.setText(1, status_icon + " ☣️")
    
    def _get_status_icon(self, status):
        """Get status icon."""
        icons = {
            'healthy': '🟢',
            'under_attack': '🔴',
            'recovering': '🟡'
        }
        return icons.get(status, '⚪')
    
    def clear_display(self):
        """Clear tree and activity log."""
        self.tree.clear()
        self.activity_log.clear()
    
    def add_activity(self, message, color="#E0E0E0"):
        """Add activity message to log.
        
        Args:
            message: Activity message text
            color: HTML color code for message
        """
        # Add colored message
        self.activity_log.append(f"<span style='color:{color}'>{message}</span>")
        
        # Auto-scroll to bottom
        scrollbar = self.activity_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
