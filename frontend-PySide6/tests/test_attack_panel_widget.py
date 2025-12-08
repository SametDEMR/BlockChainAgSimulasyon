"""Tests for AttackPanelWidget - Milestone 3.1."""
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


# ============ Basic Structure Tests ============

def test_attack_panel_creation(attack_panel):
    """Test widget is created successfully."""
    assert attack_panel is not None


def test_toolbox_exists(attack_panel):
    """Test QToolBox is created."""
    assert hasattr(attack_panel, 'toolbox')
    assert attack_panel.toolbox is not None


def test_toolbox_has_six_sections(attack_panel):
    """Test QToolBox has 6 attack sections."""
    assert attack_panel.toolbox.count() == 6


def test_toolbox_section_titles(attack_panel):
    """Test QToolBox section titles."""
    expected_titles = [
        "🌊 DDoS Attack",
        "⚔️ Byzantine Attack",
        "👥 Sybil Attack",
        "⚡ Majority Attack (51%)",
        "🔌 Network Partition",
        "💎 Selfish Mining"
    ]
    
    for i, expected in enumerate(expected_titles):
        assert attack_panel.toolbox.itemText(i) == expected


# ============ DDoS Section Tests ============

def test_ddos_section_has_target_dropdown(attack_panel):
    """Test DDoS section has target dropdown."""
    assert hasattr(attack_panel, 'ddos_target')
    assert attack_panel.ddos_target.count() >= 1  # At least "Select Target..."


def test_ddos_section_has_intensity_slider(attack_panel):
    """Test DDoS section has intensity slider."""
    assert hasattr(attack_panel, 'ddos_intensity')
    assert attack_panel.ddos_intensity.minimum() == 1
    assert attack_panel.ddos_intensity.maximum() == 10
    assert attack_panel.ddos_intensity.value() == 5


def test_ddos_intensity_label_updates(attack_panel):
    """Test DDoS intensity label updates with slider."""
    attack_panel.ddos_intensity.setValue(7)
    assert attack_panel.ddos_intensity_label.text() == "7"


# ============ Byzantine Section Tests ============

def test_byzantine_section_has_target_dropdown(attack_panel):
    """Test Byzantine section has target dropdown."""
    assert hasattr(attack_panel, 'byzantine_target')
    assert attack_panel.byzantine_target.count() >= 1  # At least "Select Validator..."


# ============ Sybil Section Tests ============

def test_sybil_section_has_count_slider(attack_panel):
    """Test Sybil section has fake nodes count slider."""
    assert hasattr(attack_panel, 'sybil_count')
    assert attack_panel.sybil_count.minimum() == 5
    assert attack_panel.sybil_count.maximum() == 50
    assert attack_panel.sybil_count.value() == 10


def test_sybil_count_label_updates(attack_panel):
    """Test Sybil count label updates with slider."""
    attack_panel.sybil_count.setValue(25)
    assert attack_panel.sybil_count_label.text() == "25"


# ============ Selfish Mining Section Tests ============

def test_selfish_section_has_attacker_dropdown(attack_panel):
    """Test Selfish Mining section has attacker dropdown."""
    assert hasattr(attack_panel, 'selfish_attacker')
    assert attack_panel.selfish_attacker.count() >= 1  # At least "Select Miner..."


# ============ Signal Tests ============

def test_ddos_attack_signal(attack_panel, qapp):
    """Test DDoS attack signal emission."""
    # Setup
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel.ddos_intensity.setValue(8)
    
    # Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Trigger
    attack_panel._trigger_ddos()
    
    # Verify signal emitted
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "ddos"
    assert params["target"] == "node_0"
    assert params["intensity"] == 8


def test_byzantine_attack_signal(attack_panel, qapp):
    """Test Byzantine attack signal emission."""
    # Setup
    attack_panel.byzantine_target.addItem("node_1")
    attack_panel.byzantine_target.setCurrentText("node_1")
    
    # Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Trigger
    attack_panel._trigger_byzantine()
    
    # Verify
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "byzantine"
    assert params["target"] == "node_1"


def test_sybil_attack_signal(attack_panel, qapp):
    """Test Sybil attack signal emission."""
    # Setup
    attack_panel.sybil_count.setValue(20)
    
    # Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Trigger
    attack_panel._trigger_sybil()
    
    # Verify
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "sybil"
    assert params["fake_node_count"] == 20


def test_majority_attack_signal(attack_panel, qapp):
    """Test Majority attack signal emission."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "majority"
    assert params == {}


def test_partition_attack_signal(attack_panel, qapp):
    """Test Network Partition signal emission."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "partition"
    assert params == {}


def test_selfish_mining_signal(attack_panel, qapp):
    """Test Selfish Mining signal emission."""
    # Setup
    attack_panel.selfish_attacker.addItem("node_2")
    attack_panel.selfish_attacker.setCurrentText("node_2")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    assert attack_type == "selfish_mining"
    assert params["attacker_id"] == "node_2"


# ============ No Signal on Invalid Input Tests ============

def test_ddos_no_signal_without_target(attack_panel, qapp):
    """Test DDoS doesn't emit signal without valid target."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # No target selected (default "Select Target...")
    attack_panel._trigger_ddos()
    
    assert len(captured_signals) == 0


def test_byzantine_no_signal_without_target(attack_panel, qapp):
    """Test Byzantine doesn't emit signal without valid target."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # No validator selected
    attack_panel._trigger_byzantine()
    
    assert len(captured_signals) == 0


def test_selfish_no_signal_without_attacker(attack_panel, qapp):
    """Test Selfish Mining doesn't emit signal without valid attacker."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # No miner selected
    attack_panel._trigger_selfish()
    
    assert len(captured_signals) == 0


# ============ Update Node List Tests ============

def test_update_node_list_empty(attack_panel):
    """Test updating with empty node list."""
    attack_panel.update_node_list([])
    
    # Should only have default items
    assert attack_panel.ddos_target.count() == 1
    assert attack_panel.byzantine_target.count() == 1
    assert attack_panel.selfish_attacker.count() == 1


def test_update_node_list_with_nodes(attack_panel):
    """Test updating with node list."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": True},
        {"id": "node_2", "is_validator": False},
        {"id": "node_3", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # DDoS should have all nodes + default
    assert attack_panel.ddos_target.count() == 5  # 1 default + 4 nodes
    
    # Byzantine should have only validators + default
    assert attack_panel.byzantine_target.count() == 3  # 1 default + 2 validators
    
    # Selfish should have all nodes + default
    assert attack_panel.selfish_attacker.count() == 5  # 1 default + 4 nodes


def test_update_node_list_preserves_selection(attack_panel):
    """Test updating node list preserves current selection."""
    # Initial setup
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
    ]
    attack_panel.update_node_list(nodes)
    
    # Select node_0
    attack_panel.ddos_target.setCurrentText("node_0")
    
    # Update again with same nodes
    attack_panel.update_node_list(nodes)
    
    # Selection should be preserved
    assert attack_panel.ddos_target.currentText() == "node_0"


def test_update_node_list_validators_only_in_byzantine(attack_panel):
    """Test Byzantine dropdown only contains validators."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
        {"id": "node_2", "is_validator": True},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Check Byzantine dropdown
    byzantine_items = [
        attack_panel.byzantine_target.itemText(i) 
        for i in range(attack_panel.byzantine_target.count())
    ]
    
    assert "Select Validator..." in byzantine_items
    assert "node_0" in byzantine_items
    assert "node_2" in byzantine_items
    assert "node_1" not in byzantine_items  # Not a validator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
