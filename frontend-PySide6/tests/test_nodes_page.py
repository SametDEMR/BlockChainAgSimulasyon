"""Test for Nodes Page."""
import pytest
from unittest.mock import Mock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from ui.pages.nodes_page import NodesPage


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    from core.data_manager import DataManager
    dm = Mock(spec=DataManager)
    dm.nodes_updated = Mock()
    return dm


@pytest.fixture
def nodes_page(qapp, mock_data_manager):
    """Create nodes page."""
    page = NodesPage(mock_data_manager)
    yield page
    page.close()


class TestNodesPage:
    """Test NodesPage class."""
    
    def test_init(self, nodes_page):
        """Test initialization."""
        assert nodes_page.tree is not None
        assert nodes_page.tree.columnCount() == 5
    
    def test_update_with_nodes(self, nodes_page):
        """Test nodes update."""
        nodes = [
            {"id": "node_0", "role": "validator", "status": "healthy", "trust_score": 95, "response_time": 50},
            {"id": "node_1", "role": "validator", "status": "under_attack", "trust_score": 70, "response_time": 200},
            {"id": "node_4", "role": "regular", "status": "healthy", "balance": 100, "response_time": 55}
        ]
        
        nodes_page._on_nodes_updated(nodes)
        
        assert nodes_page.tree.topLevelItemCount() == 2  # Validators and Regular
    
    def test_clear_display(self, nodes_page):
        """Test clear display."""
        nodes = [{"id": "node_0", "role": "validator", "status": "healthy", "trust_score": 100, "response_time": 50}]
        nodes_page._on_nodes_updated(nodes)
        
        nodes_page.clear_display()
        assert nodes_page.tree.topLevelItemCount() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
