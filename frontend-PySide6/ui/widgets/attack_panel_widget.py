"""
Attack Control Panel Widget - QToolBox ile attack yönetimi
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBox, QGroupBox, 
    QLabel, QComboBox, QSlider, QPushButton,
    QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal

from .active_attack_item import ActiveAttackItem


class AttackPanelWidget(QWidget):
    """
    Sol dock'ta gösterilecek attack kontrol paneli.
    QToolBox kullanarak farklı attack tiplerini organize eder.
    """
    
    # Signals
    attack_triggered = Signal(str, dict)  # (attack_type, params)
    attack_stop_requested = Signal(str)  # attack_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_attacks = {}  # {attack_id: QListWidgetItem}
        self.init_ui()
        
    def init_ui(self):
        """UI bileşenlerini oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # QToolBox - Her attack tipi ayrı bir "sayfa"
        self.toolbox = QToolBox()
        
        # Attack sections (ACTIVE ATTACKS hariç)
        self._create_ddos_section()
        self._create_byzantine_section()
        self._create_sybil_section()
        self._create_majority_section()
        self._create_partition_section()
        self._create_selfish_section()
        
        layout.addWidget(self.toolbox)
        
        # ACTIVE ATTACKS - Ayrı grup, dashboard tarafından kullanılacak
        self._create_active_attacks_section()
        # Not added to layout - dashboard will handle it
        
    def _create_ddos_section(self):
        """DDoS Attack section"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Target dropdown
        self.ddos_target = QComboBox()
        self.ddos_target.addItem("Select Target...")
        layout.addRow("Target:", self.ddos_target)
        
        # Intensity slider
        self.ddos_intensity = QSlider(Qt.Horizontal)
        self.ddos_intensity.setMinimum(1)
        self.ddos_intensity.setMaximum(10)
        self.ddos_intensity.setValue(5)
        self.ddos_intensity.setTickPosition(QSlider.TicksBelow)
        self.ddos_intensity.setTickInterval(1)
        
        intensity_layout = QVBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity: Low ← → High"))
        intensity_layout.addWidget(self.ddos_intensity)
        
        # Intensity label
        self.ddos_intensity_label = QLabel("5")
        self.ddos_intensity.valueChanged.connect(
            lambda v: self.ddos_intensity_label.setText(str(v))
        )
        
        intensity_h = QHBoxLayout()
        intensity_h.addLayout(intensity_layout)
        intensity_h.addWidget(self.ddos_intensity_label)
        layout.addRow(intensity_h)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger DDoS Attack")
        trigger_btn.clicked.connect(self._trigger_ddos)
        layout.addRow(trigger_btn)
        
        self.toolbox.addItem(widget, "🌊 DDoS Attack")
        
    def _create_byzantine_section(self):
        """Byzantine Attack section"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Target dropdown (validators only)
        self.byzantine_target = QComboBox()
        self.byzantine_target.addItem("Select Validator...")
        layout.addRow("Target:", self.byzantine_target)
        
        # Info label
        info_label = QLabel("⚠️ Only validators can be Byzantine")
        info_label.setWordWrap(True)
        layout.addRow(info_label)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger Byzantine Attack")
        trigger_btn.clicked.connect(self._trigger_byzantine)
        layout.addRow(trigger_btn)
        
        self.toolbox.addItem(widget, "⚔️ Byzantine Attack")
        
    def _create_sybil_section(self):
        """Sybil Attack section"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Fake nodes slider
        self.sybil_count = QSlider(Qt.Horizontal)
        self.sybil_count.setMinimum(5)
        self.sybil_count.setMaximum(50)
        self.sybil_count.setValue(10)
        self.sybil_count.setTickPosition(QSlider.TicksBelow)
        self.sybil_count.setTickInterval(5)
        
        count_layout = QVBoxLayout()
        count_layout.addWidget(QLabel("Fake Nodes: 5 ← → 50"))
        count_layout.addWidget(self.sybil_count)
        
        # Count label
        self.sybil_count_label = QLabel("10")
        self.sybil_count.valueChanged.connect(
            lambda v: self.sybil_count_label.setText(str(v))
        )
        
        count_h = QHBoxLayout()
        count_h.addLayout(count_layout)
        count_h.addWidget(self.sybil_count_label)
        layout.addRow(count_h)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger Sybil Attack")
        trigger_btn.clicked.connect(self._trigger_sybil)
        layout.addRow(trigger_btn)
        
        self.toolbox.addItem(widget, "👥 Sybil Attack")
        
    def _create_majority_section(self):
        """Majority Attack section (51%)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Warning label
        warning = QLabel(
            "⚠️ WARNING\n\n"
            "This attack will compromise 51% of validators.\n"
            "Network consensus will be severely affected."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #FF9800; font-weight: bold;")
        layout.addWidget(warning)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger Majority Attack")
        trigger_btn.clicked.connect(self._trigger_majority)
        trigger_btn.setStyleSheet("background-color: #F44336;")
        layout.addWidget(trigger_btn)
        
        layout.addStretch()
        self.toolbox.addItem(widget, "⚡ Majority Attack (51%)")
        
    def _create_partition_section(self):
        """Network Partition section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info label
        info = QLabel(
            "This attack will split the network into 2 isolated groups.\n"
            "Nodes won't be able to communicate across partition."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger Network Partition")
        trigger_btn.clicked.connect(self._trigger_partition)
        layout.addWidget(trigger_btn)
        
        layout.addStretch()
        self.toolbox.addItem(widget, "🔌 Network Partition")
        
    def _create_selfish_section(self):
        """Selfish Mining section"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Attacker dropdown
        self.selfish_attacker = QComboBox()
        self.selfish_attacker.addItem("Select Miner...")
        layout.addRow("Attacker:", self.selfish_attacker)
        
        # Info label
        info = QLabel("Miner will hide mined blocks to gain advantage")
        info.setWordWrap(True)
        layout.addRow(info)
        
        # Trigger button
        trigger_btn = QPushButton("▶️ Trigger Selfish Mining")
        trigger_btn.clicked.connect(self._trigger_selfish)
        layout.addRow(trigger_btn)
        
        self.toolbox.addItem(widget, "💎 Selfish Mining")
        
    def _create_active_attacks_section(self):
        """Active Attacks section - Ayrı grup olarak en altta"""
        self.active_attacks_group = QGroupBox("⚠️ Active Attacks (0)")
        layout = QVBoxLayout(self.active_attacks_group)
        
        # List widget
        self.active_attacks_list = QListWidget()
        self.active_attacks_list.setSpacing(5)
        self.active_attacks_list.setMaximumHeight(200)
        layout.addWidget(self.active_attacks_list)
        
        # Initially collapsed look
        self.active_attacks_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
    def _trigger_ddos(self):
        """DDoS attack trigger"""
        target = self.ddos_target.currentText()
        intensity = self.ddos_intensity.value()
        
        if target == "Select Target...":
            return
            
        params = {
            "target": target,
            "intensity": intensity
        }
        self.attack_triggered.emit("ddos", params)
        
    def _trigger_byzantine(self):
        """Byzantine attack trigger"""
        target = self.byzantine_target.currentText()
        
        if target == "Select Validator...":
            return
            
        params = {"target": target}
        self.attack_triggered.emit("byzantine", params)
        
    def _trigger_sybil(self):
        """Sybil attack trigger"""
        count = self.sybil_count.value()
        params = {"fake_node_count": count}
        self.attack_triggered.emit("sybil", params)
        
    def _trigger_majority(self):
        """Majority attack trigger"""
        self.attack_triggered.emit("majority", {})
        
    def _trigger_partition(self):
        """Network partition trigger"""
        self.attack_triggered.emit("partition", {})
        
    def _trigger_selfish(self):
        """Selfish mining trigger"""
        attacker = self.selfish_attacker.currentText()
        
        if attacker == "Select Miner...":
            return
            
        params = {"attacker_id": attacker}
        self.attack_triggered.emit("selfish_mining", params)
        
    def update_node_list(self, nodes: list):
        """
        Node listesini güncelle - dropdown'lar için
        
        Args:
            nodes: Node dict listesi [{"id": "node_0", "is_validator": True, ...}, ...]
        """
        # DDoS - tüm node'lar
        current_ddos = self.ddos_target.currentText()
        self.ddos_target.clear()
        self.ddos_target.addItem("Select Target...")
        
        # Byzantine - sadece validators
        current_byz = self.byzantine_target.currentText()
        self.byzantine_target.clear()
        self.byzantine_target.addItem("Select Validator...")
        
        # Selfish - tüm node'lar
        current_selfish = self.selfish_attacker.currentText()
        self.selfish_attacker.clear()
        self.selfish_attacker.addItem("Select Miner...")
        
        for node in nodes:
            node_id = node.get("id", "")
            
            # DDoS ve Selfish için tüm node'lar
            self.ddos_target.addItem(node_id)
            self.selfish_attacker.addItem(node_id)
            
            # Byzantine için sadece validators
            if node.get("role") == "validator":
                self.byzantine_target.addItem(node_id)
        
        # Eski seçimi geri yükle (varsa)
        if current_ddos != "Select Target...":
            idx = self.ddos_target.findText(current_ddos)
            if idx >= 0:
                self.ddos_target.setCurrentIndex(idx)
                
        if current_byz != "Select Validator...":
            idx = self.byzantine_target.findText(current_byz)
            if idx >= 0:
                self.byzantine_target.setCurrentIndex(idx)
                
        if current_selfish != "Select Miner...":
            idx = self.selfish_attacker.findText(current_selfish)
            if idx >= 0:
                self.selfish_attacker.setCurrentIndex(idx)
                
    def add_active_attack(self, attack_data: dict):
        """
        Active attack ekle
        
        Args:
            attack_data: {
                "id": "attack_123",
                "type": "ddos",
                "target": "node_5",
                "progress": 0.0,
                "remaining_time": 30
            }
        """
        attack_id = attack_data.get("id", "")
        if not attack_id or attack_id in self.active_attacks:
            return
            
        # Custom widget oluştur
        attack_widget = ActiveAttackItem(attack_data)
        attack_widget.stop_requested.connect(self._on_attack_stop_requested)
        
        # List item
        item = QListWidgetItem(self.active_attacks_list)
        item.setSizeHint(attack_widget.sizeHint())
        self.active_attacks_list.addItem(item)
        self.active_attacks_list.setItemWidget(item, attack_widget)
        
        # Tracking
        self.active_attacks[attack_id] = item
        
        # Update section title
        self._update_active_attacks_title()
        
    def remove_active_attack(self, attack_id: str):
        """
        Active attack kaldır
        
        Args:
            attack_id: Attack ID
        """
        if attack_id not in self.active_attacks:
            return
            
        item = self.active_attacks[attack_id]
        row = self.active_attacks_list.row(item)
        self.active_attacks_list.takeItem(row)
        
        del self.active_attacks[attack_id]
        
        # Update section title
        self._update_active_attacks_title()
        
    def update_active_attack(self, attack_id: str, progress: float, remaining_time: int):
        """
        Active attack progress güncelle
        
        Args:
            attack_id: Attack ID
            progress: 0.0 - 1.0
            remaining_time: Kalan saniye
        """
        if attack_id not in self.active_attacks:
            return
            
        item = self.active_attacks[attack_id]
        widget = self.active_attacks_list.itemWidget(item)
        if isinstance(widget, ActiveAttackItem):
            widget.update_progress(progress, remaining_time)

            if progress >= 1.0 or remaining_time <= 0:
                self.clear_active_attacks()
            
    def get_active_attacks_count(self) -> int:
        """Active attack sayısı"""
        return len(self.active_attacks)
        
    def clear_active_attacks(self):
        """Tüm active attack'leri temizle"""
        self.active_attacks_list.clear()
        self.active_attacks.clear()
        self._update_active_attacks_title()
        
    def _update_active_attacks_title(self):
        """Active Attacks section title güncelle"""
        count = len(self.active_attacks)
        # QGroupBox title güncelle
        self.active_attacks_group.setTitle(f"⚠️ Active Attacks ({count})")
        
    def _on_attack_stop_requested(self, attack_id: str):
        """Stop butonu handler"""
        self.attack_stop_requested.emit(attack_id)
