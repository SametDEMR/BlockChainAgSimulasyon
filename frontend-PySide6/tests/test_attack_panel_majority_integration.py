"""Integration tests for Majority Attack Panel - Milestone 6.5"""
import pytest
from PySide6.QtWidgets import QApplication
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


# ============ Majority Attack Tests ============

def test_majority_always_allows_attack(attack_panel):
    """Test Majority attack doesn't require parameters."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    # Should always emit signal (no validation needed)
    assert len(captured_signals) == 1


def test_majority_attack_type_is_correct(attack_panel):
    """Test Majority attack type is 'majority'."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "majority"


def test_majority_params_are_empty(attack_panel):
    """Test Majority attack has empty parameters."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    attack_type, params = captured_signals[0]
    assert params == {}
    assert len(params) == 0


# ============ API Call Format Test ============

def test_majority_params_format_for_api(attack_panel):
    """Test Majority parameters are in correct format for API call."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    attack_type, params = captured_signals[0]
    
    # Verify structure
    assert isinstance(params, dict)
    assert len(params) == 0  # Empty dict


# ============ Multiple Triggers Test ============

def test_majority_multiple_triggers(attack_panel):
    """Test multiple Majority attack triggers."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Trigger multiple times
    attack_panel._trigger_majority()
    attack_panel._trigger_majority()
    attack_panel._trigger_majority()
    
    # All should emit
    assert len(captured_signals) == 3
    
    # All should have same structure
    for attack_type, params in captured_signals:
        assert attack_type == "majority"
        assert params == {}


# ============ Full Integration Test ============

def test_majority_full_attack_flow(attack_panel):
    """Test complete Majority attack flow from UI to signal."""
    # 1. Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # 2. Trigger attack (no setup needed)
    attack_panel._trigger_majority()
    
    # 3. Verify signal
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "majority"
    assert params == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
