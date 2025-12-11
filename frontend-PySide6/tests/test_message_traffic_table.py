"""
Tests for Message Traffic Table (Milestone 8.3)
Tests the QTableWidget implementation in PBFTWidget
"""
import pytest
import sys
from PySide6.QtWidgets import QApplication, QTableWidget, QHeaderView
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
    return PBFTWidget()


class TestMessageTrafficTable:
    """Test suite for Message Traffic Table (8.3)"""
    
    def test_table_is_qtablewidget(self, pbft_widget):
        """Test message table is QTableWidget"""
        assert isinstance(pbft_widget.message_table, QTableWidget)
    
    def test_table_columns(self, pbft_widget):
        """Test table has 5 columns: Timestamp, Sender, Receiver, Type, View"""
        assert pbft_widget.message_table.columnCount() == 5
        
        headers = []
        for i in range(5):
            headers.append(pbft_widget.message_table.horizontalHeaderItem(i).text())
        
        assert headers == ["Time", "Sender", "Receiver", "Type", "View"]
    
    def test_alternate_row_colors(self, pbft_widget):
        """Test table has alternating row colors enabled"""
        assert pbft_widget.message_table.alternatingRowColors() is True
    
    def test_sorting_enabled(self, pbft_widget):
        """Test table sorting is enabled"""
        assert pbft_widget.message_table.isSortingEnabled() is False  # Should be disabled for performance
    
    def test_table_read_only(self, pbft_widget):
        """Test table is read-only (no edit triggers)"""
        from PySide6.QtWidgets import QAbstractItemView
        assert pbft_widget.message_table.editTriggers() == QAbstractItemView.NoEditTriggers
    
    def test_column_resize_modes(self, pbft_widget):
        """Test column resize modes are set correctly"""
        header = pbft_widget.message_table.horizontalHeader()
        
        # Time column - ResizeToContents
        assert header.sectionResizeMode(0) == QHeaderView.ResizeToContents
        
        # Sender column - ResizeToContents
        assert header.sectionResizeMode(1) == QHeaderView.ResizeToContents
        
        # Receiver column - ResizeToContents
        assert header.sectionResizeMode(2) == QHeaderView.ResizeToContents
        
        # Type column - Stretch
        assert header.sectionResizeMode(3) == QHeaderView.Stretch
        
        # View column - ResizeToContents
        assert header.sectionResizeMode(4) == QHeaderView.ResizeToContents
    
    def test_message_type_color_pre_prepare(self, pbft_widget):
        """Test PRE_PREPARE message color is blue (#2196F3)"""
        message = {
            'timestamp': '12:00:00',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'PRE_PREPARE',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#2196f3'
        assert type_item.foreground().color().name() == '#ffffff'
    
    def test_message_type_color_prepare(self, pbft_widget):
        """Test PREPARE message color is orange (#FF9800)"""
        message = {
            'timestamp': '12:00:00',
            'sender': 'node_1',
            'receiver': 'ALL',
            'type': 'PREPARE',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#ff9800'
        assert type_item.foreground().color().name() == '#ffffff'
    
    def test_message_type_color_commit(self, pbft_widget):
        """Test COMMIT message color is green (#4CAF50)"""
        message = {
            'timestamp': '12:00:00',
            'sender': 'node_2',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#4caf50'
        assert type_item.foreground().color().name() == '#ffffff'
    
    def test_message_type_color_reply(self, pbft_widget):
        """Test REPLY message color is purple (#9C27B0)"""
        message = {
            'timestamp': '12:00:00',
            'sender': 'node_3',
            'receiver': 'node_0',
            'type': 'REPLY',
            'view': 0
        }
        pbft_widget.add_message(message)
        
        type_item = pbft_widget.message_table.item(0, 3)
        assert type_item.background().color().name() == '#9c27b0'
        assert type_item.foreground().color().name() == '#ffffff'
    
    def test_auto_scroll_newest_first(self, pbft_widget):
        """Test messages are added at top (newest first)"""
        message1 = {
            'timestamp': '12:00:00',
            'sender': 'node_0',
            'receiver': 'ALL',
            'type': 'PREPARE',
            'view': 0
        }
        message2 = {
            'timestamp': '12:00:01',
            'sender': 'node_1',
            'receiver': 'ALL',
            'type': 'COMMIT',
            'view': 0
        }
        
        pbft_widget.add_message(message1)
        pbft_widget.add_message(message2)
        
        # Newest message should be at row 0
        assert pbft_widget.message_table.item(0, 0).text() == '12:00:01'
        # Older message should be at row 1
        assert pbft_widget.message_table.item(1, 0).text() == '12:00:00'
    
    def test_max_100_rows_limit(self, pbft_widget):
        """Test table enforces MAX 100 rows limit"""
        # Add more than 100 messages
        for i in range(110):
            message = {
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i % 4}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        # Should not exceed 100 rows
        assert pbft_widget.message_table.rowCount() == 100
    
    def test_performance_limit_constant(self, pbft_widget):
        """Test MAX_MESSAGES constant is set to 100"""
        assert PBFTWidget.MAX_MESSAGES == 100
    
    def test_message_data_in_cells(self, pbft_widget):
        """Test message data is correctly displayed in cells"""
        message = {
            'timestamp': '14:25:33',
            'sender': 'validator_2',
            'receiver': 'ALL_VALIDATORS',
            'type': 'PRE_PREPARE',
            'view': 5
        }
        pbft_widget.add_message(message)
        
        assert pbft_widget.message_table.item(0, 0).text() == '14:25:33'
        assert pbft_widget.message_table.item(0, 1).text() == 'validator_2'
        assert pbft_widget.message_table.item(0, 2).text() == 'ALL_VALIDATORS'
        assert pbft_widget.message_table.item(0, 3).text() == 'PRE_PREPARE'
        assert pbft_widget.message_table.item(0, 4).text() == '5'
    
    def test_selection_behavior(self, pbft_widget):
        """Test table selection behavior is by rows"""
        from PySide6.QtWidgets import QAbstractItemView
        assert pbft_widget.message_table.selectionBehavior() == QAbstractItemView.SelectRows
    
    def test_color_coding_all_types(self, pbft_widget):
        """Test all message types have correct color coding"""
        colors = {
            'PRE_PREPARE': '#2196f3',
            'PREPARE': '#ff9800',
            'COMMIT': '#4caf50',
            'REPLY': '#9c27b0'
        }
        
        for msg_type, expected_color in colors.items():
            pbft_widget.clear_messages()
            message = {
                'timestamp': '12:00:00',
                'sender': 'node_0',
                'receiver': 'ALL',
                'type': msg_type,
                'view': 0
            }
            pbft_widget.add_message(message)
            
            type_item = pbft_widget.message_table.item(0, 3)
            assert type_item.background().color().name() == expected_color
            assert type_item.text() == msg_type
    
    def test_update_messages_bulk(self, pbft_widget):
        """Test update_messages method adds multiple messages"""
        messages = [
            {'timestamp': '12:00:00', 'sender': 'node_0', 'receiver': 'ALL', 'type': 'PRE_PREPARE', 'view': 0},
            {'timestamp': '12:00:01', 'sender': 'node_1', 'receiver': 'ALL', 'type': 'PREPARE', 'view': 0},
            {'timestamp': '12:00:02', 'sender': 'node_2', 'receiver': 'ALL', 'type': 'COMMIT', 'view': 0},
        ]
        
        pbft_widget.update_messages(messages)
        
        assert pbft_widget.message_table.rowCount() == 3
        # Newest message should be at top
        assert pbft_widget.message_table.item(0, 0).text() == '12:00:02'
    
    def test_clear_messages(self, pbft_widget):
        """Test clear_messages removes all rows"""
        for i in range(10):
            message = {
                'timestamp': f'12:00:{i:02d}',
                'sender': f'node_{i}',
                'receiver': 'ALL',
                'type': 'PREPARE',
                'view': 0
            }
            pbft_widget.add_message(message)
        
        assert pbft_widget.message_table.rowCount() == 10
        
        pbft_widget.clear_messages()
        assert pbft_widget.message_table.rowCount() == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
