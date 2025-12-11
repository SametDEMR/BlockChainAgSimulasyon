"""Integration tests for Sybil Attack Panel - Milestone 6.4"""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock
import sys

from ui.widgets.attack_panel_widget import AttackPanelWidget


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def attack_panel(qapp):
    """Create AttackPanelWidget instance."""
    widget = AttackPanelWidget()
    return widget


# ============ Sybil Widget Structure Tests ============

def test_sybil_has_count_slider(attack_panel):
    """Test Sybil section has fake nodes count slider."""
    assert hasattr(attack_panel, 'sybil_count')
    assert attack_panel.sybil_count is not None


def test_sybil_slider_range(attack_panel):
    """Test Sybil slider has correct range (5-50)."""
    assert attack_panel.sybil_count.minimum() == 5
    assert attack_panel.sybil_count.maximum() == 50


def test_sybil_default_count_is_10(attack_panel):
    """Test Sybil default fake node count is 10."""
    assert attack_panel.sybil_count.value() == 10


def test_sybil_count_label_exists(attack_panel):
    """Test Sybil count label exists."""
    assert hasattr(attack_panel, 'sybil_count_label')
    assert attack_panel.sybil_count_label.text() == "10"


# ============ Sybil Parameter Tests ============

def test_sybil_always_allows_attack(attack_panel):
    """Test Sybil attack doesn't require node selection."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    # Should always emit signal (no validation needed)
    assert len(captured_signals) == 1


def test_sybil_params_include_fake_node_count(attack_panel):
    """Test Sybil parameters include fake_node_count."""
    attack_panel.sybil_count.setValue(25)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    assert "fake_node_count" in params
    assert params["fake_node_count"] == 25


def test_sybil_attack_type_is_correct(attack_panel):
    """Test Sybil attack type is 'sybil'."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "sybil"


# ============ Sybil Count Range Tests ============

def test_sybil_min_count_value(attack_panel):
    """Test Sybil minimum fake node count (5)."""
    attack_panel.sybil_count.setValue(5)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    assert params["fake_node_count"] == 5


def test_sybil_max_count_value(attack_panel):
    """Test Sybil maximum fake node count (50)."""
    attack_panel.sybil_count.setValue(50)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    assert params["fake_node_count"] == 50


def test_sybil_mid_range_value(attack_panel):
    """Test Sybil mid-range value."""
    attack_panel.sybil_count.setValue(30)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    assert params["fake_node_count"] == 30


# ============ Sybil UI Interaction Tests ============

def test_sybil_count_label_updates_with_slider(attack_panel):
    """Test count label updates when slider moves."""
    attack_panel.sybil_count.setValue(15)
    assert attack_panel.sybil_count_label.text() == "15"
    
    attack_panel.sybil_count.setValue(40)
    assert attack_panel.sybil_count_label.text() == "40"
    
    attack_panel.sybil_count.setValue(8)
    assert attack_panel.sybil_count_label.text() == "8"


# ============ Full Integration Test ============

def test_sybil_full_attack_flow(attack_panel):
    """Test complete Sybil attack flow from UI to signal."""
    # 1. Set fake node count
    attack_panel.sybil_count.setValue(20)
    
    # 2. Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # 3. Trigger attack
    attack_panel._trigger_sybil()
    
    # 4. Verify signal
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "sybil"
    assert params["fake_node_count"] == 20


# ============ API Call Format Test ============

def test_sybil_params_format_for_api(attack_panel):
    """Test Sybil parameters are in correct format for API call."""
    attack_panel.sybil_count.setValue(35)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    
    # Verify structure
    assert isinstance(params, dict)
    assert len(params) == 1  # Only fake_node_count
    assert "fake_node_count" in params
    assert isinstance(params["fake_node_count"], int)
    assert params["fake_node_count"] >= 5
    assert params["fake_node_count"] <= 50


# ============ Multiple Triggers Test ============

def test_sybil_multiple_triggers_with_different_counts(attack_panel):
    """Test multiple Sybil attacks with different counts."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # First attack with 10 nodes
    attack_panel.sybil_count.setValue(10)
    attack_panel._trigger_sybil()
    
    # Second attack with 30 nodes
    attack_panel.sybil_count.setValue(30)
    attack_panel._trigger_sybil()
    
    # Third attack with 45 nodes
    attack_panel.sybil_count.setValue(45)
    attack_panel._trigger_sybil()
    
    # Verify all signals
    assert len(captured_signals) == 3
    assert captured_signals[0][1]["fake_node_count"] == 10
    assert captured_signals[1][1]["fake_node_count"] == 30
    assert captured_signals[2][1]["fake_node_count"] == 45


# ============ Edge Cases ============

def test_sybil_with_boundary_values(attack_panel):
    """Test Sybil at exact boundary values."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Test minimum boundary
    attack_panel.sybil_count.setValue(5)
    attack_panel._trigger_sybil()
    assert captured_signals[-1][1]["fake_node_count"] == 5
    
    # Test maximum boundary
    attack_panel.sybil_count.setValue(50)
    attack_panel._trigger_sybil()
    assert captured_signals[-1][1]["fake_node_count"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
