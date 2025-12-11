"""Tests for Node Status Cards - Milestone 7.3."""
import pytest
from PySide6.QtWidgets import QApplication, QFrame
from PySide6.QtCore import Qt
import sys

from ui.widgets.node_status_card import NodeStatusCard


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def status_card(qapp):
    """Create NodeStatusCard instance."""
    card = NodeStatusCard('node_0')
    return card


# ============ Milestone 7.3 Tests: Node Status Cards ============

def test_card_creation(status_card):
    """Test card is created successfully."""
    assert status_card is not None
    assert isinstance(status_card, QFrame)


def test_card_has_node_id(status_card):
    """Test card stores node_id."""
    assert status_card.node_id == 'node_0'


def test_card_frame_styling(status_card):
    """Test QFrame has custom styling."""
    # Should have Box and Raised frame style
    assert status_card.frameStyle() & QFrame.Box
    assert status_card.lineWidth() == 2


def test_card_size_constraints(status_card):
    """Test card has size constraints."""
    assert status_card.minimumWidth() == 150
    assert status_card.maximumWidth() == 200


def test_card_has_status_icon(status_card):
    """Test card has status icon label."""
    assert hasattr(status_card, 'status_icon')
    assert status_card.status_icon.text() == "🟢"  # Default healthy


def test_card_has_node_label(status_card):
    """Test card has node ID label."""
    assert hasattr(status_card, 'node_label')
    assert status_card.node_label.text() == 'node_0'


def test_card_has_response_time_label(status_card):
    """Test card has response time label."""
    assert hasattr(status_card, 'response_time')
    assert 'RT:' in status_card.response_time.text()


def test_card_has_metric_label(status_card):
    """Test card has metric type label."""
    assert hasattr(status_card, 'metric_label')
    # Default is Trust for validators
    assert status_card.metric_label.text() in ['Trust:', 'Balance:']


def test_card_has_progress_bar(status_card):
    """Test card has progress bar."""
    assert hasattr(status_card, 'progress_bar')
    assert status_card.progress_bar.minimum() == 0
    assert status_card.progress_bar.maximum() == 100
    assert status_card.progress_bar.maximumHeight() == 8


def test_card_has_metric_value(status_card):
    """Test card has metric value label."""
    assert hasattr(status_card, 'metric_value')
    assert status_card.metric_value.text() == "0"


def test_update_data_healthy_status(status_card):
    """Test updating card with healthy status."""
    node_data = {
        'id': 'node_0',
        'status': 'healthy',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 95
    }
    
    status_card.update_data(node_data)
    
    assert status_card.status_icon.text() == "🟢"
    assert "50ms" in status_card.response_time.text()
    assert status_card.metric_value.text() == "95"
    assert status_card.progress_bar.value() == 95


def test_update_data_under_attack_status(status_card):
    """Test updating card with under_attack status."""
    node_data = {
        'id': 'node_0',
        'status': 'under_attack',
        'response_time': 200,
        'role': 'validator',
        'trust_score': 60
    }
    
    status_card.update_data(node_data)
    
    assert status_card.status_icon.text() == "🔴"
    assert "200ms" in status_card.response_time.text()


def test_update_data_recovering_status(status_card):
    """Test updating card with recovering status."""
    node_data = {
        'id': 'node_0',
        'status': 'recovering',
        'response_time': 100,
        'role': 'validator',
        'trust_score': 80
    }
    
    status_card.update_data(node_data)
    
    assert status_card.status_icon.text() == "🟡"


def test_update_data_unknown_status(status_card):
    """Test updating card with unknown status."""
    node_data = {
        'id': 'node_0',
        'status': 'unknown',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 90
    }
    
    status_card.update_data(node_data)
    
    assert status_card.status_icon.text() == "⚪"


def test_update_data_validator_trust_score(status_card):
    """Test validator shows trust score."""
    node_data = {
        'id': 'validator_0',
        'status': 'healthy',
        'response_time': 45,
        'role': 'validator',
        'trust_score': 98
    }
    
    status_card.update_data(node_data)
    
    assert status_card.metric_label.text() == "Trust:"
    assert status_card.metric_value.text() == "98"
    assert status_card.progress_bar.value() == 98


def test_update_data_regular_node_balance(status_card):
    """Test regular node shows balance."""
    node_data = {
        'id': 'node_1',
        'status': 'healthy',
        'response_time': 50,
        'role': 'regular',
        'balance': 750
    }
    
    status_card.update_data(node_data)
    
    assert status_card.metric_label.text() == "Balance:"
    assert status_card.metric_value.text() == "750"
    # Balance scaled to 0-100 (750/10 = 75)
    assert status_card.progress_bar.value() == 75


def test_update_data_high_balance_scaling(status_card):
    """Test high balance is capped at 100 for progress bar."""
    node_data = {
        'id': 'node_1',
        'status': 'healthy',
        'response_time': 50,
        'role': 'regular',
        'balance': 1500  # Should cap at 100
    }
    
    status_card.update_data(node_data)
    
    # Value shows actual balance
    assert status_card.metric_value.text() == "1500"
    # Progress bar capped at 100
    assert status_card.progress_bar.value() == 100


def test_update_data_zero_trust_score(status_card):
    """Test handling zero trust score."""
    node_data = {
        'id': 'validator_0',
        'status': 'under_attack',
        'response_time': 300,
        'role': 'validator',
        'trust_score': 0
    }
    
    status_card.update_data(node_data)
    
    assert status_card.metric_value.text() == "0"
    assert status_card.progress_bar.value() == 0


