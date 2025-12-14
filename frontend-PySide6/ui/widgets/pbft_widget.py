"""
PBFT Widget
Displays PBFT consensus status and message traffic
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from typing import Dict, List


class PBFTWidget(QWidget):
    """PBFT status and message traffic widget"""
    
    # Message type colors
    MESSAGE_COLORS = {
        'PRE_PREPARE': '#2196F3',   # Blue
        'PREPARE': '#FF9800',        # Orange
        'COMMIT': '#4CAF50',         # Green
        'REPLY': '#9C27B0',          # Purple
    }
    
    MAX_MESSAGES = 100  # Performance limit
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # PBFT Status Section
        status_group = QGroupBox("PBFT Status")
        status_layout = QHBoxLayout(status_group)
        
        self.primary_label = QLabel("Primary: N/A")
        self.view_label = QLabel("View: 0")
        self.consensus_label = QLabel("Consensus: 0")
        self.validators_label = QLabel("Validators: 0")
        self.messages_label = QLabel("Messages: 0")
        
        status_layout.addWidget(self.primary_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.view_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.consensus_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.validators_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.messages_label)
        status_layout.addStretch()
        
        layout.addWidget(status_group)
        
        # Message Traffic Section
        traffic_group = QGroupBox("Message Traffic")
        traffic_layout = QVBoxLayout(traffic_group)
        
        self.message_table = QTableWidget()
        self.message_table.setColumnCount(5)
        self.message_table.setHorizontalHeaderLabels([
            "Time", "Sender", "Receiver", "Type", "View"
        ])
        
        # Table settings
        self.message_table.setAlternatingRowColors(True)
        self.message_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.message_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.message_table.horizontalHeader().setStretchLastSection(True)
        
        # Enable scrolling
        from PySide6.QtWidgets import QSizePolicy
        self.message_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.message_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Column widths
        header = self.message_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Sender
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Receiver
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # View
        
        traffic_layout.addWidget(self.message_table)
        layout.addWidget(traffic_group)
        
        # Set layout stretch
        layout.setStretch(0, 0)  # Status: fixed height
        layout.setStretch(1, 1)  # Table: expandable
    
    def update_pbft_status(self, pbft_data: Dict):
        """
        Update PBFT status display
        
        Args:
            pbft_data: Dict with keys: primary, view, consensus_count, 
                      validator_count, total_messages
        """
        primary = pbft_data.get('primary', 'N/A')
        view = pbft_data.get('view', 0)
        consensus = pbft_data.get('consensus_count', 0)
        validators = pbft_data.get('validator_count', 0)
        messages = pbft_data.get('total_messages', 0)
        
        self.primary_label.setText(f"Primary: {primary}")
        self.view_label.setText(f"View: {view}")
        self.consensus_label.setText(f"Consensus: {consensus}")
        self.validators_label.setText(f"Validators: {validators}")
        self.messages_label.setText(f"Messages: {messages}")
    
    def add_message(self, message_data: Dict):
        """
        Add a message to the table
        
        Args:
            message_data: Dict with keys: timestamp, sender, receiver, 
                         type, view
        """
        # Limit rows for performance
        if self.message_table.rowCount() >= self.MAX_MESSAGES:
            self.message_table.removeRow(self.message_table.rowCount() - 1)
        
        # Insert at top (newest first)
        self.message_table.insertRow(0)
        
        timestamp = message_data.get('timestamp', '')
        sender = message_data.get('sender', '')
        receiver = message_data.get('receiver', '')
        msg_type = message_data.get('type', '')
        view = message_data.get('view', 0)
        
        # Create items
        time_item = QTableWidgetItem(timestamp)
        sender_item = QTableWidgetItem(sender)
        receiver_item = QTableWidgetItem(receiver)
        type_item = QTableWidgetItem(msg_type)
        view_item = QTableWidgetItem(str(view))
        
        # Color code message type
        if msg_type in self.MESSAGE_COLORS:
            color = QColor(self.MESSAGE_COLORS[msg_type])
            type_item.setBackground(color)
            type_item.setForeground(QColor("#FFFFFF"))
        
        # Set items
        self.message_table.setItem(0, 0, time_item)
        self.message_table.setItem(0, 1, sender_item)
        self.message_table.setItem(0, 2, receiver_item)
        self.message_table.setItem(0, 3, type_item)
        self.message_table.setItem(0, 4, view_item)
    
    def update_messages(self, messages: List[Dict]):
        """
        Update message table with list of messages
        
        Args:
            messages: List of message dictionaries (oldest to newest)
        """
        self.clear_messages()
        
        # Add messages in order (add_message inserts at top)
        # So oldest message is added first, newest last (ends up at top)
        for message in messages[-self.MAX_MESSAGES:]:
            self.add_message(message)
    
    def clear_messages(self):
        """Clear all messages from table"""
        self.message_table.setRowCount(0)
    
    def clear_display(self):
        """Clear all display data"""
        self.primary_label.setText("Primary: N/A")
        self.view_label.setText("View: 0")
        self.consensus_label.setText("Consensus: 0")
        self.validators_label.setText("Validators: 0")
        self.messages_label.setText("Messages: 0")
        self.clear_messages()
    
    def get_message_count(self) -> int:
        """Get current message count in table"""
        return self.message_table.rowCount()
