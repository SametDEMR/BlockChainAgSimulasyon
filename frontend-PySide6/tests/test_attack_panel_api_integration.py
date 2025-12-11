"""API Integration tests for Attack Panel - Milestone 6.9"""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, MagicMock
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
    client = Mock(spec=APIClient)
    client.trigger_attack = Mock(return_value={"attack_id": "test_123", "duration": 30})
    client.stop_attack = Mock(return_value={"status": "stopped"})
    return client


# ============ DDoS API Integration Tests ============

def test_ddos_signal_contains_correct_api_format(attack_panel):
    """Test DDoS signal provides data in API-compatible format."""
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel.ddos_intensity.setValue(7)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    
    # Verify API call format: trigger_attack(type, target, parameters)
    assert attack_type == "ddos"
    assert "target" in params
    assert "intensity" in params
    assert params["target"] == "node_0"
    assert params["intensity"] == 7


def test_ddos_params_can_be_passed_to_api_client(attack_panel, mock_api_client):
    """Test DDoS params can be used with API client."""
    attack_panel.ddos_target.addItem("node_5")
    attack_panel.ddos_target.setCurrentText("node_5")
    attack_panel.ddos_intensity.setValue(8)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    
    # Simulate API call
    target = params.get("target")
    result = mock_api_client.trigger_attack(attack_type, target, params)
    
    mock_api_client.trigger_attack.assert_called_once_with("ddos", "node_5", params)
    assert result["attack_id"] == "test_123"


# ============ Byzantine API Integration Tests ============

def test_byzantine_signal_contains_correct_api_format(attack_panel):
    """Test Byzantine signal provides data in API-compatible format."""
    attack_panel.byzantine_target.addItem("validator_0")
    attack_panel.byzantine_target.setCurrentText("validator_0")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    attack_type, params = captured_signals[0]
    
    assert attack_type == "byzantine"
    assert "target" in params
    assert params["target"] == "validator_0"


def test_byzantine_params_can_be_passed_to_api_client(attack_panel, mock_api_client):
    """Test Byzantine params can be used with API client."""
    attack_panel.byzantine_target.addItem("validator_1")
    attack_panel.byzantine_target.setCurrentText("validator_1")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_byzantine()
    
    attack_type, params = captured_signals[0]
    target = params.get("target")
    
    result = mock_api_client.trigger_attack(attack_type, target, params)
    
    mock_api_client.trigger_attack.assert_called_once()
    assert result["attack_id"] == "test_123"


# ============ Sybil API Integration Tests ============

def test_sybil_signal_contains_correct_api_format(attack_panel):
    """Test Sybil signal provides data in API-compatible format."""
    attack_panel.sybil_count.setValue(25)
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_sybil()
    
    attack_type, params = captured_signals[0]
    
    assert attack_type == "sybil"
    assert "fake_node_count" in params
    assert params["fake_node_count"] == 25


# ============ Majority API Integration Tests ============

def test_majority_signal_contains_correct_api_format(attack_panel):
    """Test Majority signal provides data in API-compatible format."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    attack_type, params = captured_signals[0]
    
    assert attack_type == "majority"
    assert params == {}


def test_majority_params_can_be_passed_to_api_client(attack_panel, mock_api_client):
    """Test Majority params can be used with API client."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_majority()
    
    attack_type, params = captured_signals[0]
    target = params.get("target")
    
    result = mock_api_client.trigger_attack(attack_type, target, params)
    
    mock_api_client.trigger_attack.assert_called_once_with("majority", None, {})


# ============ Partition API Integration Tests ============

def test_partition_signal_contains_correct_api_format(attack_panel):
    """Test Partition signal provides data in API-compatible format."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_partition()
    
    attack_type, params = captured_signals[0]
    
    assert attack_type == "partition"
    assert params == {}


# ============ Selfish Mining API Integration Tests ============

def test_selfish_signal_contains_correct_api_format(attack_panel):
    """Test Selfish Mining signal provides data in API-compatible format."""
    attack_panel.selfish_attacker.addItem("miner_0")
    attack_panel.selfish_attacker.setCurrentText("miner_0")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_selfish()
    
    attack_type, params = captured_signals[0]
    
    assert attack_type == "selfish_mining"
    assert "attacker_id" in params
    assert params["attacker_id"] == "miner_0"


# ============ Stop Attack API Integration Tests ============

def test_stop_attack_signal_format(attack_panel, mock_api_client):
    """Test stop attack signal provides attack_id for API."""
    attack_data = {
        "id": "attack_123",
        "type": "ddos",
        "target": "node_0",
        "progress": 0.5,
        "remaining_time": 15
    }
    
    attack_panel.add_active_attack(attack_data)
    
    captured_signals = []
    attack_panel.attack_stop_requested.connect(
        lambda attack_id: captured_signals.append(attack_id)
    )
    
    # Trigger stop
    item = attack_panel.active_attacks["attack_123"]
    widget = attack_panel.active_attacks_list.itemWidget(item)
    widget.stop_button.click()
    
    assert len(captured_signals) == 1
    attack_id = captured_signals[0]
    
    # Verify can be used with API
    result = mock_api_client.stop_attack(attack_id)
    mock_api_client.stop_attack.assert_called_once_with("attack_123")


# ============ All Attack Types API Format Verification ============

def test_all_attack_types_have_valid_api_format(attack_panel):
    """Test all attack types produce valid API formats."""
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    # DDoS
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    attack_panel._trigger_ddos()
    
    # Byzantine
    attack_panel.byzantine_target.addItem("validator_0")
    attack_panel.byzantine_target.setCurrentText("validator_0")
    attack_panel._trigger_byzantine()
    
    # Sybil
    attack_panel._trigger_sybil()
    
    # Majority
    attack_panel._trigger_majority()
    
    # Partition
    attack_panel._trigger_partition()
    
    # Selfish Mining
    attack_panel.selfish_attacker.addItem("miner_0")
    attack_panel.selfish_attacker.setCurrentText("miner_0")
    attack_panel._trigger_selfish()
    
    # All should have valid format
    assert len(captured_signals) == 6
    
    for attack_type, params in captured_signals:
        assert isinstance(attack_type, str)
        assert isinstance(params, dict)


# ============ Error Handling Tests ============

def test_api_error_handling_simulation(attack_panel, mock_api_client):
    """Test handling API errors."""
    # Simulate API error
    mock_api_client.trigger_attack.return_value = {"error": "Connection failed"}
    
    attack_panel.ddos_target.addItem("node_0")
    attack_panel.ddos_target.setCurrentText("node_0")
    
    captured_signals = []
    attack_panel.attack_triggered.connect(
        lambda attack_type, params: captured_signals.append((attack_type, params))
    )
    
    attack_panel._trigger_ddos()
    
    attack_type, params = captured_signals[0]
    target = params.get("target")
    
    result = mock_api_client.trigger_attack(attack_type, target, params)
    
    # Should receive error
    assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
