"""
Tests for PBFT Performance Optimization (Milestone 8.5)
Tests row limits, efficient updates, and memory cleanup
"""
import pytest
import sys
import time
from PySide6.QtWidgets import QApplication
from ui.widgets.pbft_widget import PBFTWidget


@pytest.fixture
def qapp():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def pbft_widget(qapp):
    """PBFTWidget fixture"""
    return PBFTWidget()


class TestPBFTPerformanceOptimization:
    """Test suite for PBFT Performance Optimization (8.5)"""
    
    def test_row_limit_enforcement(self, pbft_widget):
        """Test table enforces 100 row limit"""
        # Add 150 messages
        for i in range(150):
            message = {
                'timestamp': f'12:{i//60:02d}:{i%60:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        # Should cap at MAX_MESSAGES
        assert pbft_widget.message_table.rowCount() == PBFTWidget.MAX_MESSAGES
        assert pbft_widget.message_table.rowCount() == 100
    
    def test_oldest_message_removed(self, pbft_widget):
        """Test oldest message is removed when limit exceeded"""
        # Add 100 messages
        for i in range(100):
            message = {
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        # Oldest should be at bottom (row 99)
        assert pbft_widget.message_table.item(99, 0).text() == '12:00:00'
        
        # Add one more
        new_message = {
            'timestamp': '12:01:40',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        }
        pbft_widget.add_message(new_message)
        
        # Still 100 rows
        assert pbft_widget.message_table.rowCount() == 100
        # Newest at top
        assert pbft_widget.message_table.item(0, 0).text() == '12:01:40'
        # Old bottom removed, new bottom is second oldest
        assert pbft_widget.message_table.item(99, 0).text() == '12:00:01'
    
    def test_efficient_insertion_top(self, pbft_widget):
        """Test messages inserted at top efficiently"""
        first_message = {
            'timestamp': '12:00:00',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'PREPARE',
            'view': 0
        }
        pbft_widget.add_message(first_message)
        
        second_message = {
            'timestamp': '12:00:01',
            'sender': 'node_1',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        }
        pbft_widget.add_message(second_message)
        
        # Second message should be at row 0
        assert pbft_widget.message_table.item(0, 0).text() == '12:00:01'
        # First message pushed to row 1
        assert pbft_widget.message_table.item(1, 0).text() == '12:00:00'
    
    def test_memory_cleanup_clear(self, pbft_widget):
        """Test clear_messages properly cleans memory"""
        # Add 50 messages
        for i in range(50):
            message = {
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        assert pbft_widget.message_table.rowCount() == 50
        
        # Clear
        pbft_widget.clear_messages()
        
        # Should be empty
        assert pbft_widget.message_table.rowCount() == 0
    
    def test_memory_cleanup_clear_display(self, pbft_widget):
        """Test clear_display cleans all data"""
        # Add PBFT status
        pbft_widget.update_pbft_status({
            'primary': 'node_0',
            'view': 5,
            'consensus_count': 42,
            'validator_count': 4,
            'total_messages': 847
        })
        
        # Add messages
        for i in range(20):
            pbft_widget.add_message({
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            })
        
        assert pbft_widget.message_table.rowCount() == 20
        
        # Clear all
        pbft_widget.clear_display()
        
        # Messages cleared
        assert pbft_widget.message_table.rowCount() == 0
        # Status reset
        assert "Primary: N/A" in pbft_widget.primary_label.text()
    
    def test_bulk_update_performance(self, pbft_widget):
        """Test update_messages handles bulk efficiently"""
        # Create 100 messages
        messages = [
            {
                'timestamp': f'12:{i//60:02d}:{i%60:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        pbft_widget.update_messages(messages)
        elapsed = time.time() - start_time
        
        # Should complete quickly (< 1 second)
        assert elapsed < 1.0
        assert pbft_widget.message_table.rowCount() == 100
    
    def test_update_messages_clears_old(self, pbft_widget):
        """Test update_messages clears old data first"""
        # Add initial messages
        for i in range(30):
            pbft_widget.add_message({
                'timestamp': f'11:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            })
        
        assert pbft_widget.message_table.rowCount() == 30
        
        # Update with new messages
        new_messages = [
            {
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'COMMIT',
                'view': 0
            }
            for i in range(10)
        ]
        
        pbft_widget.update_messages(new_messages)
        
        # Old messages cleared, only new ones
        assert pbft_widget.message_table.rowCount() == 10
        assert pbft_widget.message_table.item(0, 0).text() == '12:00:09'
    
    def test_max_messages_constant(self, pbft_widget):
        """Test MAX_MESSAGES constant is 100"""
        assert PBFTWidget.MAX_MESSAGES == 100
    
    def test_no_memory_leak_repeated_updates(self, pbft_widget):
        """Test repeated updates don't leak memory"""
        # Simulate 1000 message additions
        for cycle in range(10):
            for i in range(100):
                pbft_widget.add_message({
                    'timestamp': f'{cycle:02d}:{i//60:02d}:{i%60:02d}',
                    'sender': f'node_{i % 4}',
                    'receiver': 'ALL',
                    'type': 'PREPARE',
                    'view': 0
                })
        
        # Should still be at max
        assert pbft_widget.message_table.rowCount() == 100
    
    def test_efficient_limit_check(self, pbft_widget):
        """Test limit check is efficient (not rebuilding entire table)"""
        # Fill to limit
        for i in range(100):
            pbft_widget.add_message({
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            })
        
        # Add more and time it
        start_time = time.time()
        for i in range(50):
            pbft_widget.add_message({
                'timestamp': f'12:01:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'COMMIT',
                'view': 0
            })
        elapsed = time.time() - start_time
        
        # Should still be fast (< 0.5 seconds)
        assert elapsed < 0.5
        assert pbft_widget.message_table.rowCount() == 100
    
    def test_row_removal_performance(self, pbft_widget):
        """Test row removal is using removeRow efficiently"""
        # Fill to 100
        for i in range(100):
            pbft_widget.add_message({
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            })
        
        # Adding one more should remove last row
        pbft_widget.add_message({
            'timestamp': '12:02:00',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        })
        
        # Verify still at 100
        assert pbft_widget.message_table.rowCount() == 100
        # Newest at top
        assert pbft_widget.message_table.item(0, 0).text() == '12:02:00'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
