"""
Active Attack Item Widget - Her attack için custom list item
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QProgressBar
)
from PySide6.QtCore import Qt, Signal


class ActiveAttackItem(QWidget):
    """
    Active attack gösterimi için custom widget.
    QListWidget item olarak kullanılır.
    """
    
    # Signal - stop butonu tıklandığında
    stop_requested = Signal(str)  # attack_id
    
    def __init__(self, attack_data: dict, parent=None):
        """
        Args:
            attack_data: {
                "id": "attack_123",
                "type": "ddos",
                "target": "node_5",
                "progress": 0.5,  # 0.0 - 1.0
                "remaining_time": 10  # saniye
            }
        """
        super().__init__(parent)
        self.attack_id = attack_data.get("id", "")
        self.init_ui(attack_data)
        
    def init_ui(self, attack_data: dict):
        """UI bileşenlerini oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Top row: Icon + Type + Target
        top_layout = QHBoxLayout()
        
        # Attack icon
        icon_map = {
            "ddos": "🌊",
            "byzantine": "⚔️",
            "sybil": "👥",
            "majority": "⚡",
            "partition": "🔌",
            "selfish_mining": "💎"
        }
        attack_type = attack_data.get("type", "")
        icon = icon_map.get(attack_type, "⚠️")
        
        self.icon_label = QLabel(f"{icon} {attack_type.upper()}")
        self.icon_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.icon_label)
        
        # Target info
        target = attack_data.get("target", "N/A")
        if target != "N/A":
            self.target_label = QLabel(f"on {target}")
        else:
            self.target_label = QLabel("Network-wide")
        top_layout.addWidget(self.target_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Middle row: Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress = attack_data.get("progress", 0)
        self.progress_bar.setValue(int(progress * 100))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # Bottom row: Time + Stop button
        bottom_layout = QHBoxLayout()
        
        remaining = attack_data.get("remaining_time", 0)
        self.time_label = QLabel(f"Remaining: {remaining}s")
        bottom_layout.addWidget(self.time_label)
        
        bottom_layout.addStretch()
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMaximumWidth(60)
        self.stop_button.setStyleSheet(
            "background-color: #F44336; color: white; font-weight: bold;"
        )
        self.stop_button.clicked.connect(self._on_stop_clicked)
        bottom_layout.addWidget(self.stop_button)
        
        layout.addLayout(bottom_layout)
        
        # Style
        self.setStyleSheet("""
            ActiveAttackItem {
                border: 1px solid #FF9800;
                border-radius: 4px;
                background-color: #2D2D2D;
            }
        """)
        
    def _on_stop_clicked(self):
        """Stop butonu handler"""
        self.stop_requested.emit(self.attack_id)
        
    def update_progress(self, progress: float, remaining_time: int):
        """
        Progress ve time güncelle
        
        Args:
            progress: 0.0 - 1.0 arası
            remaining_time: Kalan saniye
        """
        self.progress_bar.setValue(int(progress * 100))
        self.time_label.setText(f"Remaining: {remaining_time}s")
        
    def get_attack_id(self) -> str:
        """Attack ID döndür"""
        return self.attack_id
