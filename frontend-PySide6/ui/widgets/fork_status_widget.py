"""Fork Status Widget - Displays blockchain fork detection information."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ForkStatusWidget(QWidget):
    """Widget to display fork detection and history."""
    
    def __init__(self):
        """Initialize fork status widget."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box
        group = QGroupBox("⚠️ Fork Detection Status")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        group_layout = QVBoxLayout(group)
        
        # Summary section
        summary_layout = self._create_summary_section()
        group_layout.addLayout(summary_layout)
        
        # Fork history table
        self.fork_table = self._create_fork_table()
        group_layout.addWidget(self.fork_table)
        
        layout.addWidget(group)
    
    def _create_summary_section(self):
        """Create summary statistics section."""
        layout = QHBoxLayout()
        
        # Total forks
        self.lbl_total_forks = QLabel("Total Fork Events: 0")
        self.lbl_total_forks.setStyleSheet("font-size: 12px; color: #FF5722;")
        layout.addWidget(self.lbl_total_forks)
        
        layout.addSpacing(20)
        
        # Orphaned blocks
        self.lbl_orphaned = QLabel("Orphaned Blocks: 0")
        self.lbl_orphaned.setStyleSheet("font-size: 12px; color: #9E9E9E;")
        layout.addWidget(self.lbl_orphaned)
        
        layout.addSpacing(20)
        
        # Nodes affected
        self.lbl_nodes_affected = QLabel("Nodes Affected: 0")
        self.lbl_nodes_affected.setStyleSheet("font-size: 12px; color: #2196F3;")
        layout.addWidget(self.lbl_nodes_affected)
        
        layout.addStretch()
        
        return layout
    
    def _create_fork_table(self):
        """Create fork history table."""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Node ID", "Fork Point", "Lost Blocks", 
            "Original Chain", "Winning Chain", "Timestamp"
        ])
        
        # Table styling
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #2B2B2B;
                gridline-color: #444;
                border: 1px solid #444;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #FF9800;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                padding: 5px;
                border: 1px solid #444;
                font-weight: bold;
            }
        """)
        
        # Column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        table.setColumnWidth(1, 100)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 120)
        
        return table
    
    def update_fork_status(self, fork_statuses):
        """Update fork status display.
        
        Args:
            fork_statuses: List of fork status data from /blockchain/fork-status endpoint
        """
        if not fork_statuses:
            self._clear_display()
            return
        
        # Calculate totals
        total_fork_events = 0
        total_orphaned = 0
        nodes_affected = 0
        
        # Clear table
        self.fork_table.setRowCount(0)
        
        # Add rows for each node with fork history
        for node_status in fork_statuses:
            node_id = node_status.get('node_id', 'Unknown')
            fork_status = node_status.get('fork_status', {})
            fork_history = fork_status.get('fork_history', [])
            
            if not fork_history:
                continue
            
            nodes_affected += 1
            fork_events = fork_status.get('fork_events_count', 0)
            orphaned_blocks = fork_status.get('orphaned_blocks_count', 0)
            
            total_fork_events += fork_events
            total_orphaned += orphaned_blocks
            
            # Add row for each fork event in history
            for fork_event in fork_history:
                self._add_fork_row(node_id, fork_event)
        
        # Update summary
        self.lbl_total_forks.setText(f"Total Fork Events: {total_fork_events}")
        self.lbl_orphaned.setText(f"Orphaned Blocks: {total_orphaned}")
        self.lbl_nodes_affected.setText(f"Nodes Affected: {nodes_affected}")
        
        # Show/hide widget based on fork events
        self.setVisible(total_fork_events > 0)
    
    def _add_fork_row(self, node_id, fork_event):
        """Add a fork event row to the table.
        
        Args:
            node_id: Node identifier
            fork_event: Fork event data
        """
        row = self.fork_table.rowCount()
        self.fork_table.insertRow(row)
        
        # Node ID
        item_node = QTableWidgetItem(node_id)
        item_node.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fork_table.setItem(row, 0, item_node)
        
        # Fork point
        fork_point = fork_event.get('fork_point', 0)
        item_fork_point = QTableWidgetItem(f"Block #{fork_point}")
        item_fork_point.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fork_table.setItem(row, 1, item_fork_point)
        
        # Lost blocks
        current_length = fork_event.get('current_chain_length', 0)
        incoming_length = fork_event.get('incoming_chain_length', 0)
        lost_blocks = current_length - fork_point
        
        item_lost = QTableWidgetItem(str(lost_blocks))
        item_lost.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_lost.setForeground(QColor("#FF5722"))
        self.fork_table.setItem(row, 2, item_lost)
        
        # Original chain length
        item_original = QTableWidgetItem(f"{current_length} blocks")
        item_original.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fork_table.setItem(row, 3, item_original)
        
        # Winning chain length
        item_winning = QTableWidgetItem(f"{incoming_length} blocks")
        item_winning.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_winning.setForeground(QColor("#4CAF50"))
        self.fork_table.setItem(row, 4, item_winning)
        
        # Timestamp
        timestamp = fork_event.get('timestamp', 0)
        from datetime import datetime
        time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        item_time = QTableWidgetItem(time_str)
        item_time.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fork_table.setItem(row, 5, item_time)
    
    def _clear_display(self):
        """Clear all displays."""
        self.lbl_total_forks.setText("Total Fork Events: 0")
        self.lbl_orphaned.setText("Orphaned Blocks: 0")
        self.lbl_nodes_affected.setText("Nodes Affected: 0")
        self.fork_table.setRowCount(0)
        self.setVisible(False)
