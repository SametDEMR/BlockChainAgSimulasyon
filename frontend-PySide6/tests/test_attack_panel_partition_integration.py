"""Integration tests for Network Partition Attack Panel - Milestone 6.6"""
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


# ============ Partition Attack Tests ============

def test_partition_always_allows_attack(attack_panel):
    """Test Partition attack doesn't require parameters."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    assert len(captured_signals) == 1


def test_partition_attack_type_is_correct(attack_panel):
    """Test Partition attack type is 'partition'."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "partition"


def test_partition_params_are_empty(attack_panel):
    """Test Partition attack has empty parameters."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    attack_type, params = captured_signals[0]
    assert params == {}
    assert len(params) == 0


# ============ API Call Format Test ============

def test_partition_params_format_for_api(attack_panel):
    """Test Partition parameters are in correct format for API call."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    attack_type, params = captured_signals[0]
    
    assert isinstance(params, dict)
    assert len(params) == 0


# ============ Multiple Triggers Test ============

def test_partition_multiple_triggers(attack_panel):
    """Test multiple Partition attack triggers."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    attack_panel._trigger_partition()
    
    assert len(captured_signals) == 2
    
    for attack_type, params in captured_signals:
        assert attack_type == "partition"
        assert params == {}


# ============ Full Integration Test ============

def test_partition_full_attack_flow(attack_panel):
    """Test complete Partition attack flow from UI to signal."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "partition"
    assert params == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
