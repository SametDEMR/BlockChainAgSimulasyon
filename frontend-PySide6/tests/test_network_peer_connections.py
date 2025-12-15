"""
Test: Network Map Peer-Based Connections
Tests peer-based edge creation in network graph
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.widgets.network_graph_widget import NetworkGraphWidget


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def graph_widget(qapp):
    """Create graph widget for testing"""
    widget = NetworkGraphWidget()
    return widget


def test_validators_mesh_connected(graph_widget):
    """Validators should be fully connected (mesh)"""
    nodes = [
        {'id': 'v1', 'role': 'validator', 'peers': ['v2', 'v3'], 'status': 'healthy'},
        {'id': 'v2', 'role': 'validator', 'peers': ['v1', 'v3'], 'status': 'healthy'},
        {'id': 'v3', 'role': 'validator', 'peers': ['v1', 'v2'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # 3 validators = 3 edges (mesh: v1-v2, v1-v3, v2-v3)
    assert len(graph_widget.edge_items) == 3
    
    # Verify connections exist
    edge_pairs = set()
    for edge, (n1, n2) in graph_widget.edge_connections.items():
        edge_pairs.add(tuple(sorted([n1, n2])))
    
    assert ('v1', 'v2') in edge_pairs
    assert ('v1', 'v3') in edge_pairs
    assert ('v2', 'v3') in edge_pairs


def test_regulars_connected_to_multiple_validators(graph_widget):
    """Regular nodes should connect to multiple validators"""
    nodes = [
        {'id': 'v1', 'role': 'validator', 'peers': ['v2', 'r1', 'r2'], 'status': 'healthy'},
        {'id': 'v2', 'role': 'validator', 'peers': ['v1', 'r1'], 'status': 'healthy'},
        {'id': 'r1', 'role': 'regular', 'peers': ['v1', 'v2'], 'status': 'healthy'},
        {'id': 'r2', 'role': 'regular', 'peers': ['v1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Edges: v1-v2 (validator mesh), v1-r1, v2-r1, v1-r2 = 4 edges
    assert len(graph_widget.edge_items) == 4
    
    # Verify r1 connects to both v1 and v2
    r1_connections = []
    for edge, (n1, n2) in graph_widget.edge_connections.items():
        if 'r1' in (n1, n2):
            other = n2 if n1 == 'r1' else n1
            r1_connections.append(other)
    
    assert 'v1' in r1_connections
    assert 'v2' in r1_connections


def test_no_duplicate_edges(graph_widget):
    """Edges should not be duplicated (bidirectional = single edge)"""
    nodes = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n2'], 'status': 'healthy'},
        {'id': 'n2', 'role': 'validator', 'peers': ['n1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Only 1 edge should exist (not 2)
    assert len(graph_widget.edge_items) == 1


def test_peers_field_missing(graph_widget):
    """Nodes without peers field should work gracefully"""
    nodes = [
        {'id': 'n1', 'role': 'validator', 'status': 'healthy'},  # No peers
        {'id': 'n2', 'role': 'regular', 'peers': [], 'status': 'healthy'},  # Empty peers
    ]
    
    graph_widget.update_graph(nodes)
    
    # No edges should be created
    assert len(graph_widget.edge_items) == 0


def test_peer_not_in_positions(graph_widget):
    """Edges to non-existent nodes should be skipped"""
    nodes = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n2', 'n_nonexistent'], 'status': 'healthy'},
        {'id': 'n2', 'role': 'regular', 'peers': ['n1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Only n1-n2 edge (n_nonexistent is skipped)
    assert len(graph_widget.edge_items) == 1
    
    edge_pairs = set()
    for edge, (n1, n2) in graph_widget.edge_connections.items():
        edge_pairs.add(tuple(sorted([n1, n2])))
    
    assert ('n1', 'n2') in edge_pairs


def test_complex_network_topology(graph_widget):
    """Test complex network with multiple validators and regulars"""
    nodes = [
        # 4 validators (mesh = 6 edges)
        {'id': 'v1', 'role': 'validator', 'peers': ['v2', 'v3', 'v4', 'r1', 'r2'], 'status': 'healthy'},
        {'id': 'v2', 'role': 'validator', 'peers': ['v1', 'v3', 'v4', 'r3'], 'status': 'healthy'},
        {'id': 'v3', 'role': 'validator', 'peers': ['v1', 'v2', 'v4', 'r1'], 'status': 'healthy'},
        {'id': 'v4', 'role': 'validator', 'peers': ['v1', 'v2', 'v3'], 'status': 'healthy'},
        # 3 regulars (various connections)
        {'id': 'r1', 'role': 'regular', 'peers': ['v1', 'v3'], 'status': 'healthy'},
        {'id': 'r2', 'role': 'regular', 'peers': ['v1'], 'status': 'healthy'},
        {'id': 'r3', 'role': 'regular', 'peers': ['v2'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Validators mesh: 6 edges (4 choose 2)
    # Regular connections: v1-r1, v3-r1, v1-r2, v2-r3 = 4 edges
    # Total: 10 edges
    assert len(graph_widget.edge_items) == 10


def test_partition_overrides_peers(graph_widget):
    """Partition groups should override peer-based edges"""
    nodes = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n2', 'n3'], 'partition_group': 'A', 'status': 'healthy'},
        {'id': 'n2', 'role': 'regular', 'peers': ['n1'], 'partition_group': 'A', 'status': 'healthy'},
        {'id': 'n3', 'role': 'regular', 'peers': ['n1'], 'partition_group': 'B', 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Partition active: Group A (n1-n2), Group B (only n3, no edges)
    assert len(graph_widget.edge_items) == 1
    
    # Verify edge is within group A
    for edge, (node1, node2) in graph_widget.edge_connections.items():
        assert 'n3' not in (node1, node2)  # n3 is isolated in Group B


def test_real_time_peer_updates(graph_widget):
    """Peers should update dynamically"""
    # Initial state
    nodes_v1 = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n2'], 'status': 'healthy'},
        {'id': 'n2', 'role': 'regular', 'peers': ['n1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes_v1)
    assert len(graph_widget.edge_items) == 1
    
    # New peer added (n1 now connects to n3)
    nodes_v2 = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n2', 'n3'], 'status': 'healthy'},
        {'id': 'n2', 'role': 'regular', 'peers': ['n1'], 'status': 'healthy'},
        {'id': 'n3', 'role': 'regular', 'peers': ['n1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes_v2)
    assert len(graph_widget.edge_items) == 2
    
    edge_pairs = set()
    for edge, (node1, node2) in graph_widget.edge_connections.items():
        edge_pairs.add(tuple(sorted([node1, node2])))
    
    assert ('n1', 'n2') in edge_pairs
    assert ('n1', 'n3') in edge_pairs


def test_no_self_connections(graph_widget):
    """Nodes should not connect to themselves"""
    nodes = [
        {'id': 'n1', 'role': 'validator', 'peers': ['n1', 'n2'], 'status': 'healthy'},  # Self-connection
        {'id': 'n2', 'role': 'regular', 'peers': ['n1'], 'status': 'healthy'},
    ]
    
    graph_widget.update_graph(nodes)
    
    # Only n1-n2 edge (self-connection ignored)
    assert len(graph_widget.edge_items) == 1
    
    for edge, (node1, node2) in graph_widget.edge_connections.items():
        assert node1 != node2  # No self-loops
