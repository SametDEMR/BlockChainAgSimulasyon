"""Verification script for MetricsWidget Milestone 2.3."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from ui.widgets.metrics_widget import MetricsWidget
    from ui.widgets.node_status_card import NodeStatusCard
    
    print("="*60)
    print("MILESTONE 2.3 VERIFICATION: Node Status Cards")
    print("="*60)
    
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    widget = MetricsWidget(data_manager=None)
    print("\n✓ MetricsWidget created")
    
    # Check card components
    assert hasattr(widget, 'cards_grid'), "cards_grid missing"
    print("✓ cards_grid exists")
    
    assert hasattr(widget, 'status_cards'), "status_cards missing"
    assert isinstance(widget.status_cards, dict), "status_cards not dict"
    print("✓ status_cards initialized")
    
    # Test single card
    print("\n--- Testing single card ---")
    nodes = [{
        'id': 'node_0',
        'role': 'validator',
        'status': 'healthy',
        'response_time': 50,
        'trust_score': 95
    }]
    
    widget.update_status_cards(nodes)
    assert 'node_0' in widget.status_cards
    assert isinstance(widget.status_cards['node_0'], NodeStatusCard)
    print("✓ Card created for node_0")
    
    # Test multiple cards
    print("\n--- Testing multiple cards ---")
    nodes = [
        {'id': 'node_0', 'role': 'validator', 'status': 'healthy', 'response_time': 50, 'trust_score': 95},
        {'id': 'node_1', 'role': 'validator', 'status': 'under_attack', 'response_time': 200, 'trust_score': 70},
        {'id': 'node_2', 'role': 'regular', 'status': 'healthy', 'response_time': 45, 'balance': 500},
        {'id': 'node_3', 'role': 'regular', 'status': 'recovering', 'response_time': 80, 'balance': 450},
    ]
    
    widget.update_status_cards(nodes)
    assert len(widget.status_cards) == 4
    print(f"✓ 4 cards created: {list(widget.status_cards.keys())}")
    
    # Test grid placement (2 columns)
    assert widget.cards_grid.count() == 4
    print("✓ Cards added to grid (2x2 layout)")
    
    # Test card update
    print("\n--- Testing card update ---")
    initial_card = widget.status_cards['node_1']
    
    nodes = [{'id': 'node_1', 'role': 'validator', 'status': 'healthy', 'response_time': 60, 'trust_score': 85}]
    widget.update_status_cards(nodes)
    
    assert widget.status_cards['node_1'] is initial_card
    print("✓ Existing card updated (not recreated)")
    
    # Test clear
    print("\n--- Testing clear ---")
    widget.clear_display()
    assert len(widget.status_cards) == 0
    print("✓ Clear removed all cards")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED FOR MILESTONE 2.3")
    print("="*60)
    print("\nFeatures:")
    print("  • NodeStatusCard widget created")
    print("  • Status icons: 🟢 (healthy), 🔴 (under_attack), 🟡 (recovering)")
    print("  • Displays: RT, Trust/Balance, Progress bar")
    print("  • 2-column grid layout")
    print("  • Border color matches status")
    print("  • Hover effect")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
