"""Integration tests for DDoS Attack Panel - Milestone 6.2"""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, patch
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


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    return Mock(spec=APIClient)


# ============ DDoS Widget Structure Tests ============

def test_ddos_has_target_dropdown(attack_panel):
    """Test DDoS section has target dropdown."""
    assert hasattr(attack_panel, 'ddos_target')
    assert attack_panel.ddos_target is not None


def test_ddos_has_intensity_slider(attack_panel):
    """Test DDoS section has intensity slider."""
    assert hasattr(attack_panel, 'ddos_intensity')
    assert attack_panel.ddos_intensity.minimum() == 1
    assert attack_panel.ddos_intensity.maximum() == 10


def test_ddos_default_intensity_is_5(attack_panel):
    """Test DDoS intensity default value is 5."""
    assert attack_panel.ddos_intensity.value() == 5


def test_ddos_intensity_label_exists(attack_panel):
    """Test DDoS intensity label exists."""
    assert hasattr(attack_panel, 'ddos_intensity_label')
    assert attack_panel.ddos_intensity_label.text() == "5"


# ============ DDoS Parameter Validation Tests ============

def test_ddos_validates_target_selection(attack_panel):
    """Test DDoS validates target is selected."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # Don't select target (default "Select Target...")
    attack_panel._trigger_ddos()
    
    # Should not emit signal
    assert len(captured_signals) == 0


def test_ddos_allows_valid_attack(attack_panel):
    """Test DDoS allows attack with valid parameters."""
    # Setup valid parameters
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel.ddos_intensity.setValue(8)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    # Should emit signal
    assert len(captured_signals) == 1


# ============ DDoS Parameter Content Tests ============

def test_ddos_params_include_target(attack_panel):
    """Test DDoS parameters include target."""
    attack_panel.ddos_target.addItem("node_5")
    attack_panel.ddos_target.setCurrentText("node_5")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    assert "target" in params
    assert params["target"] == "node_5"


def test_ddos_params_include_intensity(attack_panel):
    """Test DDoS parameters include intensity."""
    attack_panel.ddos_target.addItem("node_3")
    attack_panel.ddos_target.setCurrentText("node_3")
    attack_panel.ddos_intensity.setValue(9)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    assert "intensity" in params
    assert params["intensity"] == 9


def test_ddos_attack_type_is_correct(attack_panel):
    """Test DDoS attack type is 'ddos'."""
    attack_panel.ddos_target.addItem("node_1")
    attack_panel.ddos_target.setCurrentText("node_1")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    assert attack_type == "ddos"


# ============ DDoS Intensity Range Tests ============

def test_ddos_intensity_min_value(attack_panel):
    """Test DDoS intensity minimum is 1."""
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel.ddos_intensity.setValue(1)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    assert params["intensity"] == 1


def test_ddos_intensity_max_value(attack_panel):
    """Test DDoS intensity maximum is 10."""
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel.ddos_intensity.setValue(10)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    assert params["intensity"] == 10


# ============ DDoS UI Interaction Tests ============

def test_ddos_intensity_label_updates_with_slider(attack_panel):
    """Test intensity label updates when slider moves."""
    attack_panel.ddos_intensity.setValue(3)
    assert attack_panel.ddos_intensity_label.text() == "3"
    
    attack_panel.ddos_intensity.setValue(7)
    assert attack_panel.ddos_intensity_label.text() == "7"


def test_ddos_target_dropdown_populated_by_node_list(attack_panel):
    """Test target dropdown is populated by update_node_list."""
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
        {"id": "node_2", "is_validator": False},
    ]
    
    attack_panel.update_node_list(nodes)
    
    # Should have 4 items: 1 default + 3 nodes
    assert attack_panel.ddos_target.count() == 4
    
    # Check items exist
    items = [attack_panel.ddos_target.itemText(i) for i in range(attack_panel.ddos_target.count())]
    assert "node_0" in items
    assert "node_1" in items
    assert "node_2" in items


# ============ Full Integration Test ============

def test_ddos_full_attack_flow(attack_panel):
    """Test complete DDoS attack flow from UI to signal."""
    # 1. Populate node list
    nodes = [
        {"id": "node_0", "is_validator": True},
        {"id": "node_1", "is_validator": False},
    ]
    attack_panel.update_node_list(nodes)
    
    # 2. Select target
    attack_panel.ddos_target.setCurrentText("node_1")
    
    # 3. Set intensity
    attack_panel.ddos_intensity.setValue(7)
    
    # 4. Capture signal
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # 5. Trigger attack
    attack_panel._trigger_ddos()
    
    # 6. Verify signal
    assert len(captured_signals) == 1
    attack_type, params = captured_signals[0]
    
    assert attack_type == "ddos"
    assert params["target"] == "node_1"
    assert params["intensity"] == 7


# ============ API Call Format Test ============

def test_ddos_params_format_for_api(attack_panel):
    """Test DDoS parameters are in correct format for API call."""
    attack_panel.ddos_target.addItem("test_node")
    attack_panel.ddos_target.setCurrentText("test_node")
    attack_panel.ddos_intensity.setValue(6)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    
    # Verify structure
    assert isinstance(params, dict)
    assert len(params) == 2  # Only target and intensity
    assert isinstance(params["target"], str)
    assert isinstance(params["intensity"], int)
    assert params["intensity"] >= 1
    assert params["intensity"] <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
