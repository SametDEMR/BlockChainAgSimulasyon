"""Integration tests for Selfish Mining Attack Panel - Milestone 6.7"""
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


# ============ Selfish Mining Widget Structure Tests ============

def test_selfish_has_attacker_dropdown(attack_panel):
    """Test Selfish Mining section has attacker dropdown."""
    assert hasattr(attack_panel, 'selfish_attacker')
    assert attack_panel.selfish_attacker is not None


def test_selfish_default_item(attack_panel):
    """Test Selfish dropdown has default item."""
    assert attack_panel.selfish_attacker.count() >= 1
    assert attack_panel.selfish_attacker.itemText(0) == "Select Miner..."


# ============ Selfish Mining Validation Tests ============

def test_selfish_validates_attacker_selection(attack_panel):
    """Test Selfish Mining validates attacker is selected."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    assert len(captured_signals) == 0


def test_selfish_allows_valid_attack(attack_panel):
    """Test Selfish Mining allows attack with valid attacker."""
    attack_panel.selfish_attacker.addItem("miner_0")
    attack_panel.selfish_attacker.setCurrentText("miner_0")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    assert len(captured_signals) == 1


# ============ Selfish Mining Parameter Tests ============

def test_selfish_params_include_attacker_id(attack_panel):
    """Test Selfish Mining parameters include attacker_id."""
    attack_panel.selfish_attacker.addItem("node_5")
    attack_panel.selfish_attacker.setCurrentText("node_5")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    attack_type, params = captured_signals[0]
    assert "attacker_id" in params
    assert params["attacker_id"] == "node_5"


def test_selfish_attack_type_is_correct(attack_panel):
    """Test Selfish Mining attack type is 'selfish_mining'."""
    attack_panel.selfish_attacker.addItem("node_1")
    attack_panel.selfish_attacker.setCurrentText("node_1")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "selfish_mining"


# ============ Selfish Mining Node List Tests ============

def test_selfish_dropdown_populated_by_node_list(attack_panel):
    """Test attacker dropdown is populated by update_node_list."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
        {"id": "node_2", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    assert attack_panel.selfish_attacker.count() == 4  # 1 default + 3 nodes
    
    items = [attack_panel.selfish_attacker.itemText(i) 
             for i in range(attack_panel.selfish_attacker.count())]
    assert "node_0" in items
    assert "node_1" in items
    assert "node_2" in items


def test_selfish_includes_all_nodes(attack_panel):
    """Test Selfish Mining includes both validators and regular nodes."""
    nodes = [
        {"id": "validator_0", "is_validator": True},
        {"id": "validator_1", "is_validator": True},
        {"id": "regular_0", "is_validator": False},
        {"id": "regular_1", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    items = [attack_panel.selfish_attacker.itemText(i) 
             for i in range(attack_panel.selfish_attacker.count())]
    
    assert "validator_0" in items
    assert "validator_1" in items
    assert "regular_0" in items
    assert "regular_1" in items


# ============ Full Integration Test ============

def test_selfish_full_attack_flow(attack_panel):
    """Test complete Selfish Mining attack flow from UI to signal."""
    nodes = [
        {"id": "miner_0", "is_validator": False},
        {"id": "miner_1", "is_validator": False},
    ]
    attack_panel.update_node_list(nodes)
    
    attack_panel.selfish_attacker.setCurrentText("miner_1")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "selfish_mining"
    assert params["attacker_id"] == "miner_1"


# ============ API Call Format Test ============

def test_selfish_params_format_for_api(attack_panel):
    """Test Selfish Mining parameters are in correct format for API call."""
    attack_panel.selfish_attacker.addItem("test_miner")
    attack_panel.selfish_attacker.setCurrentText("test_miner")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    attack_type, params = captured_signals[0]
    
    assert isinstance(params, dict)
    assert len(params) == 1
    assert "attacker_id" in params
    assert isinstance(params["attacker_id"], str)


# ============ Edge Cases ============

def test_selfish_preserves_selection(attack_panel):
    """Test Selfish Mining preserves selection when node list updates."""
    nodes = [
        {"id": "node_0", "is_validator": False},
        {"id": "node_1", "is_validator": False},
    ]
    attack_panel.update_node_list(nodes)
    
    attack_panel.selfish_attacker.setCurrentText("node_1")
    
    attack_panel.update_node_list(nodes)
    
    assert attack_panel.selfish_attacker.currentText() == "node_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
