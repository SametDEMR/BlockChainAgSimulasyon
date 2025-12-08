"""Tests for Milestone 3.2 - Active Attacks Tracking."""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock
import sys

from ui.widgets.attack_panel_widget import AttackPanelWidget
from ui.widgets.active_attack_item import ActiveAttackItem


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


# ============ Active Attacks Section Tests ============

def test_active_attacks_section_exists(attack_panel):
    """Test Active Attacks section is created."""
    assert attack_panel.toolbox.count() == 7  # 6 attacks + 1 active
    assert "Active Attacks" in attack_panel.toolbox.itemText(6)


def test_active_attacks_list_exists(attack_panel):
    """Test active attacks list widget exists."""
    assert hasattr(attack_panel, 'active_attacks_list')
    assert attack_panel.active_attacks_list is not None


def test_initial_active_attacks_count(attack_panel):
    """Test initial active attacks count is 0."""
    assert attack_panel.get_active_attacks_count() == 0


def test_initial_title_shows_zero(attack_panel):
    """Test Active Attacks title shows (0)."""
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Add Active Attack Tests ============

def test_add_single_attack(attack_panel):
    """Test adding single active attack."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.3,
        "remaining_time": 20
    }
    
    attack_panel.add_active_attack(attack_data)
    
    assert attack_panel.get_active_attacks_count() == 1
    assert "attack_1" in attack_panel.active_attacks


def test_add_multiple_attacks(attack_panel):
    """Test adding multiple active attacks."""
    attacks = [
        {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.2, "remaining_time": 15},
        {"id": "attack_2", "type": "byzantine", "target": "node_1", "progress": 0.5, "remaining_time": 10},
        {"id": "attack_3", "type": "sybil", "progress": 0.7, "remaining_time": 5}
    ]
    
    for attack in attacks:
        attack_panel.add_active_attack(attack)
    
    assert attack_panel.get_active_attacks_count() == 3


def test_title_updates_on_add(attack_panel):
    """Test title updates when attack is added."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    
    title = attack_panel.toolbox.itemText(6)
    assert "(1)" in title


def test_duplicate_attack_id_ignored(attack_panel):
    """Test duplicate attack ID is ignored."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.add_active_attack(attack_data)  # Duplicate
    
    assert attack_panel.get_active_attacks_count() == 1


def test_empty_attack_id_ignored(attack_panel):
    """Test attack without ID is ignored."""
    attack_data = {"type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    
    assert attack_panel.get_active_attacks_count() == 0


# ============ Remove Active Attack Tests ============

def test_remove_existing_attack(attack_panel):
    """Test removing existing attack."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    assert attack_panel.get_active_attacks_count() == 1
    
    attack_panel.remove_active_attack("attack_1")
    assert attack_panel.get_active_attacks_count() == 0


def test_remove_nonexistent_attack(attack_panel):
    """Test removing non-existent attack doesn't cause error."""
    attack_panel.remove_active_attack("nonexistent")
    assert attack_panel.get_active_attacks_count() == 0


