"""Verification script for MetricsWidget Milestone 2.2."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from ui.widgets.metrics_widget import MetricsWidget
    import pyqtgraph as pg
    
    print("="*60)
    print("MILESTONE 2.2 VERIFICATION: PyQtGraph Integration")
    print("="*60)
    
    # Create QApplication
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    # Create widget
    widget = MetricsWidget(data_manager=None)
    print("\n✓ MetricsWidget created")
    
    # Check PyQtGraph components
    assert hasattr(widget, 'plot_widget'), "plot_widget missing"
    print("✓ plot_widget exists")
    
    assert hasattr(widget, 'response_time_data'), "response_time_data missing"
    assert isinstance(widget.response_time_data, dict), "response_time_data not dict"
    print("✓ response_time_data initialized")
    
    assert hasattr(widget, 'graph_curves'), "graph_curves missing"
    assert isinstance(widget.graph_curves, dict), "graph_curves not dict"
    print("✓ graph_curves initialized")
    
    assert widget.max_points == 50, f"max_points should be 50, got {widget.max_points}"
    print("✓ max_points = 50")
    
    assert len(widget.colors) == 10, f"colors should have 10 items, got {len(widget.colors)}"
    print("✓ 10 colors defined")
    
    # Test single node update
    print("\n--- Testing single node update ---")
    nodes = [{'id': 'node_0', 'response_time': 50}]
    widget.update_response_time_graph(nodes)
    
    assert 'node_0' in widget.response_time_data, "node_0 not in data"
    print("✓ node_0 data created")
    
    assert len(widget.response_time_data['node_0']) == 1, "Should have 1 data point"
    print("✓ Data point added")
    
    assert 'node_0' in widget.graph_curves, "node_0 curve not created"
    print("✓ Curve created")
    
    # Test multiple updates
    print("\n--- Testing multiple updates ---")
    for i in range(5):
        nodes = [{'id': 'node_0', 'response_time': 50 + i * 10}]
        widget.update_response_time_graph(nodes)
    
    assert len(widget.response_time_data['node_0']) == 6, f"Should have 6 points, got {len(widget.response_time_data['node_0'])}"
    print(f"✓ Accumulated 6 data points: {list(widget.response_time_data['node_0'])}")
    
    # Test multiple nodes
    print("\n--- Testing multiple nodes ---")
    widget.clear_display()  # Reset
    
    nodes = [
        {'id': 'node_0', 'response_time': 50},
        {'id': 'node_1', 'response_time': 45},
        {'id': 'node_2', 'response_time': 70},
    ]
    widget.update_response_time_graph(nodes)
    
    assert len(widget.response_time_data) == 3, f"Should have 3 nodes, got {len(widget.response_time_data)}"
    assert len(widget.graph_curves) == 3, f"Should have 3 curves, got {len(widget.graph_curves)}"
    print("✓ 3 nodes tracked")
    print(f"  Node IDs: {list(widget.response_time_data.keys())}")
    
    # Test max points limit
    print("\n--- Testing max points limit (50) ---")
    widget.clear_display()
    nodes = [{'id': 'node_test', 'response_time': 100}]
    
    for i in range(60):
        nodes[0]['response_time'] = 100 + i
        widget.update_response_time_graph(nodes)
    
    assert len(widget.response_time_data['node_test']) == 50, f"Should cap at 50, got {len(widget.response_time_data['node_test'])}"
    
    # Check oldest points dropped
    data = list(widget.response_time_data['node_test'])
    assert data[0] == 110, f"First point should be 110, got {data[0]}"  # 100 + 10 (first 10 dropped)
    assert data[-1] == 159, f"Last point should be 159, got {data[-1]}"  # 100 + 59
    print("✓ Max 50 points enforced")
    print(f"  Range: {data[0]} to {data[-1]}")
    
    # Test clear
    print("\n--- Testing clear ---")
    widget.clear_display()
    assert len(widget.response_time_data) == 0, "Data not cleared"
    assert len(widget.graph_curves) == 0, "Curves not cleared"
    print("✓ Clear works")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED FOR MILESTONE 2.2")
    print("="*60)
    print("\nFeatures:")
    print("  • PyQtGraph PlotWidget integrated")
    print("  • Real-time response time tracking")
    print("  • Multi-node support (10 colors)")
    print("  • Auto-scroll (last 50 points)")
    print("  • Legend and grid")
    print("  • Dark theme styling")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
