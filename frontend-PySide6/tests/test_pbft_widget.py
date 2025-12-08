"""
Tests for PBFTWidget
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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
    widget = PBFTWidget()
    return widget


@pytest.fixture
def sample_pbft_status():
    """Sample PBFT status data"""
    return {
        'primary': 'node_0',
        'view': 2,
        'consensus_count': 15,
        'validator_count': 4,
        'total_messages': 234
    }


@pytest.fixture
def sample_messages():
    """Sample PBFT messages"""
    return [
        {
            'timestamp': '12:30:01',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'PRE_PREPARE',
            'view': 2
        },
        {
            'timestamp': '12:30:02',
            'sender': 'node_1',
            'receiver': 'ALL',
            'type': 'PREPARE',
            'view': 2
        },
        {
            'timestamp': '12:30:03',
            'sender': 'node_2',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 2
        },
        {
            'timestamp': '12:30:04',
            'sender': 'node_3',
            'receiver': 'node_0',
            'type': 'REPLY',
            'view': 2
        },
    ]


class TestPBFTWidget:
    """Test suite for PBFTWidget"""
    
    def test_creation(self, pbft_widget):
        """Test widget can be created"""
        assert pbft_widget is not None
        assert isinstance(pbft_widget, PBFTWidget)
    
    def test_initial_state(self, pbft_widget):
        """Test initial state"""
        assert "Primary: N/A" in pbft_widget.primary_label.text()
        assert "View: 0" in pbft_widget.view_label.text()
        assert "Consensus: 0" in pbft_widget.consensus_label.text()
        assert "Validators: 0" in pbft_widget.validators_label.text()
        assert "Messages: 0" in pbft_widget.messages_label.text()
        assert pbft_widget.message_table.rowCount() == 0
    
    def test_update_pbft_status(self, pbft_widget, sample_pbft_status):
        """Test update_pbft_status method"""
        pbft_widget.update_pbft_status(sample_pbft_status)
        
        assert "node_0" in pbft_widget.primary_label.text()
        assert "2" in pbft_widget.view_label.text()
        assert "15" in pbft_widget.consensus_label.text()
        assert "4" in pbft_widget.validators_label.text()
        assert "234" in pbft_widget.messages_label.text()
    
    def test_message_table_structure(self, pbft_widget):
        """Test message table has correct columns"""
        assert pbft_widget.message_table.columnCount() == 5
        
        headers = []
        for i in range(5):
            headers.append(pbft_widget.message_table.horizontalHeaderItem(i).text())
        
        assert headers == ["Time", "Sender", "Receiver", "Type", "View"]
    
    def test_add_message(self, pbft_widget, sample_messages):
        """Test add_message method"""
        message = sample_messages[0]
        pbft_widget.add_message(message)
        
        assert pbft_widget.message_table.rowCount() == 1
        assert pbft_widget.message_table.item(0, 0).text() == '12:30:01'
        assert pbft_widget.message_table.item(0, 1).text() == 'node_0'
        assert pbft_widget.message_table.item(0, 2).text() == 'ALL'
        assert pbft_widget.message_table.item(0, 3).text() == 'PRE_PREPARE'
        assert pbft_widget.message_table.item(0, 4).text() == '2'
    
    def test_add_multiple_messages(self, pbft_widget, sample_messages):
        """Test adding multiple messages"""
        for msg in sample_messages:
            pbft_widget.add_message(msg)
        
        assert pbft_widget.message_table.rowCount() == len(sample_messages)
    
    def test_messages_newest_first(self, pbft_widget, sample_messages):
        """Test messages are added at top (newest first)"""
        pbft_widget.add_message(sample_messages[0])
        pbft_widget.add_message(sample_messages[1])
        
        # Newest message (second added) should be at row 0
        assert pbft_widget.message_table.item(0, 0).text() == '12:30:02'
        # Older message should be at row 1
        assert pbft_widget.message_table.item(1, 0).text() == '12:30:01'
    
    def test_message_color_pre_prepare(self, pbft_widget):
        """Test PRE_PREPARE message color"""
        message = {
            'timestamp': '12:30:00',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'PRE_PREPARE',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#2196f3'
    
    def test_message_color_prepare(self, pbft_widget):
        """Test PREPARE message color"""
        message = {
            'timestamp': '12:30:00',
            'sender': 'node_1',
            'receiver': 'ALL',
            'type': 'PREPARE',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#ff9800'
    
    def test_message_color_commit(self, pbft_widget):
        """Test COMMIT message color"""
        message = {
            'timestamp': '12:30:00',
            'sender': 'node_2',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#4caf50'
    
    def test_message_color_reply(self, pbft_widget):
        """Test REPLY message color"""
        message = {
            'timestamp': '12:30:00',
            'sender': 'node_3',
            'receiver': 'node_0',
            'type': 'REPLY',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#9c27b0'
    
    def test_max_messages_limit(self, pbft_widget):
        """Test MAX_MESSAGES limit"""
        # Add more than MAX_MESSAGES
        for i in range(PBFTWidget.MAX_MESSAGES + 10):
            message = {
                'timestamp': f'12:30:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        # Should not exceed MAX_MESSAGES
        assert pbft_widget.message_table.rowCount() == PBFTWidget.MAX_MESSAGES
    
    def test_update_messages(self, pbft_widget, sample_messages):
        """Test update_messages method"""
        pbft_widget.update_messages(sample_messages)
        
        assert pbft_widget.message_table.rowCount() == len(sample_messages)
        # Newest message should be at top
        assert pbft_widget.message_table.item(0, 0).text() == '12:30:04'
    
    def test_update_messages_clears_old(self, pbft_widget, sample_messages):
        """Test update_messages clears old messages"""
        # Add initial messages
        pbft_widget.update_messages(sample_messages)
        initial_count = pbft_widget.message_table.rowCount()
        
        # Update with fewer messages
        pbft_widget.update_messages(sample_messages[:2])
        
        assert pbft_widget.message_table.rowCount() == 2
        assert pbft_widget.message_table.rowCount() < initial_count
    
    def test_clear_messages(self, pbft_widget, sample_messages):
        """Test clear_messages method"""
        pbft_widget.update_messages(sample_messages)
        assert pbft_widget.message_table.rowCount() > 0
        
        pbft_widget.clear_messages()
        assert pbft_widget.message_table.rowCount() == 0
    
    def test_clear_display(self, pbft_widget, sample_pbft_status, sample_messages):
        """Test clear_display method"""
        pbft_widget.update_pbft_status(sample_pbft_status)
        pbft_widget.update_messages(sample_messages)
        
        pbft_widget.clear_display()
        
        assert "Primary: N/A" in pbft_widget.primary_label.text()
        assert "View: 0" in pbft_widget.view_label.text()
        assert pbft_widget.message_table.rowCount() == 0
    
    def test_get_message_count(self, pbft_widget, sample_messages):
        """Test get_message_count method"""
        assert pbft_widget.get_message_count() == 0
        
        pbft_widget.update_messages(sample_messages)
        assert pbft_widget.get_message_count() == len(sample_messages)
    
    def test_table_read_only(self, pbft_widget, sample_messages):
        """Test table is read-only"""
        pbft_widget.update_messages(sample_messages)
        
        # EditTriggers should be NoEditTriggers (0)
        from PySide6.QtWidgets import QAbstractItemView
        assert pbft_widget.message_table.editTriggers() == QAbstractItemView.NoEditTriggers
    
    def test_message_with_missing_fields(self, pbft_widget):
        """Test adding message with missing fields"""
        incomplete_message = {
            'timestamp': '12:30:00',
            'type': 'PREPARE'
            # Missing sender, receiver, view
        }
        
        # Should not crash
        pbft_widget.add_message(incomplete_message)
        assert pbft_widget.message_table.rowCount() == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
