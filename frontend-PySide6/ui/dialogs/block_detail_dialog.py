"""Block Detail Dialog - Shows detailed information about a block."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QGroupBox, QFormLayout, QHeaderView
)
from PySide6.QtCore import Qt, Signal


class BlockDetailDialog(QDialog):
    """Dialog showing detailed block information."""
    
    # Signals
    navigate_to_block = Signal(str)  # Emit block hash to navigate
    
    def __init__(self, block_data, all_blocks=None, parent=None):
        """Initialize block detail dialog.
        
        Args:
            block_data: Dictionary with block information
            all_blocks: List of all blocks for navigation
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.block_data = block_data
        self.all_blocks = all_blocks or []
        
        self._setup_ui()
        self._populate_data()
    
    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("Block Details")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Block info section
        info_group = self._create_block_info_section()
        layout.addWidget(info_group)
        
        # Transaction table
        tx_group = self._create_transaction_section()
        layout.addWidget(tx_group, stretch=1)
        
        # Navigation and close buttons
        button_layout = self._create_button_section()
        layout.addLayout(button_layout)
    
    def _create_block_info_section(self):
        """Create block information section.
        
        Returns:
            QGroupBox: Block info group
        """
        group = QGroupBox("Block Information")
        form = QFormLayout(group)
        
        # Index
        self.lbl_index = QLabel()
        form.addRow("Index:", self.lbl_index)
        
        # Hash
        self.lbl_hash = QLabel()
        self.lbl_hash.setWordWrap(True)
        self.lbl_hash.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("Hash:", self.lbl_hash)
        
        # Previous Hash
        self.lbl_prev_hash = QLabel()
        self.lbl_prev_hash.setWordWrap(True)
        self.lbl_prev_hash.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("Previous Hash:", self.lbl_prev_hash)
        
        # Miner
        self.lbl_miner = QLabel()
        form.addRow("Miner:", self.lbl_miner)
        
        # Timestamp
        self.lbl_timestamp = QLabel()
        form.addRow("Timestamp:", self.lbl_timestamp)
        
        # Transaction count
        self.lbl_tx_count = QLabel()
        form.addRow("Transactions:", self.lbl_tx_count)
        
        # Nonce
        self.lbl_nonce = QLabel()
        form.addRow("Nonce:", self.lbl_nonce)
        
        # Status
        self.lbl_status = QLabel()
        form.addRow("Status:", self.lbl_status)
        
        return group
    
    def _create_transaction_section(self):
        """Create transaction list section.
        
        Returns:
            QGroupBox: Transaction group
        """
        group = QGroupBox("Transactions")
        layout = QVBoxLayout(group)
        
        # Transaction table
        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(4)
        self.tx_table.setHorizontalHeaderLabels([
            "From", "To", "Amount", "Timestamp"
        ])
        
        # Table settings
        self.tx_table.setAlternatingRowColors(True)
        self.tx_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Stretch columns
        header = self.tx_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.tx_table)
        
        return group
    
    def _create_button_section(self):
        """Create button section.
        
        Returns:
            QHBoxLayout: Button layout
        """
        layout = QHBoxLayout()
        
        # Previous block button
        self.btn_prev = QPushButton("← Previous Block")
        self.btn_prev.clicked.connect(self._navigate_previous)
        layout.addWidget(self.btn_prev)
        
        # Next block button
        self.btn_next = QPushButton("Next Block →")
        self.btn_next.clicked.connect(self._navigate_next)
        layout.addWidget(self.btn_next)
        
        layout.addStretch()
        
        # Close button
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)
        
        return layout
    
    def _populate_data(self):
        """Populate dialog with block data."""
        # Block info
        self.lbl_index.setText(str(self.block_data.get('index', 'N/A')))
        self.lbl_hash.setText(self.block_data.get('hash', 'N/A'))
        self.lbl_prev_hash.setText(self.block_data.get('previous_hash', 'N/A'))
        self.lbl_miner.setText(self.block_data.get('miner_id', 'N/A'))
        self.lbl_timestamp.setText(str(self.block_data.get('timestamp', 'N/A')))
        self.lbl_nonce.setText(str(self.block_data.get('nonce', 'N/A')))
        
        # Transaction count
        transactions = self.block_data.get('transactions', [])
        self.lbl_tx_count.setText(str(len(transactions)))
        
        # Status
        status_parts = []
        if self.block_data.get('is_orphan'):
            status_parts.append("Orphan")
        if self.block_data.get('is_malicious'):
            status_parts.append("Malicious")
        if not status_parts:
            if self.block_data.get('index') == 0:
                status_parts.append("Genesis")
            else:
                status_parts.append("Normal")
        self.lbl_status.setText(", ".join(status_parts))
        
        # Populate transactions
        self._populate_transactions(transactions)
        
        # Enable/disable navigation buttons
        self._update_navigation_buttons()
    
    def _populate_transactions(self, transactions):
        """Populate transaction table.
        
        Args:
            transactions: List of transaction dictionaries
        """
        self.tx_table.setRowCount(len(transactions))
        
        for i, tx in enumerate(transactions):
            # From
            from_item = QTableWidgetItem(tx.get('from', 'N/A'))
            self.tx_table.setItem(i, 0, from_item)
            
            # To
            to_item = QTableWidgetItem(tx.get('to', 'N/A'))
            self.tx_table.setItem(i, 1, to_item)
            
            # Amount
            amount = tx.get('amount', 0)
            amount_item = QTableWidgetItem(f"{amount:.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tx_table.setItem(i, 2, amount_item)
            
            # Timestamp
            timestamp_item = QTableWidgetItem(str(tx.get('timestamp', 'N/A')))
            self.tx_table.setItem(i, 3, timestamp_item)
    
    def _update_navigation_buttons(self):
        """Enable/disable navigation buttons based on availability."""
        if not self.all_blocks:
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return
        
        current_index = self.block_data.get('index', 0)
        
        # Previous button
        self.btn_prev.setEnabled(current_index > 0)
        
        # Next button
        max_index = max(b.get('index', 0) for b in self.all_blocks)
        self.btn_next.setEnabled(current_index < max_index)
    
    def _navigate_previous(self):
        """Navigate to previous block."""
        if not self.all_blocks:
            return
        
        current_index = self.block_data.get('index', 0)
        if current_index <= 0:
            return
        
        # Find previous block
        prev_block = None
        for block in self.all_blocks:
            if block.get('index') == current_index - 1:
                prev_block = block
                break
        
        if prev_block:
            self.navigate_to_block.emit(prev_block['hash'])
            self.block_data = prev_block
            self._populate_data()
    
    def _navigate_next(self):
        """Navigate to next block."""
        if not self.all_blocks:
            return
        
        current_index = self.block_data.get('index', 0)
        
        # Find next block
        next_block = None
        for block in self.all_blocks:
            if block.get('index') == current_index + 1:
                next_block = block
                break
        
        if next_block:
            self.navigate_to_block.emit(next_block['hash'])
            self.block_data = next_block
            self._populate_data()
    
    def update_block_data(self, block_data, all_blocks=None):
        """Update dialog with new block data.
        
        Args:
            block_data: New block data
            all_blocks: Updated list of all blocks
        """
        self.block_data = block_data
        if all_blocks is not None:
            self.all_blocks = all_blocks
        self._populate_data()
