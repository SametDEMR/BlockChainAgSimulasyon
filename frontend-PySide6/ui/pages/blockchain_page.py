"""Blockchain Explorer Page - Blockchain visualization and exploration."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, Signal

from ui.widgets.blockchain_graph_widget import BlockchainGraphWidget
from ui.widgets.block_item import BlockItem
from ui.widgets.chain_drawer import ChainDrawer
from ui.widgets.fork_status_widget import ForkStatusWidget
from ui.dialogs.block_detail_dialog import BlockDetailDialog


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
        self.chain_drawer = ChainDrawer()
        self.current_layout = None
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Stats section
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)
        
        # Fork Status Widget (initially hidden)
        self.fork_status_widget = ForkStatusWidget()
        self.fork_status_widget.setVisible(False)
        layout.addWidget(self.fork_status_widget)
        
        # Control bar
        control_bar = self._create_control_bar()
        layout.addLayout(control_bar)
        
        # Blockchain graph widget
        self.graph_widget = BlockchainGraphWidget()
        layout.addWidget(self.graph_widget, stretch=1)
    
    def _create_stats_section(self):
        """Create blockchain statistics section."""
        group = QGroupBox("Blockchain Statistics")
        layout = QHBoxLayout(group)
        
        self.lbl_total_blocks = QLabel("Total Blocks: 0")
        self.lbl_total_blocks.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_total_blocks)
        
        self.lbl_forks = QLabel("Forks: 0")
        self.lbl_forks.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF9800;")
        layout.addWidget(self.lbl_forks)
        
        self.lbl_pending_tx = QLabel("Pending TX: 0")
        self.lbl_pending_tx.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        layout.addWidget(self.lbl_pending_tx)
        
        self.lbl_orphan_blocks = QLabel("Orphan Blocks: 0")
        self.lbl_orphan_blocks.setStyleSheet("font-size: 14px; font-weight: bold; color: #9E9E9E;")
        layout.addWidget(self.lbl_orphan_blocks)
        
        layout.addStretch()
        return group
    
    def _create_control_bar(self):
        """Create control bar with zoom and filter controls."""
        layout = QHBoxLayout()
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        layout.addWidget(zoom_label)
        
        self.btn_zoom_in = QPushButton("➕ Zoom In")
        self.btn_zoom_in.setMaximumWidth(100)
        self.btn_zoom_in.clicked.connect(self._on_zoom_in)
        layout.addWidget(self.btn_zoom_in)
        
        self.btn_zoom_out = QPushButton("➖ Zoom Out")
        self.btn_zoom_out.setMaximumWidth(100)
        self.btn_zoom_out.clicked.connect(self._on_zoom_out)
        layout.addWidget(self.btn_zoom_out)
        
        self.btn_fit_view = QPushButton("🔲 Fit View")
        self.btn_fit_view.setMaximumWidth(100)
        self.btn_fit_view.clicked.connect(self._on_fit_view)
        layout.addWidget(self.btn_fit_view)
        
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
        
        # Graph widget signals
        self.graph_widget.block_double_clicked.connect(self._on_block_double_clicked)
    
    def _on_blockchain_updated(self, blockchain):
        """Handle blockchain data update."""
        # Update stats
        chain_length = blockchain.get('chain_length', 0)
        self.lbl_total_blocks.setText(f"Total Blocks: {chain_length}")
        
        pending_tx = blockchain.get('pending_transactions', 0)
        self.lbl_pending_tx.setText(f"Pending TX: {pending_tx}")
        
        # Render blockchain
        self._render_blockchain(blockchain)
    
    def _on_fork_status_updated(self, fork_status):
        """Handle fork status update."""
        # Fork status is a dict with 'fork_statuses' key containing list of node fork statuses
        fork_statuses = fork_status.get('fork_statuses', [])
        
        # Update fork status widget
        self.fork_status_widget.update_fork_status(fork_statuses)
        
        # Count total forks and orphaned blocks
        total_forks = 0
        total_orphaned = 0
        
        for node_status in fork_statuses:
            fs = node_status.get('fork_status', {})
            total_forks += fs.get('fork_events_count', 0)
            total_orphaned += fs.get('orphaned_blocks_count', 0)
        
        # Update stats labels
        self.lbl_forks.setText(f"Forks: {total_forks}")
        self.lbl_orphan_blocks.setText(f"Orphan Blocks: {total_orphaned}")
    
    def _render_blockchain(self, blockchain_data):
        """Render blockchain visualization."""
        # Calculate layout
        self.current_layout = self.chain_drawer.calculate_layout(blockchain_data)
        
        # Clear existing
        self.graph_widget.clear_blocks()
        
        # Apply filters
        filters = self.get_filter_state()
        
        # Add blocks
        for block_info in self.current_layout['blocks']:
            block_data = block_info['data']
            
            # Check filters
            if not self._should_show_block(block_data, filters):
                continue
            
            # Create block item
            block_item = BlockItem(block_data)
            position = block_info['position']
            block_item.setPos(position[0], position[1])
            
            # Add to scene
            self.graph_widget.add_block_item(block_item)
        
        # Add connections
        for conn in self.current_layout['connections']:
            line = self.chain_drawer.create_connection_line(conn)
            self.graph_widget.add_connection_line(line)
        
        # Update scene rect
        blocks_count = len(blockchain_data.get('blocks', []))
        self.graph_widget.update_scene_rect(blocks_count)
    
    def _should_show_block(self, block_data, filters):
        """Check if block should be shown based on filters."""
        if block_data.get('index') == 0:
            return filters.get('show_genesis', True)
        elif block_data.get('is_orphan'):
            return filters.get('show_orphan', True)
        elif block_data.get('is_malicious'):
            return filters.get('show_malicious', True)
        else:
            return filters.get('show_normal', True)
    
    def _on_zoom_in(self):
        """Handle zoom in button."""
        self.graph_widget.zoom_in()
        self.zoom_in_requested.emit()
    
    def _on_zoom_out(self):
        """Handle zoom out button."""
        self.graph_widget.zoom_out()
        self.zoom_out_requested.emit()
    
    def _on_fit_view(self):
        """Handle fit view button."""
        self.graph_widget.fit_view()
        self.fit_view_requested.emit()
    
    def _on_filter_changed(self):
        """Handle filter checkbox state changes."""
        filters = self.get_filter_state()
        self.filter_changed.emit(filters)
        
        # Re-render with filters
        blockchain = self.data_manager.get_cached_blockchain()
        if blockchain:
            self._render_blockchain(blockchain)
    
    def _on_block_double_clicked(self, block_data):
        """Handle block double click - show detail dialog."""
        blockchain = self.data_manager.get_cached_blockchain()
        all_blocks = blockchain.get('blocks', []) if blockchain else []
        
        dialog = BlockDetailDialog(block_data, all_blocks, self)
        dialog.exec()
    
    def update_stats(self, total_blocks=0, forks=0, pending_tx=0, orphan_blocks=0):
        """Update statistics display."""
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
        
        self.graph_widget.clear_blocks()
        self.fork_status_widget._clear_display()
        
        self.chk_show_genesis.setChecked(True)
        self.chk_show_normal.setChecked(True)
        self.chk_show_malicious.setChecked(True)
        self.chk_show_orphan.setChecked(True)
    
    def get_filter_state(self):
        """Get current filter state."""
        return {
            'show_genesis': self.chk_show_genesis.isChecked(),
            'show_normal': self.chk_show_normal.isChecked(),
            'show_malicious': self.chk_show_malicious.isChecked(),
            'show_orphan': self.chk_show_orphan.isChecked()
        }
