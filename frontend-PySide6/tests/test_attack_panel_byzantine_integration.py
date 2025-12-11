"""Integration tests for Byzantine Attack Panel - Milestone 6.3"""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock
import sys

from ui.widgets.attack_panel_widget import AttackPanelWidget
from core.api_client import APIClient


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


# ============ Byzantine Widget Structure Tests ============

def test_byzantine_has_target_dropdown(attack_panel):
    """Test Byzantine section has target dropdown."""
    assert hasattr(attack_panel, 'byzantine_target')
    assert attack_panel.byzantine_target is not None


def test_byzantine_default_item(attack_panel):
    """Test Byzantine dropdown has default item."""
    assert attack_panel.byzantine_target.count() >= 1
    assert attack_panel.byzantine_target.itemText(0) == "Select Validator..."


# ============ Byzantine Validator Filtering Tests ============

def test_byzantine_only_shows_validators(attack_panel):
    """Test Byzantine dropdown only contains validators."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
        {"id": "node_2", "is_validator": True},
        {"id": "node_3", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Should have 3 items: 1 default + 2 validators
    assert attack_panel.byzantine_target.count() == 3
    
    items = [attack_panel.byzantine_target.itemText(i) 
             for i in range(attack_panel.byzantine_target.count())]
    
    assert "Select Validator..." in items
    assert "node_0" in items
    assert "node_2" in items
    assert "node_1" not in items
    assert "node_3" not in items


def test_byzantine_filters_out_regular_nodes(attack_panel):
    """Test Byzantine excludes non-validator nodes."""
    nodes = [
        {"id": "validator_1", "is_validator": True},
        {"id": "regular_1", "is_validator": False},
        {"id": "regular_2", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    items = [attack_panel.byzantine_target.itemText(i) 
             for i in range(attack_panel.byzantine_target.count())]
    
    assert "validator_1" in items
    assert "regular_1" not in items
    assert "regular_2" not in items


# ============ Byzantine Parameter Validation Tests ============

def test_byzantine_validates_target_selection(attack_panel):
    """Test Byzantine validates target is selected."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Don't select target (default "Select Validator...")
    attack_panel._trigger_byzantine()
    
    # Should not emit signal
    assert len(captured_signals) == 0


def test_byzantine_allows_valid_attack(attack_panel):
    """Test Byzantine allows attack with valid validator."""
    # Setup valid parameters
    attack_panel.byzantine_target.addItem("validator_0")
    attack_panel.byzantine_target.setCurrentText("validator_0")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    # Should emit signal
    assert len(captured_signals) == 1


# ============ Byzantine Parameter Content Tests ============

def test_byzantine_params_include_target(attack_panel):
    """Test Byzantine parameters include target."""
    attack_panel.byzantine_target.addItem("validator_5")
    attack_panel.byzantine_target.setCurrentText("validator_5")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    attack_type, params = captured_signals[0]
    assert "target" in params
    assert params["target"] == "validator_5"


def test_byzantine_attack_type_is_correct(attack_panel):
    """Test Byzantine attack type is 'byzantine'."""
    attack_panel.byzantine_target.addItem("validator_1")
    attack_panel.byzantine_target.setCurrentText("validator_1")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "byzantine"


# ============ Byzantine with Mixed Nodes Tests ============

def test_byzantine_with_mixed_node_list(attack_panel):
    """Test Byzantine with mixed validators and regular nodes."""
    nodes = [
        {"id": "node_0", "is_validator": False},
        {"id": "node_1", "is_validator": True},
        {"id": "node_2", "is_validator": False},
        {"id": "node_3", "is_validator": True},
        {"id": "node_4", "is_validator": False},
        {"id": "node_5", "is_validator": True},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Should have 4 items: 1 default + 3 validators
    assert attack_panel.byzantine_target.count() == 4
    
    items = [attack_panel.byzantine_target.itemText(i) 
             for i in range(attack_panel.byzantine_target.count())]
    
    # Validators should be present
    assert "node_1" in items
    assert "node_3" in items
    assert "node_5" in items
    
    # Regular nodes should not be present
    assert "node_0" not in items
    assert "node_2" not in items
    assert "node_4" not in items


# ============ Full Integration Test ============

def test_byzantine_full_attack_flow(attack_panel):
    """Test complete Byzantine attack flow from UI to signal."""
    # 1. Populate node list with validators
    nodes = [
        {"id": "validator_0", "is_validator": True},
        {"id": "validator_1", "is_validator": True},
        {"id": "regular_0", "is_validator": False},
    ]
    attack_panel.update_node_list(nodes)
    
    # 2. Select validator target
    attack_panel.byzantine_target.setCurrentText("validator_1")
    
    # 3. Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # 4. Trigger attack
    attack_panel._trigger_byzantine()
    
    # 5. Verify signal
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "byzantine"
    assert params["target"] == "validator_1"


# ============ API Call Format Test ============

def test_byzantine_params_format_for_api(attack_panel):
    """Test Byzantine parameters are in correct format for API call."""
    attack_panel.byzantine_target.addItem("test_validator")
    attack_panel.byzantine_target.setCurrentText("test_validator")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    attack_type, params = captured_signals[0]
    
    # Verify structure
    assert isinstance(params, dict)
    assert len(params) == 1  # Only target
    assert "target" in params
    assert isinstance(params["target"], str)


# ============ Edge Cases ============

def test_byzantine_with_no_validators(attack_panel):
    """Test Byzantine when no validators exist."""
    nodes = [
        {"id": "node_0", "is_validator": False},
        {"id": "node_1", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Should only have default item
    assert attack_panel.byzantine_target.count() == 1
    assert attack_panel.byzantine_target.itemText(0) == "Select Validator..."


def test_byzantine_with_all_validators(attack_panel):
    """Test Byzantine when all nodes are validators."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": True},
        {"id": "node_2", "is_validator": True},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Should have 4 items: 1 default + 3 validators
    assert attack_panel.byzantine_target.count() == 4


def test_byzantine_preserves_validator_selection(attack_panel):
    """Test Byzantine preserves selection when node list updates."""
    # Initial setup
    nodes = [
        {"id": "validator_0", "is_validator": True},
        {"id": "validator_1", "is_validator": True},
    ]
    attack_panel.update_node_list(nodes)
    
    # Select a validator
    attack_panel.byzantine_target.setCurrentText("validator_1")
    
    # Update with same nodes
    attack_panel.update_node_list(nodes)
    
    # Selection should be preserved
    assert attack_panel.byzantine_target.currentText() == "validator_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
