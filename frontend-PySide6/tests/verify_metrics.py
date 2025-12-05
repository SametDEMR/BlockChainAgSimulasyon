"""Quick verification script for MetricsWidget."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from ui.widgets.metrics_widget import MetricsWidget
    
    print("✓ Imports successful")
    
    # Create QApplication
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    # Create widget without data manager
    widget = MetricsWidget(data_manager=None)
    print("✓ MetricsWidget created successfully")
    
    # Check sections exist
    assert widget.graph_section is not None, "graph_section missing"
    print("✓ graph_section exists")
    
    assert widget.cards_section is not None, "cards_section missing"
    print("✓ cards_section exists")
    
    assert widget.health_section is not None, "health_section missing"
    print("✓ health_section exists")
    
    assert widget.metrics_section is not None, "metrics_section missing"
    print("✓ metrics_section exists")
    
    # Check health bars
    assert widget.overall_health is not None, "overall_health missing"
    assert widget.validators_health is not None, "validators_health missing"
    assert widget.regular_health is not None, "regular_health missing"
    print("✓ Health bars exist")
    
    # Check metrics labels
    assert widget.blocks_per_min is not None, "blocks_per_min missing"
    assert widget.tx_per_sec is not None, "tx_per_sec missing"
    assert widget.avg_block_time is not None, "avg_block_time missing"
    print("✓ Metrics labels exist")
    
    # Test update_health
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_1', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_2', 'role': 'validator', 'status': 'under_attack'},
        {'id': 'node_3', 'role': 'validator', 'status': 'healthy'},
        {'id': 'node_4', 'role': 'regular', 'status': 'healthy'},
        {'id': 'node_5', 'role': 'regular', 'status': 'healthy'},
    ]
    
    widget.update_health(nodes)
    assert widget.overall_health.value() == 83, f"Expected 83, got {widget.overall_health.value()}"
    assert widget.validators_health.value() == 75, f"Expected 75, got {widget.validators_health.value()}"
    assert widget.regular_health.value() == 100, f"Expected 100, got {widget.regular_health.value()}"
    print("✓ update_health works correctly")
    
    # Test update_metrics
    metrics = {
        'blocks_per_minute': 12,
        'transactions_per_second': 5.2,
        'average_block_time': 5.1
    }
    
    widget.update_metrics(metrics)
    assert widget.blocks_per_min.text() == "12"
    assert widget.tx_per_sec.text() == "5.2"
    assert widget.avg_block_time.text() == "5.1s"
    print("✓ update_metrics works correctly")
    
    # Test clear_display
    widget.clear_display()
    assert widget.overall_health.value() == 0
    assert widget.blocks_per_min.text() == "0"
    print("✓ clear_display works correctly")
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED FOR MILESTONE 2.1")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
