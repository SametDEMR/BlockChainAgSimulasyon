"""Blockchain Explorer Page - Blockchain visualization and exploration."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, Signal


class BlockchainExplorerPage(QWidget):
    """Blockchain explorer page showing blockchain visualization."""
    
    # Signals
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    fit_view_requested = Signal()
    filter_changed = Signal(dict)
    
    def __init__(self, data_manager):
        """Initialize blockchain explorer page.
        
        Args:
            data_manager: DataManager instance
        """
        super().__init__()
        
        self.data_manager = data_manager
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Stats section
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)
        
        # Control bar
        control_bar = self._create_control_bar()
        layout.addLayout(control_bar)
        
        # Placeholder for blockchain graph widget (will be added in 5.2)
        placeholder = QLabel("Blockchain Graph Widget will be added here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(300)
        placeholder.setStyleSheet("background-color: #2E2E2E; border: 1px dashed #555;")
        layout.addWidget(placeholder, stretch=1)
    
    def _create_stats_section(self):
        """Create blockchain statistics section.
        
        Returns:
            QGroupBox: Stats group widget
        """
        group = QGroupBox("Blockchain Statistics")
        layout = QHBoxLayout(group)
        
        # Total blocks
        self.lbl_total_blocks = QLabel("Total Blocks: 0")
        self.lbl_total_blocks.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_total_blocks)
        
        # Forks count
        self.lbl_forks = QLabel("Forks: 0")
        self.lbl_forks.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF9800;")
        layout.addWidget(self.lbl_forks)
        
        # Pending transactions
        self.lbl_pending_tx = QLabel("Pending TX: 0")
        self.lbl_pending_tx.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        layout.addWidget(self.lbl_pending_tx)
        
        # Orphan blocks
        self.lbl_orphan_blocks = QLabel("Orphan Blocks: 0")
        self.lbl_orphan_blocks.setStyleSheet("font-size: 14px; font-weight: bold; color: #9E9E9E;")
        layout.addWidget(self.lbl_orphan_blocks)
        
        layout.addStretch()
        
        return group
    
    def _create_control_bar(self):
        """Create control bar with zoom and filter controls.
        
        Returns:
            QHBoxLayout: Control bar layout
        """
        layout = QHBoxLayout()
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        layout.addWidget(zoom_label)
        
        self.btn_zoom_in = QPushButton("➕ Zoom In")
        self.btn_zoom_in.setMaximumWidth(100)
        self.btn_zoom_in.clicked.connect(self.zoom_in_requested.emit)
        layout.addWidget(self.btn_zoom_in)
        
        self.btn_zoom_out = QPushButton("➖ Zoom Out")
        self.btn_zoom_out.setMaximumWidth(100)
        self.btn_zoom_out.clicked.connect(self.zoom_out_requested.emit)
        layout.addWidget(self.btn_zoom_out)
        
        self.btn_fit_view = QPushButton("🔲 Fit View")
        self.btn_fit_view.setMaximumWidth(100)
        self.btn_fit_view.clicked.connect(self.fit_view_requested.emit)
        layout.addWidget(self.btn_fit_view)
        
        # Separator
        layout.addSpacing(20)
        
        # Filter controls
        filter_label = QLabel("Show:")
        layout.addWidget(filter_label)
        
        self.chk_show_genesis = QCheckBox("Genesis")
        self.chk_show_genesis.setChecked(True)
        self.chk_show_genesis.stateChanged.connect(self._on_filter_changed)
        layout.addWidget(self.chk_show_genesis)
        
        self.chk_show_normal = QCheckBox("Normal")
        self.chk_show_normal.setChecked(True)
        self.chk_show_normal.stateChanged.connect(self._on_filter_changed)
        layout.addWidget(self.chk_show_normal)
        
        self.chk_show_malicious = QCheckBox("Malicious")
        self.chk_show_malicious.setChecked(True)
        self.chk_show_malicious.stateChanged.connect(self._on_filter_changed)
        layout.addWidget(self.chk_show_malicious)
        
        self.chk_show_orphan = QCheckBox("Orphan")
        self.chk_show_orphan.setChecked(True)
        self.chk_show_orphan.stateChanged.connect(self._on_filter_changed)
        layout.addWidget(self.chk_show_orphan)
        
        layout.addStretch()
        
        return layout
    
    def _setup_connections(self):
        """Setup signal connections with data manager."""
        self.data_manager.blockchain_updated.connect(self._on_blockchain_updated)
        self.data_manager.fork_status_updated.connect(self._on_fork_status_updated)
    
    def _on_blockchain_updated(self, blockchain):
        """Handle blockchain data update.
        
        Args:
            blockchain: Blockchain data dictionary
        """
        # Update total blocks
        chain_length = blockchain.get('chain_length', 0)
        self.lbl_total_blocks.setText(f"Total Blocks: {chain_length}")
        
        # Update pending transactions
        pending_tx = blockchain.get('pending_transactions', 0)
        self.lbl_pending_tx.setText(f"Pending TX: {pending_tx}")
    
    def _on_fork_status_updated(self, fork_status):
        """Handle fork status update.
        
        Args:
            fork_status: Fork status data dictionary
        """
        # Update forks count
        forks_count = fork_status.get('active_forks', 0)
        self.lbl_forks.setText(f"Forks: {forks_count}")
        
        # Update orphan blocks
        orphan_count = fork_status.get('orphan_blocks', 0)
        self.lbl_orphan_blocks.setText(f"Orphan Blocks: {orphan_count}")
    
    def _on_filter_changed(self):
        """Handle filter checkbox state changes."""
        filters = {
            'show_genesis': self.chk_show_genesis.isChecked(),
            'show_normal': self.chk_show_normal.isChecked(),
            'show_malicious': self.chk_show_malicious.isChecked(),
            'show_orphan': self.chk_show_orphan.isChecked()
        }
        self.filter_changed.emit(filters)
    
    def update_stats(self, total_blocks=0, forks=0, pending_tx=0, orphan_blocks=0):
        """Update statistics display.
        
        Args:
            total_blocks: Total number of blocks
            forks: Number of active forks
            pending_tx: Number of pending transactions
            orphan_blocks: Number of orphan blocks
        """
        self.lbl_total_blocks.setText(f"Total Blocks: {total_blocks}")
        self.lbl_forks.setText(f"Forks: {forks}")
        self.lbl_pending_tx.setText(f"Pending TX: {pending_tx}")
        self.lbl_orphan_blocks.setText(f"Orphan Blocks: {orphan_blocks}")
    
    def clear_display(self):
        """Clear all displays and reset to initial state."""
        self.lbl_total_blocks.setText("Total Blocks: 0")
        self.lbl_forks.setText("Forks: 0")
        self.lbl_pending_tx.setText("Pending TX: 0")
        self.lbl_orphan_blocks.setText("Orphan Blocks: 0")
        
        # Reset filters
        self.chk_show_genesis.setChecked(True)
        self.chk_show_normal.setChecked(True)
        self.chk_show_malicious.setChecked(True)
        self.chk_show_orphan.setChecked(True)
    
    def get_filter_state(self):
        """Get current filter state.
        
        Returns:
            dict: Current filter settings
        """
        return {
            'show_genesis': self.chk_show_genesis.isChecked(),
            'show_normal': self.chk_show_normal.isChecked(),
            'show_malicious': self.chk_show_malicious.isChecked(),
            'show_orphan': self.chk_show_orphan.isChecked()
        }