def test_title_updates_on_remove(attack_panel):
    """Test title updates when attack is removed."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.remove_active_attack("attack_1")
    
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Update Active Attack Tests ============

def test_update_attack_progress(attack_panel):
    """Test updating attack progress."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.update_active_attack("attack_1", 0.75, 10)
    
    # Verify item widget updated
    item = attack_panel.active_attacks["attack_1"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    
    assert isinstance(widget, ActiveAttackItem)
    assert widget.progress_bar.value() == 75


def test_update_nonexistent_attack(attack_panel):
    """Test updating non-existent attack doesn't cause error."""
    attack_panel.update_active_attack("nonexistent", 0.5, 15)


# ============ Clear Active Attacks Tests ============

def test_clear_all_attacks(attack_panel):
    """Test clearing all active attacks."""
    attacks = [
        {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.2, "remaining_time": 15},
        {"id": "attack_2", "type": "byzantine", "target": "node_1", "progress": 0.5, "remaining_time": 10},
    ]
    
    for attack in attacks:
        attack_panel.add_active_attack(attack)
    
    assert attack_panel.get_active_attacks_count() == 2
    
    attack_panel.clear_active_attacks()
    
    assert attack_panel.get_active_attacks_count() == 0
    assert len(attack_panel.active_attacks) == 0


def test_clear_updates_title(attack_panel):
    """Test clear updates title to (0)."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    attack_panel.add_active_attack(attack_data)
    
    attack_panel.clear_active_attacks()
    
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Stop Signal Tests ============

def test_stop_signal_emitted(attack_panel, qapp):
    """Test stop signal is emitted when stop button clicked."""
    attack_data = {"id": "attack_1", "type": "ddos", "target": "node_5", "progress": 0.0, "remaining_time": 30}
    attack_panel.add_active_attack(attack_data)
    
    # Capture signal
    captured_signals = []
    attack_panel.attack_stop_requested.connect(
        lambda attack_id: captured_signals.append(attack_id)
    )
    
    # Get widget and trigger stop
    item = attack_panel.active_attacks["attack_1"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    widget.stop_button.click()
    
    assert len(captured_signals) == 1
    assert captured_signals[0] == "attack_1"


# ============ ActiveAttackItem Widget Tests ============

def test_active_attack_item_creation(qapp):
    """Test ActiveAttackItem widget creation."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.5,
        "remaining_time": 20
    }
    
    item = ActiveAttackItem(attack_data)
    
    assert item is not None
    assert item.attack_id == "attack_1"


def test_active_attack_item_has_widgets(qapp):
    """Test ActiveAttackItem has required widgets."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.5,
        "remaining_time": 20
    }
    
    item = ActiveAttackItem(attack_data)
    
    assert hasattr(item, 'icon_label')
    assert hasattr(item, 'target_label')
    assert hasattr(item, 'progress_bar')
    assert hasattr(item, 'time_label')
    assert hasattr(item, 'stop_button')


def test_active_attack_item_progress_display(qapp):
    """Test progress bar displays correct value."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.75,
        "remaining_time": 10
    }
    
    item = ActiveAttackItem(attack_data)
    
    assert item.progress_bar.value() == 75


def test_active_attack_item_update_progress(qapp):
    """Test updating progress and time."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.3,
        "remaining_time": 20
    }
    
    item = ActiveAttackItem(attack_data)
    item.update_progress(0.9, 5)
    
    assert item.progress_bar.value() == 90
    assert "5s" in item.time_label.text()


def test_active_attack_item_icon_map(qapp):
    """Test different attack types have different icons."""
    attack_types = ["ddos", "byzantine", "sybil", "majority", "partition", "selfish_mining"]
    
    for attack_type in attack_types:
        attack_data = {
            "id": f"attack_{attack_type}",
            "type": attack_type,
            "target": "node_5",
            "progress": 0.0,
            "remaining_time": 30
        }
        
        item = ActiveAttackItem(attack_data)
        
        # Should have icon in label
        assert item.icon_label.text() != ""
        assert attack_type.upper() in item.icon_label.text()


def test_active_attack_item_network_wide_target(qapp):
    """Test attack without specific target shows 'Network-wide'."""
    attack_data = {
        "id": "attack_1",
        "type": "partition",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    item = ActiveAttackItem(attack_data)
    
    assert "Network-wide" in item.target_label.text()


def test_active_attack_item_stop_signal(qapp):
    """Test stop button emits signal."""
    attack_data = {
        "id": "attack_1",
        "type": "ddos",
        "target": "node_5",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    item = ActiveAttackItem(attack_data)
    
    captured_signals = []
    item.stop_requested.connect(lambda attack_id: captured_signals.append(attack_id))
    
    item.stop_button.click()
    
    assert len(captured_signals) == 1
    assert captured_signals[0] == "attack_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
