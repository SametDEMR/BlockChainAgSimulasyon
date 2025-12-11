"""Manual test for Blockchain Explorer Page."""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from unittest.mock import Mock

from ui.pages.blockchain_page import BlockchainExplorerPage
from core.data_manager import DataManager


def test_blockchain_page():
    """Test blockchain page functionality."""
    print("=" * 60)
    print("Blockchain Explorer Page - Manual Test")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create mock API client
    mock_api = Mock()
    mock_api.is_connected.return_value = True
    
    # Create DataManager
    data_manager = DataManager(mock_api)
    
    # Create page
    print("\n1. Testing page initialization...")
    page = BlockchainExplorerPage(data_manager)
    print("   ✓ Page created successfully")
    
    # Check widgets exist
    print("\n2. Testing widget creation...")
    assert page.lbl_total_blocks is not None, "Total blocks label missing"
    assert page.lbl_forks is not None, "Forks label missing"
    assert page.lbl_pending_tx is not None, "Pending TX label missing"
    assert page.lbl_orphan_blocks is not None, "Orphan blocks label missing"
    print("   ✓ All stats labels created")
    
    assert page.btn_zoom_in is not None, "Zoom in button missing"
    assert page.btn_zoom_out is not None, "Zoom out button missing"
    assert page.btn_fit_view is not None, "Fit view button missing"
    print("   ✓ All control buttons created")
    
    assert page.chk_show_genesis is not None, "Genesis checkbox missing"
    assert page.chk_show_normal is not None, "Normal checkbox missing"
    assert page.chk_show_malicious is not None, "Malicious checkbox missing"
    assert page.chk_show_orphan is not None, "Orphan checkbox missing"
    print("   ✓ All filter checkboxes created")
    
    # Test initial values
    print("\n3. Testing initial values...")
    assert "Total Blocks: 0" in page.lbl_total_blocks.text()
    assert "Forks: 0" in page.lbl_forks.text()
    assert "Pending TX: 0" in page.lbl_pending_tx.text()
    assert "Orphan Blocks: 0" in page.lbl_orphan_blocks.text()
    print("   ✓ All initial values correct")
    
    # Test update_stats
    print("\n4. Testing update_stats method...")
    page.update_stats(total_blocks=100, forks=5, pending_tx=10, orphan_blocks=2)
    assert "100" in page.lbl_total_blocks.text()
    assert "5" in page.lbl_forks.text()
    assert "10" in page.lbl_pending_tx.text()
    assert "2" in page.lbl_orphan_blocks.text()
    print("   ✓ Stats updated correctly")
    
    # Test signal handling
    print("\n5. Testing signal handling...")
    blockchain_data = {
        'chain_length': 50,
        'pending_transactions': 15
    }
    data_manager.blockchain_updated.emit(blockchain_data)
    app.processEvents()
    assert "50" in page.lbl_total_blocks.text()
    assert "15" in page.lbl_pending_tx.text()
    print("   ✓ Blockchain update signal handled")
    
    fork_status = {
        'active_forks': 3,
        'orphan_blocks': 7
    }
    data_manager.fork_status_updated.emit(fork_status)
    app.processEvents()
    assert "3" in page.lbl_forks.text()
    assert "7" in page.lbl_orphan_blocks.text()
    print("   ✓ Fork status update signal handled")
    
    # Test signals emitted
    print("\n6. Testing signal emission...")
    signal_received = {'zoom_in': False, 'zoom_out': False, 'fit_view': False, 'filter': False}
    
    def on_zoom_in():
        signal_received['zoom_in'] = True
    
    def on_zoom_out():
        signal_received['zoom_out'] = True
    
    def on_fit_view():
        signal_received['fit_view'] = True
    
    def on_filter(filters):
        signal_received['filter'] = True
    
    page.zoom_in_requested.connect(on_zoom_in)
    page.zoom_out_requested.connect(on_zoom_out)
    page.fit_view_requested.connect(on_fit_view)
    page.filter_changed.connect(on_filter)
    
    page.btn_zoom_in.click()
    app.processEvents()
    assert signal_received['zoom_in'], "Zoom in signal not emitted"
    print("   ✓ Zoom in signal emitted")
    
    page.btn_zoom_out.click()
    app.processEvents()
    assert signal_received['zoom_out'], "Zoom out signal not emitted"
    print("   ✓ Zoom out signal emitted")
    
    page.btn_fit_view.click()
    app.processEvents()
    assert signal_received['fit_view'], "Fit view signal not emitted"
    print("   ✓ Fit view signal emitted")
    
    page.chk_show_genesis.setChecked(False)
    app.processEvents()
    assert signal_received['filter'], "Filter changed signal not emitted"
    print("   ✓ Filter changed signal emitted")
    
    # Test get_filter_state
    print("\n7. Testing get_filter_state method...")
    filters = page.get_filter_state()
    assert filters['show_genesis'] == False
    assert filters['show_normal'] == True
    print("   ✓ Filter state returned correctly")
    
    # Test clear_display
    print("\n8. Testing clear_display method...")
    page.clear_display()
    assert "Total Blocks: 0" in page.lbl_total_blocks.text()
    assert page.chk_show_genesis.isChecked()
    print("   ✓ Display cleared correctly")
    
    # Clean up
    page.deleteLater()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_blockchain_page()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
