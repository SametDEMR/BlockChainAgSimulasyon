"""PBFT Messages Page - Full page PBFT widget."""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from ui.widgets.pbft_widget import PBFTWidget


class PBFTPage(QWidget):
    """Full page for PBFT consensus messages."""
    
    def __init__(self, pbft_widget):
        """Initialize PBFT page.
        
        Args:
            pbft_widget: PBFTWidget instance
        """
        super().__init__()
        
        self.pbft_widget = pbft_widget
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI - just contains PBFT widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Add PBFT widget
        layout.addWidget(self.pbft_widget)
    
    def clear_display(self):
        """Clear display."""
        self.pbft_widget.clear_display()