def test_update_data_zero_balance(status_card):
    """Test handling zero balance."""
    node_data = {
        'id': 'node_1',
        'status': 'healthy',
        'response_time': 50,
        'role': 'regular',
        'balance': 0
    }
    
    status_card.update_data(node_data)
    
    assert status_card.metric_value.text() == "0"
    assert status_card.progress_bar.value() == 0


def test_update_data_missing_optional_fields(status_card):
    """Test handling missing optional fields."""
    node_data = {
        'id': 'node_0',
        # Missing status, response_time, role, trust_score
    }
    
    # Should not crash
    status_card.update_data(node_data)
    
    # Should use defaults
    assert status_card.status_icon.text() == "🟢"  # Default healthy
    assert "0ms" in status_card.response_time.text()


def test_border_color_changes_with_status(status_card):
    """Test border color changes based on status."""
    # Healthy status
    node_data = {
        'id': 'node_0',
        'status': 'healthy',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 95
    }
    status_card.update_data(node_data)
    # Border should contain green color reference
    assert '#4CAF50' in status_card.styleSheet()
    
    # Under attack status
    node_data['status'] = 'under_attack'
    status_card.update_data(node_data)
    # Border should contain red color reference
    assert '#F44336' in status_card.styleSheet()
    
    # Recovering status
    node_data['status'] = 'recovering'
    status_card.update_data(node_data)
    # Border should contain orange color reference
    assert '#FF9800' in status_card.styleSheet()


def test_progress_bar_color_matches_status(status_card):
    """Test progress bar chunk color matches status."""
    node_data = {
        'id': 'node_0',
        'status': 'healthy',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 95
    }
    
    status_card.update_data(node_data)
    
    # Progress bar chunk should match status color
    assert '#4CAF50' in status_card.styleSheet()


def test_multiple_updates_same_card(status_card):
    """Test multiple updates on same card."""
    # First update
    node_data1 = {
        'id': 'node_0',
        'status': 'healthy',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 95
    }
    status_card.update_data(node_data1)
    assert status_card.status_icon.text() == "🟢"
    
    # Second update with different data
    node_data2 = {
        'id': 'node_0',
        'status': 'under_attack',
        'response_time': 250,
        'role': 'validator',
        'trust_score': 50
    }
    status_card.update_data(node_data2)
    assert status_card.status_icon.text() == "🔴"
    assert "250ms" in status_card.response_time.text()
    assert status_card.metric_value.text() == "50"


def test_card_hover_styling(status_card):
    """Test card has hover effect in stylesheet."""
    # Check that hover style is defined
    assert 'hover' in status_card.styleSheet().lower()


def test_card_background_color(status_card):
    """Test card has dark background color."""
    assert '#2D2D2D' in status_card.styleSheet()


def test_card_border_radius(status_card):
    """Test card has rounded corners."""
    assert 'border-radius' in status_card.styleSheet()
    assert '8px' in status_card.styleSheet()


def test_progress_bar_no_text(status_card):
    """Test progress bar has no text (only visual)."""
    assert not status_card.progress_bar.isTextVisible()


def test_card_labels_font_styling(status_card):
    """Test labels have appropriate font styling."""
    # Node label should be bold
    assert 'bold' in status_card.node_label.styleSheet().lower()
    
    # Metric value should be bold
    assert 'bold' in status_card.metric_value.styleSheet().lower()


def test_different_node_ids(qapp):
    """Test creating cards with different node IDs."""
    card1 = NodeStatusCard('validator_0')
    card2 = NodeStatusCard('node_5')
    card3 = NodeStatusCard('byzantine_node_1')
    
    assert card1.node_id == 'validator_0'
    assert card2.node_id == 'node_5'
    assert card3.node_id == 'byzantine_node_1'
    
    assert card1.node_label.text() == 'validator_0'
    assert card2.node_label.text() == 'node_5'
    assert card3.node_label.text() == 'byzantine_node_1'


def test_card_layout_structure(status_card):
    """Test card has proper layout structure."""
    # Should have vertical layout
    assert status_card.layout() is not None
    # Should have multiple child widgets
    assert status_card.layout().count() > 0


def test_response_time_formatting(status_card):
    """Test response time is formatted correctly."""
    node_data = {
        'id': 'node_0',
        'status': 'healthy',
        'response_time': 123,
        'role': 'validator',
        'trust_score': 90
    }
    
    status_card.update_data(node_data)
    
    # Should show "RT: 123ms"
    text = status_card.response_time.text()
    assert 'RT:' in text
    assert '123' in text
    assert 'ms' in text


def test_trust_score_as_integer(status_card):
    """Test trust score is displayed as integer."""
    node_data = {
        'id': 'validator_0',
        'status': 'healthy',
        'response_time': 50,
        'role': 'validator',
        'trust_score': 87.6  # Float input
    }
    
    status_card.update_data(node_data)
    
    # Should convert to integer
    assert status_card.metric_value.text() == "87"
    assert status_card.progress_bar.value() == 87


def test_balance_as_integer(status_card):
    """Test balance is displayed as integer."""
    node_data = {
        'id': 'node_1',
        'status': 'healthy',
        'response_time': 50,
        'role': 'regular',
        'balance': 456.78  # Float input
    }
    
    status_card.update_data(node_data)
    
    # Should convert to integer
    assert status_card.metric_value.text() == "456"
