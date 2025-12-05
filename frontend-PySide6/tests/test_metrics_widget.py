"""Tests for MetricsWidget - Milestone 2.3."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock
import sys

from ui.widgets.metrics_widget import MetricsWidget


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_data_manager():
    """Create mock data manager."""
    manager = Mock()
    manager.nodes_updated = Mock()
    manager.nodes_updated.connect = Mock()
    manager.metrics_updated = Mock()
    manager.metrics_updated.connect = Mock()
    return manager


@pytest.fixture
def metrics_widget(qapp, mock_data_manager):
    """Create MetricsWidget instance."""
    widget = MetricsWidget(mock_data_manager)
    return widget


# ============ 2.1 + 2.2 Tests (Previous) ============

def test_metrics_widget_creation(metrics_widget):
    """Test widget is created successfully."""
    assert metrics_widget is not None


def test_plot_widget_exists(metrics_widget):
    """Test PyQtGraph PlotWidget is created."""
    assert metrics_widget.plot_widget is not None


def test_update_response_time_single_node(metrics_widget):
    """Test updating response time for a single node."""
    nodes = [{'id': 'node_0', 'response_time': 50}]
    metrics_widget.update_response_time_graph(nodes)
    
    assert 'node_0' in metrics_widget.response_time_data
    assert 'node_0' in metrics_widget.graph_curves


# ============ Milestone 2.3 Tests (Status Cards) ============

def test_cards_grid_exists(metrics_widget):
    """Test cards grid layout is created."""
    assert hasattr(metrics_widget, 'cards_grid')
    assert hasattr(metrics_widget, 'status_cards')
    assert isinstance(metrics_widget.status_cards, dict)


def test_update_status_cards_single_node(metrics_widget):
    """Test creating card for single node."""
    nodes = [{
        'id': 'node_0',
        'role': 'validator',
        'status': 'healthy',
        'response_time': 50,
        'trust_score': 95
    }]
    
    metrics_widget.update_status_cards(nodes)
    
    # Check card created
    assert 'node_0' in metrics_widget.status_cards
    assert metrics_widget.status_cards['node_0'] is not None


def test_update_status_cards_multiple_nodes(metrics_widget):
    """Test creating cards for multiple nodes."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'validator', 'status': 'under_attack', 'response_time': 200, 'trust_score': 70},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy', 'response_time': 45, 'balance': 500},
    ]
    
    metrics_widget.update_status_cards(nodes)
    
    # Check all cards created
    assert len(metrics_widget.status_cards) == 3
    assert 'node_0' in metrics_widget.status_cards
    assert 'node_1' in metrics_widget.status_cards
    assert 'node_2' in metrics_widget.status_cards


def test_update_status_cards_updates_existing(metrics_widget):
    """Test updating existing cards."""
    # Create initial card
    nodes = [{'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95}]
    metrics_widget.update_status_cards(nodes)
    
    initial_card = metrics_widget.status_cards['node_0']
    
    # Update with different data
    nodes = [{'id': 'node_0', 'role': 'validator', 'status': 'under_attack', 'response_time': 200, 'trust_score': 60}]
    metrics_widget.update_status_cards(nodes)
    
    # Should be same card object (not recreated)
    assert metrics_widget.status_cards['node_0'] is initial_card
    # Card count unchanged
    assert len(metrics_widget.status_cards) == 1


def test_update_status_cards_grid_placement(metrics_widget):
    """Test cards are placed in 2-column grid."""
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 90},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy', 'response_time': 50, 'balance': 500},
        {'id': 'node_3', 'role': 'regular', 'status': 'healthy', 'response_time': 50, 'balance': 450},
    ]
    
    metrics_widget.update_status_cards(nodes)
    
    # Check grid has items
    assert metrics_widget.cards_grid.count() == 4


def test_clear_display_clears_cards(metrics_widget):
    """Test clear_display removes all cards."""
    # Add some cards
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'regular', 'status': 'healthy', 'response_time': 50, 'balance': 500},
    ]
    metrics_widget.update_status_cards(nodes)
    
    assert len(metrics_widget.status_cards) == 2
    
    # Clear
    metrics_widget.clear_display()
    
    # Check cards cleared
    assert len(metrics_widget.status_cards) == 0


def test_update_status_cards_with_empty_list(metrics_widget):
    """Test handling empty node list."""
    metrics_widget.update_status_cards([])
    # Should not crash
    assert len(metrics_widget.status_cards) == 0


def test_signal_connections_for_cards(metrics_widget, mock_data_manager):
    """Test cards update is connected to nodes_updated signal."""
    calls = [call[0][0] for call in mock_data_manager.nodes_updated.connect.call_args_list]
    
    # Should have update_health, update_response_time_graph, and update_status_cards
    assert len(calls) == 3
    assert metrics_widget.update_status_cards in calls


def test_card_widget_properties(metrics_widget):
    """Test individual card has correct properties."""
    from ui.widgets.node_status_card import NodeStatusCard
    
    nodes = [{'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95}]
    metrics_widget.update_status_cards(nodes)
    
    card = metrics_widget.status_cards['node_0']
    
    # Check card is correct type
    assert isinstance(card, NodeStatusCard)
    assert card.node_id == 'node_0'
