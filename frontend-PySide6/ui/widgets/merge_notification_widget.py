"""Merge Notification Widget - Displays chain merge success notification."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class MergeNotificationWidget(QWidget):
    """Widget to display chain merge notification."""
    
    def __init__(self):
        """Initialize merge notification widget."""
        super().__init__()
        self._setup_ui()
        self.setVisible(False)
        
        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self._auto_hide)
        self.hide_timer.setSingleShot(True)
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box
        self.group = QGroupBox()
        self.group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1B5E20, stop:1 #2E7D32);
                padding: 15px;
                margin: 0px;
            }
        """)
        group_layout = QVBoxLayout(self.group)
        group_layout.setSpacing(8)
        
        # Icon + Title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        icon_label = QLabel("✅")
        icon_label.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Chain Merged Successfully")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #81C784;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        group_layout.addLayout(title_layout)
        
        # Separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #4CAF50;")
        group_layout.addWidget(separator)
        
        # Main message
        self.lbl_message = QLabel("🏆 Longest chain won the consensus!")
        self.lbl_message.setStyleSheet("""
            font-size: 13px; 
            color: #C8E6C9; 
            font-weight: 600;
            padding: 5px 0px;
        """)
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(self.lbl_message)
        
        # Compact stats layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Winner
        winner_layout = QVBoxLayout()
        winner_layout.setSpacing(2)
        winner_title = QLabel("Winner Chain")
        winner_title.setStyleSheet("font-size: 10px; color: #A5D6A7; text-transform: uppercase;")
        winner_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_winner_length = QLabel("0 blocks")
        self.lbl_winner_length.setStyleSheet("font-size: 18px; color: #4CAF50; font-weight: bold;")
        self.lbl_winner_length.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winner_layout.addWidget(winner_title)
        winner_layout.addWidget(self.lbl_winner_length)
        stats_layout.addLayout(winner_layout)
        
        # Divider
        divider = QLabel("│")
        divider.setStyleSheet("font-size: 24px; color: #555; font-weight: 100;")
        stats_layout.addWidget(divider)
        
        # Loser
        loser_layout = QVBoxLayout()
        loser_layout.setSpacing(2)
        loser_title = QLabel("Orphaned Chain")
        loser_title.setStyleSheet("font-size: 10px; color: #FFAB91; text-transform: uppercase;")
        loser_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_loser_length = QLabel("0 blocks")
        self.lbl_loser_length.setStyleSheet("font-size: 18px; color: #FF7043; font-weight: bold;")
        self.lbl_loser_length.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loser_layout.addWidget(loser_title)
        loser_layout.addWidget(self.lbl_loser_length)
        stats_layout.addLayout(loser_layout)
        
        group_layout.addLayout(stats_layout)
        
        # Orphaned blocks info
        self.lbl_orphaned = QLabel("📦 Orphaned Blocks: 0")
        self.lbl_orphaned.setStyleSheet("""
            font-size: 11px; 
            color: #FFD54F; 
            padding: 5px 0px;
            font-weight: 500;
        """)
        self.lbl_orphaned.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(self.lbl_orphaned)
        
        layout.addWidget(self.group)
    
    def show_merge(self, winner_length, loser_length, orphaned_blocks):
        """Show merge notification with details."""
        self.lbl_winner_length.setText(f"{winner_length} blocks")
        self.lbl_loser_length.setText(f"{loser_length} blocks")
        self.lbl_orphaned.setText(f"📦 Orphaned Blocks: {orphaned_blocks}")
        
        self.setVisible(True)
        self.hide_timer.start(8000)
    
    def _auto_hide(self):
        """Auto-hide the notification."""
        self.setVisible(False)
    
    def hide_notification(self):
        """Manually hide the notification."""
        self.hide_timer.stop()
        self.setVisible(False)
