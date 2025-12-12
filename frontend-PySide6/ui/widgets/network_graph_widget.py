"""
Network Graph Widget
Custom QGraphicsView for displaying network topology
"""
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, 
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter
from typing import Dict, List, Optional
import networkx as nx


class NodeItem(QGraphicsEllipseItem):
    """Custom node item for network graph"""
    
    def __init__(self, node_id: str, x: float, y: float, radius: float = 20):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node_id = node_id
        self.setPos(x, y)
        self.setFlags(
            QGraphicsEllipseItem.ItemIsSelectable |
            QGraphicsEllipseItem.ItemIsMovable |
            QGraphicsEllipseItem.ItemSendsGeometryChanges
        )
        
        # Enable hover events
        self.setAcceptHoverEvents(True)
        
        # Store original pen for restoring after hover
        self._original_pen = QPen(QColor("#3D3D3D"), 2)
        self._hover_pen = QPen(QColor("#FFFFFF"), 4)
        
        # Default style
        self.setPen(self._original_pen)
        self.setBrush(QBrush(QColor("#4CAF50")))
        
        # Label
        self.label = QGraphicsTextItem(node_id, self)
        self.label.setDefaultTextColor(QColor("#E0E0E0"))
        self.label.setPos(-radius, radius + 5)
        
        # Store node data
        self.node_data = {}
        
        # Track hover state
        self._is_hovered = False

    def update_style(self, node_data: Dict):
        """Update node style based on data"""
        self.node_data = node_data

        # Partition kontrolü KALDIRILDI
        if node_data.get('is_sybil', False):
            color = "#F44336"  # Red - Sybil
        elif node_data.get('is_byzantine', False):
            color = "#FF9800"  # Orange - Byzantine
        elif node_data.get('status') == 'under_attack':
            color = "#FFC107"  # Yellow - Under Attack
        elif node_data.get('role') == 'validator':
            color = "#2196F3"  # Blue - Validator
        else:
            color = "#4CAF50"  # Green - Regular

        self.setBrush(QBrush(QColor(color)))
        
        # Update original pen based on selection
        if self.isSelected():
            self._original_pen = QPen(QColor("#FFFFFF"), 3)
        else:
            self._original_pen = QPen(QColor("#3D3D3D"), 2)
        
        # Apply current pen (hover or original)
        if self._is_hovered:
            self.setPen(self._hover_pen)
        else:
            self.setPen(self._original_pen)
    
    def hoverEnterEvent(self, event):
        """Handle hover enter - increase border width and change color"""
        self._is_hovered = True
        self.setPen(self._hover_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave - restore original border"""
        self._is_hovered = False
        self.setPen(self._original_pen)
        super().hoverLeaveEvent(event)
    
    def itemChange(self, change, value):
        """Handle item changes - update edges when position changes"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Notify parent widget to update edges
            scene = self.scene()
            if scene and hasattr(scene, 'views'):
                views = scene.views()
                if views and hasattr(views[0], 'update_edges_for_node'):
                    views[0].update_edges_for_node(self.node_id)
        
        return super().itemChange(change, value)
    
    def get_tooltip_text(self) -> str:
        """Generate tooltip text from node data"""
        lines = [f"Node: {self.node_id}"]
        
        if self.node_data:
            role = self.node_data.get('role', 'N/A')
            status = self.node_data.get('status', 'N/A')
            lines.append(f"Role: {role}")
            lines.append(f"Status: {status}")
            
            if self.node_data.get('is_sybil'):
                lines.append("Type: Sybil Node")
            elif self.node_data.get('is_byzantine'):
                lines.append("Type: Byzantine Node")
            
            if 'response_time' in self.node_data:
                lines.append(f"Response: {self.node_data['response_time']}ms")
            
            if 'trust_score' in self.node_data:
                lines.append(f"Trust: {self.node_data['trust_score']}")
        
        return "\n".join(lines)


class NetworkGraphWidget(QGraphicsView):
    """Network graph visualization widget"""
    
    # Signals
    node_clicked = Signal(str)  # node_id
    node_double_clicked = Signal(str)  # node_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Setup view
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Data structures
        self.node_items: Dict[str, NodeItem] = {}
        self.edge_items: List[QGraphicsLineItem] = []
        self.node_positions: Dict[str, tuple] = {}
        self.edge_connections: Dict[QGraphicsLineItem, tuple] = {}  # edge -> (node1_id, node2_id)
        
        # Zoom settings
        self.zoom_factor = 1.15
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.current_zoom = 1.0
    
    def clear_graph(self):
        """Clear all items from scene"""
        self.scene.clear()
        self.node_items.clear()
        self.edge_items.clear()
        self.node_positions.clear()
        self.edge_connections.clear()
    
    def update_graph(self, nodes: List[Dict]):
        """
        Update graph with node data
        
        Args:
            nodes: List of node dictionaries
        """
        if not nodes or nodes is None:
            self.clear_graph()
            return
        
        # Calculate positions FIRST (before clearing)
        self._calculate_positions(nodes)
        
        # Clear scene and items (positions already saved)
        self.scene.clear()
        self.node_items.clear()
        self.edge_items.clear()
        self.edge_connections.clear()
        
        # Create edges
        self._create_edges(nodes)
        
        # Create nodes
        for node_data in nodes:
            # Skip nodes without id
            if 'id' not in node_data:
                continue
                
            node_id = node_data['id']
            if node_id in self.node_positions:
                x, y = self.node_positions[node_id]
                node_item = NodeItem(node_id, x, y)
                node_item.update_style(node_data)
                node_item.setToolTip(node_item.get_tooltip_text())
                self.scene.addItem(node_item)
                self.node_items[node_id] = node_item
    
    def _calculate_positions(self, nodes: List[Dict]):
        """Calculate node positions using NetworkX spring layout"""
        # Create graph
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            # Skip nodes without id
            if 'id' not in node:
                continue
            G.add_node(node['id'])
        
        # Add edges (simple: connect validators to each other, regulars to validators)
        validators = [n['id'] for n in nodes if 'id' in n and n.get('role') == 'validator']
        regulars = [n['id'] for n in nodes if 'id' in n and n.get('role') != 'validator']
        
        # Connect all validators
        for i, v1 in enumerate(validators):
            for v2 in validators[i+1:]:
                G.add_edge(v1, v2)
        
        # Connect regulars to random validator
        if validators:
            for regular in regulars:
                # Connect to first validator (can be randomized)
                G.add_edge(regular, validators[0])
        
        # Calculate positions
        pos = nx.spring_layout(G, k=2, iterations=50, scale=200)
        
        # Store positions
        self.node_positions = {node_id: (x * 2, y * 2) for node_id, (x, y) in pos.items()}
    
    def get_edges_for_node(self, node_id: str) -> List[QGraphicsLineItem]:
        """
        Get all edges connected to a specific node
        
        Args:
            node_id: Node ID to get edges for
            
        Returns:
            List of QGraphicsLineItem connected to this node
        """
        connected_edges = []
        for edge, (node1, node2) in self.edge_connections.items():
            if node1 == node_id or node2 == node_id:
                connected_edges.append(edge)
        return connected_edges
    
    def update_edges_for_node(self, node_id: str):
        """
        Update edge positions for a specific node
        
        Args:
            node_id: Node ID whose edges should be updated
        """
        if node_id not in self.node_items:
            return
        
        node_item = self.node_items[node_id]
        node_pos = node_item.pos()
        
        # Update all edges connected to this node
        for edge, (node1, node2) in self.edge_connections.items():
            if node1 == node_id or node2 == node_id:
                # Get positions of both endpoints
                if node1 == node_id:
                    x1, y1 = node_pos.x(), node_pos.y()
                    if node2 in self.node_items:
                        other_pos = self.node_items[node2].pos()
                        x2, y2 = other_pos.x(), other_pos.y()
                    else:
                        continue
                else:  # node2 == node_id
                    if node1 in self.node_items:
                        other_pos = self.node_items[node1].pos()
                        x1, y1 = other_pos.x(), other_pos.y()
                    else:
                        continue
                    x2, y2 = node_pos.x(), node_pos.y()
                
                # Update edge line
                edge.setLine(x1, y1, x2, y2)
    
    def highlight_node(self, node_id: str):
        """Highlight specific node"""
        if node_id in self.node_items:
            item = self.node_items[node_id]
            item.setSelected(True)
            self.centerOn(item)
    
    def get_selected_node(self) -> Optional[str]:
        """Get currently selected node ID"""
        selected = self.scene.selectedItems()
        if selected and isinstance(selected[0], NodeItem):
            return selected[0].node_id
        return None
    
    # Zoom controls
    def zoom_in(self):
        """Zoom in"""
        new_zoom = self.current_zoom * self.zoom_factor
        if new_zoom <= self.max_zoom:
            self.scale(self.zoom_factor, self.zoom_factor)
            self.current_zoom = new_zoom
    
    def zoom_out(self):
        """Zoom out"""
        new_zoom = self.current_zoom / self.zoom_factor
        if new_zoom >= self.min_zoom:
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            self.current_zoom = new_zoom
    
    def fit_view(self):
        """Fit all items in view"""
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.current_zoom = 1.0
    
    def reset_view(self):
        """Reset view to original state"""
        self.resetTransform()
        self.current_zoom = 1.0
        self.fit_view()
    
    # Mouse events
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def mousePressEvent(self, event):
        """Handle mouse press for node selection"""
        super().mousePressEvent(event)
        
        item = self.itemAt(event.pos())
        if isinstance(item, NodeItem):
            self.node_clicked.emit(item.node_id)
        elif isinstance(item, QGraphicsTextItem) and hasattr(item.parentItem(), 'node_id'):
            self.node_clicked.emit(item.parentItem().node_id)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click for node details"""
        item = self.itemAt(event.pos())
        if isinstance(item, NodeItem):
            self.node_double_clicked.emit(item.node_id)
        elif isinstance(item, QGraphicsTextItem) and hasattr(item.parentItem(), 'node_id'):
            self.node_double_clicked.emit(item.parentItem().node_id)


    def _create_edges(self, nodes: List[Dict]):
        """Create edge items between connected nodes"""
        # Partition bilgisi
        partition_groups = {}
        group_a_nodes = []
        group_b_nodes = []

        for node in nodes:
            if 'id' not in node:
                continue
            node_id = node['id']
            if node.get('partition_group') == 'A':
                partition_groups[node_id] = 'A'
                group_a_nodes.append(node_id)
            elif node.get('partition_group') == 'B':
                partition_groups[node_id] = 'B'
                group_b_nodes.append(node_id)

        # Partition aktifse, her grubu kendi içinde bağla
        if partition_groups:
            # Group A - mesh topology
            for i, n1 in enumerate(group_a_nodes):
                for n2 in group_a_nodes[i + 1:]:
                    if n1 in self.node_positions and n2 in self.node_positions:
                        x1, y1 = self.node_positions[n1]
                        x2, y2 = self.node_positions[n2]
                        line = QGraphicsLineItem(x1, y1, x2, y2)
                        line.setPen(QPen(QColor("#00BCD4"), 2))  # Cyan
                        line.setZValue(-1)
                        self.scene.addItem(line)
                        self.edge_items.append(line)
                        self.edge_connections[line] = (n1, n2)

            # Group B - mesh topology
            for i, n1 in enumerate(group_b_nodes):
                for n2 in group_b_nodes[i + 1:]:
                    if n1 in self.node_positions and n2 in self.node_positions:
                        x1, y1 = self.node_positions[n1]
                        x2, y2 = self.node_positions[n2]
                        line = QGraphicsLineItem(x1, y1, x2, y2)
                        line.setPen(QPen(QColor("#E91E63"), 2))  # Pink
                        line.setZValue(-1)
                        self.scene.addItem(line)
                        self.edge_items.append(line)
                        self.edge_connections[line] = (n1, n2)
        else:
            # Normal durum - eski kod
            validators = [n['id'] for n in nodes if 'id' in n and n.get('role') == 'validator']
            regulars = [n['id'] for n in nodes if 'id' in n and n.get('role') != 'validator']

            pen = QPen(QColor("#3D3D3D"), 1)

            # Connect validators
            for i, v1 in enumerate(validators):
                for v2 in validators[i + 1:]:
                    if v1 in self.node_positions and v2 in self.node_positions:
                        x1, y1 = self.node_positions[v1]
                        x2, y2 = self.node_positions[v2]
                        line = QGraphicsLineItem(x1, y1, x2, y2)
                        line.setPen(pen)
                        line.setZValue(-1)
                        self.scene.addItem(line)
                        self.edge_items.append(line)
                        self.edge_connections[line] = (v1, v2)

            # Connect regulars to first validator
            if validators:
                v = validators[0]
                for regular in regulars:
                    if v in self.node_positions and regular in self.node_positions:
                        x1, y1 = self.node_positions[v]
                        x2, y2 = self.node_positions[regular]
                        line = QGraphicsLineItem(x1, y1, x2, y2)
                        line.setPen(pen)
                        line.setZValue(-1)
                        self.scene.addItem(line)
                        self.edge_items.append(line)
                        self.edge_connections[line] = (v, regular)