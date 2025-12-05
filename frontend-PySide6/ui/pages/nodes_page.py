"""Nodes Page - Node list and details."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QLabel
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
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Node ID", "Status", "Role", "Trust/Balance", "Response Time"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 120)
        self.tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.tree)
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.data_manager.nodes_updated.connect(self._on_nodes_updated)
    
    def _on_nodes_updated(self, nodes):
        """Handle nodes update."""
        self.tree.clear()
        
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
        """Clear tree."""
        self.tree.clear()
