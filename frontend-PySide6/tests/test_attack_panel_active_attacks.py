"""Integration tests for Active Attacks Section - Milestone 6.8"""
import pytest
from PySide6.QtWidgets import QApplication
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


# ============ Active Attacks List Structure Tests ============

def test_active_attacks_list_exists(attack_panel):
    """Test active attacks list widget exists."""
    assert hasattr(attack_panel, 'active_attacks_list')
    assert attack_panel.active_attacks_list is not None


def test_initial_active_attacks_count_is_zero(attack_panel):
    """Test initial active attacks count is 0."""
    assert attack_panel.get_active_attacks_count() == 0
    assert len(attack_panel.active_attacks) == 0


def test_active_attacks_section_title_shows_zero(attack_panel):
    """Test Active Attacks section title shows (0) initially."""
    # Section 6 is Active Attacks
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Add Active Attack Tests ============

def test_add_single_active_attack(attack_panel):
    """Test adding a single active attack."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    
    assert attack_panel.get_active_attacks_count() == 1
    assert "attack_001" in attack_panel.active_attacks


def test_add_multiple_active_attacks(attack_panel):
    """Test adding multiple active attacks."""
    attacks = [
        {"id": "attack_001", "type": "ddos", "target": "node_0", "progress": 0.0, "remaining_time": 30},
        {"id": "attack_002", "type": "byzantine", "target": "node_1", "progress": 0.2, "remaining_time": 25},
        {"id": "attack_003", "type": "sybil", "target": "N/A", "progress": 0.5, "remaining_time": 15},
    ]
    
    for attack_data in attacks:
        attack_panel.add_active_attack(attack_data)
    
    assert attack_panel.get_active_attacks_count() == 3


def test_add_active_attack_updates_title(attack_panel):
    """Test adding attack updates section title count."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    
    title = attack_panel.toolbox.itemText(6)
    assert "(1)" in title


def test_cannot_add_duplicate_attack_id(attack_panel):
    """Test cannot add attack with duplicate ID."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.add_active_attack(attack_data)  # Try to add again
    
    # Should still be 1
    assert attack_panel.get_active_attacks_count() == 1


# ============ Remove Active Attack Tests ============

def test_remove_active_attack(attack_panel):
    """Test removing an active attack."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    assert attack_panel.get_active_attacks_count() == 1
    
    attack_panel.remove_active_attack("attack_001")
    assert attack_panel.get_active_attacks_count() == 0


def test_remove_nonexistent_attack(attack_panel):
    """Test removing nonexistent attack doesn't crash."""
    attack_panel.remove_active_attack("nonexistent_id")
    # Should not crash


def test_remove_one_of_multiple_attacks(attack_panel):
    """Test removing one attack from multiple."""
    attacks = [
        {"id": "attack_001", "type": "ddos", "target": "node_0", "progress": 0.0, "remaining_time": 30},
        {"id": "attack_002", "type": "sybil", "target": "N/A", "progress": 0.0, "remaining_time": 30},
    ]
    
    for attack_data in attacks:
        attack_panel.add_active_attack(attack_data)
    
    attack_panel.remove_active_attack("attack_001")
    
    assert attack_panel.get_active_attacks_count() == 1
    assert "attack_001" not in attack_panel.active_attacks
    assert "attack_002" in attack_panel.active_attacks


def test_remove_updates_title(attack_panel):
    """Test removing attack updates section title."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.remove_active_attack("attack_001")
    
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Update Active Attack Tests ============

def test_update_active_attack_progress(attack_panel):
    """Test updating attack progress."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.update_active_attack("attack_001", 0.5, 15)
    
    # Get widget and verify update
    item = attack_panel.active_attacks["attack_001"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    
    assert isinstance(widget, ActiveAttackItem)
    assert widget.progress_bar.value() == 50  # 0.5 * 100


def test_update_nonexistent_attack(attack_panel):
    """Test updating nonexistent attack doesn't crash."""
    attack_panel.update_active_attack("nonexistent_id", 0.5, 15)
    # Should not crash


# ============ Clear All Attacks Tests ============

def test_clear_active_attacks(attack_panel):
    """Test clearing all active attacks."""
    attacks = [
        {"id": "attack_001", "type": "ddos", "target": "node_0", "progress": 0.0, "remaining_time": 30},
        {"id": "attack_002", "type": "sybil", "target": "N/A", "progress": 0.0, "remaining_time": 30},
    ]
    
    for attack_data in attacks:
        attack_panel.add_active_attack(attack_data)
    
    attack_panel.clear_active_attacks()
    
    assert attack_panel.get_active_attacks_count() == 0
    assert len(attack_panel.active_attacks) == 0


def test_clear_updates_title(attack_panel):
    """Test clear updates section title to (0)."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    attack_panel.clear_active_attacks()
    
    title = attack_panel.toolbox.itemText(6)
    assert "(0)" in title


# ============ Stop Button Signal Tests ============

def test_stop_button_emits_signal(attack_panel):
    """Test stop button emits attack_stop_requested signal."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    
    captured_signals = []
    attack_panel.attack_stop_requested.connect(
        lambda attack_id: captured_signals.append(attack_id)
    )
    
    # Get widget and click stop button
    item = attack_panel.active_attacks["attack_001"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    widget.stop_button.click()
    
    assert len(captured_signals) == 1
    assert captured_signals[0] == "attack_001"


# ============ Attack Type Display Tests ============

def test_ddos_attack_display(attack_panel):
    """Test DDoS attack displays correctly."""
    attack_data = {
        "id": "attack_001",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.3,
        "remaining_time": 20
    }
    
    attack_panel.add_active_attack(attack_data)
    
    item = attack_panel.active_attacks["attack_001"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    
    assert "🌊" in widget.icon_label.text()
    assert "DDOS" in widget.icon_label.text().upper()
    assert "node_0" in widget.target_label.text()


def test_sybil_attack_display(attack_panel):
    """Test Sybil attack displays correctly."""
    attack_data = {
        "id": "attack_002",
        "type": "sybil",
        "target": "N/A",
        "progress": 0.0,
        "remaining_time": 30
    }
    
    attack_panel.add_active_attack(attack_data)
    
    item = attack_panel.active_attacks["attack_002"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    
    assert "👥" in widget.icon_label.text()
    assert "Network-wide" in widget.target_label.text()


# ============ Full Integration Test ============

def test_full_active_attacks_lifecycle(attack_panel):
    """Test complete lifecycle of active attacks."""
    # 1. Add multiple attacks
    attacks = [
        {"id": "attack_001", "type": "ddos", "target": "node_0", "progress": 0.0, "remaining_time": 30},
        {"id": "attack_002", "type": "byzantine", "target": "node_1", "progress": 0.0, "remaining_time": 25},
    ]
    
    for attack_data in attacks:
        attack_panel.add_active_attack(attack_data)
    
    assert attack_panel.get_active_attacks_count() == 2
    
    # 2. Update progress
    attack_panel.update_active_attack("attack_001", 0.5, 15)
    
    # 3. Remove one attack
    attack_panel.remove_active_attack("attack_002")
    assert attack_panel.get_active_attacks_count() == 1
    
    # 4. Clear all
    attack_panel.clear_active_attacks()
    assert attack_panel.get_active_attacks_count() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
