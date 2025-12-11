"""
Pytest Configuration and Shared Fixtures
"""
import pytest
import sys
import os
import asyncio

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.simulator import Simulator
from backend.network.message_broker import MessageBroker
from backend.network.node import Node
from backend.core.wallet import Wallet
from backend.core.blockchain import Blockchain
from backend.attacks.attack_engine import AttackEngine


# ============================================================================
# Fixtures - Temel Componentler
# ============================================================================

@pytest.fixture
def wallet():
    """Yeni bir wallet instance'ı döndürür"""
    return Wallet()


@pytest.fixture
def blockchain():
    """Yeni bir blockchain instance'ı döndürür"""
    return Blockchain()


@pytest.fixture
def message_broker():
    """Hızlı test için kısa delay'li MessageBroker"""
    return MessageBroker(min_delay=0.01, max_delay=0.05)


@pytest.fixture
def node():
    """Regular node instance'ı döndürür"""
    return Node(role="regular", total_validators=4, message_broker=None)


@pytest.fixture
def validator_node(message_broker):
    """Validator node instance'ı döndürür"""
    node = Node(role="validator", total_validators=4, message_broker=message_broker)
    message_broker.register_node(node.id)
    return node


@pytest.fixture
def attack_engine():
    """Attack engine instance'ı döndürür"""
    return AttackEngine()


@pytest.fixture
def simulator():
    """Simulator instance'ı döndürür"""
    sim = Simulator()
    yield sim
    # Cleanup
    if sim.is_running:
        sim.stop()


# ============================================================================
# Async Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="function")
def event_loop():
    """Her test için yeni event loop oluştur"""
    loop = asyncio.new_event_loop()
    yield loop
    # Cleanup
    try:
        # Cancel all pending tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        # Run until all tasks are cancelled
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
    except Exception:
        pass


# ============================================================================
# API Test Fixtures
# ============================================================================

@pytest.fixture
def api_base_url():
    """API base URL"""
    return "http://localhost:8000"


# ============================================================================
# Test Markers
# ============================================================================

def pytest_configure(config):
    """Özel marker'ları kaydet"""
    config.addinivalue_line("markers", "async_test: async test cases")
    config.addinivalue_line("markers", "api: API endpoint tests (requires server)")
    config.addinivalue_line("markers", "slow: slow running tests")
    config.addinivalue_line("markers", "integration: integration tests")
