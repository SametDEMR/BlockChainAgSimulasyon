# PySide6 UI Planlama ve Mimari Dokümanı

## 📋 PROJE ÖZETİ

**Amaç:** Interactive Blockchain Attack Simulator projesinin Streamlit frontend'ini PySide6 (Qt for Python) ile yeniden geliştirmek.

**Neden PySide6?**
- Desktop uygulaması olarak daha professional görünüm
- Daha iyi performans ve kaynak yönetimi
- Native OS entegrasyonu
- PyInstaller ile standalone executable
- Daha fazla UI customization imkanı
- Gerçek zamanlı veri güncellemelerinde daha stabil

---

## 🛠️ TEKNOLOJİ STACK

### Ana Framework
- **PySide6 (Qt 6.x)** - UI framework
- **Python 3.10+** - Backend dili

### Görselleştirme Kütüphaneleri
- **PyQtGraph** - Real-time grafik çizimleri (response time, metrics)
- **NetworkX** - Network topology hesaplamaları
- **Custom QGraphicsScene** - Network map ve blockchain görselleştirme

### Asenkron İşlemler
- **QThread + Signal/Slot** - Background tasks ve API polling
- **asyncio** (opsiyonel) - Async API çağrıları için QThread içinde

### API İletişimi
- **requests** veya **aiohttp** - Backend API communication
- FastAPI backend (mevcut) - değişiklik yok

### Styling
- **Qt Style Sheets (QSS)** - Custom styling
- **qdarkstyle** - Modern dark theme

### Deployment
- **PyInstaller** - Standalone executable (.exe)

---

## 🏗️ MİMARİ YAPISI

### Ana Pencere Yapısı

```
┌─────────────────────────────────────────────────────────────────┐
│ Menu Bar: File | Settings | View | Help                         │
├─────────────────────────────────────────────────────────────────┤
│ Tool Bar: [▶ Start] [⏸ Stop] [🔄 Reset] [⚙️ Settings]          │
├──────┬──────────────────────────────────────────────┬───────────┤
│      │                                              │           │
│ LEFT │          CENTRAL WIDGET                      │   RIGHT   │
│ DOCK │        (QStackedWidget)                      │   DOCK    │
│      │                                              │           │
│      │  ┌────────────────────────────────────┐     │           │
│ AT-  │  │ Dashboard Page                     │     │ METRICS   │
│ TACK │  │  - System Overview                 │     │ DASH-     │
│ CON- │  │  - Node Count                      │     │ BOARD     │
│ TROL │  │  - Chain Length                    │     │           │
│ PA-  │  │  - Network Health                  │     │ - Status  │
│ NEL  │  │                                    │     │   Cards   │
│      │  ├────────────────────────────────────┤     │ - Graphs  │
│      │  │ Network Map Page                   │     │ - Metrics │
│ Tool │  │  - Interactive Node Graph          │     │           │
│ Box  │  │  - Zoom/Pan Controls               │     │           │
│      │  │                                    │     │           │
│ - D  │  ├────────────────────────────────────┤     │           │
│ - B  │  │ Blockchain Explorer Page           │     │           │
│ - S  │  │  - Chain Visualization             │     │           │
│ - M  │  │  - Block Details                   │     │           │
│ - P  │  │  - Fork Display                    │     │           │
│ - SF │  │                                    │     │           │
│      │  ├────────────────────────────────────┤     │           │
│      │  │ Nodes Page                         │     │           │
│      │  │  - Node Tree (Validators/Regular)  │     │           │
│      │  │  - Node Details                    │     │           │
│      │  └────────────────────────────────────┘     │           │
│      │                                              │           │
├──────┴──────────────────────────────────────────────┴───────────┤
│ Bottom Dock: PBFT Status & Message Traffic                      │
│  - Current View, Primary Validator                              │
│  - Message Table (real-time updates)                            │
├─────────────────────────────────────────────────────────────────┤
│ Status Bar: 🟢 Connected | Last Update: 2s ago                  │
└─────────────────────────────────────────────────────────────────┘
```

### QDockWidget Sistemi

**Left Dock - Attack Control Panel (QDockWidget)**
- Başlangıçta sol tarafta
- Daraltılabilir/genişletilebilir
- Float yapılabilir
- QToolBox içeriği

**Right Dock - Metrics Dashboard (QDockWidget)**
- Başlangıçta sağ tarafta
- Real-time metrik göstergeleri
- Scroll edilebilir

**Bottom Dock - PBFT & Messages (QDockWidget)**
- Başlangıçta altta
- PBFT status + message table
- Küçültülüp gizlenebilir

**Avantajları:**
- Kullanıcı layout'u özelleştirebilir
- Dock'lar kapatılabilir, taşınabilir
- Workspace esnek

---

## 📦 BILEŞEN DETAYLARI

### 1. Ana Pencere (MainWindow)

**Dosya:** `frontend_qt/ui/main_window.py`

**Sınıf:** `MainWindow(QMainWindow)`

**Sorumluluklar:**
- Menu bar, toolbar, status bar setup
- Central widget (QStackedWidget) yönetimi
- Dock widget'ların oluşturulması
- Page switching
- Global shortcuts (F5 refresh, Ctrl+S settings, vb.)

**Menu Bar:**
```
File
├─ Settings
├─ Export Logs
├─ Exit

View
├─ Dashboard
├─ Network Map
├─ Blockchain
├─ Nodes
├─ Show/Hide Attack Panel
├─ Show/Hide Metrics
├─ Show/Hide PBFT

Help
├─ Documentation
└─ About
```

**Tool Bar:**
- Start Simulator (QPushButton + QIcon)
- Stop Simulator
- Reset Simulator
- Settings
- Separator
- Page switcher (QComboBox veya QPushButton grubu)

**Status Bar:**
- Connection indicator (QLabel + color dot)
- Last update time (QLabel)
- API endpoint (QLabel)

---

### 2. Pages (QStackedWidget İçeriği)

#### 2.1 Dashboard Page

**Dosya:** `frontend_qt/ui/pages/dashboard_page.py`

**Sınıf:** `DashboardPage(QWidget)`

**Layout:**
```
┌────────────────────────────────────┐
│  System Overview (QGroupBox)       │
│  ┌──────┬──────┬──────┬──────┐    │
│  │Nodes │Active│Chain │Health│    │
│  │  10  │  10  │  45  │ 98%  │    │
│  │ LCD  │ LCD  │ LCD  │ Bar  │    │
│  └──────┴──────┴──────┴──────┘    │
├────────────────────────────────────┤
│  PBFT Consensus (QGroupBox)        │
│  Primary: node_0  View: 0          │
│  Consensus: 15  Validators: 4      │
├────────────────────────────────────┤
│  Recent Activity (QListWidget)     │
│  • Block #45 mined by node_2       │
│  • PBFT consensus reached          │
│  • DDoS attack started on node_5   │
└────────────────────────────────────┘
```

**Widgets:**
- System metrics: QLCDNumber (büyük sayılar)
- Network health: QProgressBar (0-100%)
- PBFT info: QLabel'lar
- Activity log: QListWidget (son 20 event)

---

#### 2.2 Network Map Page

**Dosya:** `frontend_qt/ui/pages/network_page.py`

**Sınıf:** `NetworkMapPage(QWidget)`

**Layout:**
```
┌────────────────────────────────────┐
│ Controls (QHBoxLayout)              │
│ [Zoom In] [Zoom Out] [Fit] [Reset] │
├────────────────────────────────────┤
│                                    │
│   NetworkGraphWidget               │
│   (Custom QGraphicsView)           │
│                                    │
│   Validator nodes: 🔷              │
│   Regular nodes: 🟢                │
│   Sybil nodes: 🔴                  │
│   Byzantine nodes: 🟠              │
│                                    │
│   Interactive: drag, zoom, pan     │
│                                    │
├────────────────────────────────────┤
│ Legend (QGroupBox)                  │
│ 🔷 Validator  🟢 Regular           │
│ 🔴 Sybil      🟠 Byzantine         │
└────────────────────────────────────┘
```

**Custom Widget:** `NetworkGraphWidget(QGraphicsView)`
- QGraphicsScene tabanlı
- Node'lar: Custom QGraphicsEllipseItem
- Bağlantılar: QGraphicsLineItem
- Renk kodlama
- Hover tooltip (node detayları)
- Click event (node seçme)
- Mouse wheel zoom
- Pan (click & drag)

**Node Positioning:**
- NetworkX spring_layout kullan
- Node pozisyonlarını cache'le (performans)

---

#### 2.3 Blockchain Explorer Page

**Dosya:** `frontend_qt/ui/pages/blockchain_page.py`

**Sınıf:** `BlockchainExplorerPage(QWidget)`

**Layout:**
```
┌────────────────────────────────────┐
│ Stats (QHBoxLayout)                 │
│ Total Blocks: 45 | Forks: 1        │
│ Pending TXs: 3   | Orphans: 2      │
├────────────────────────────────────┤
│                                    │
│   BlockchainGraphWidget            │
│   (Custom QGraphicsView)           │
│                                    │
│   [Genesis]→[Blk1]→[Blk2]→[Blk3]  │
│      🔷      🟢     🟢     🔴      │
│                     ↓              │
│                  [Blk2b] (orphan)  │
│                     🌫️             │
│                                    │
│   Horizontal scroll                │
│   Zoom in/out                      │
│                                    │
└────────────────────────────────────┘
```

**Custom Widget:** `BlockchainGraphWidget(QGraphicsView)`
- Her blok: Custom QGraphicsRectItem
- Blok renkleri:
  - 🔷 Genesis: Mavi (#2196F3)
  - 🟢 Normal: Yeşil (#4CAF50)
  - 🔴 Malicious: Kırmızı (#F44336)
  - 🌫️ Orphan: Gri (#9E9E9E)
- Blok içeriği:
  - Index, Hash (ilk 8 karakter)
  - Miner ID, TX count
- Hover: Full hash + tüm detaylar (QToolTip)
- Double-click: Transaction dialog aç
- Fork gösterimi: Branch yapısı

---

#### 2.4 Nodes Page

**Dosya:** `frontend_qt/ui/pages/nodes_page.py`

**Sınıf:** `NodesPage(QWidget)`

**Layout:**
```
┌────────────────────────────────────┐
│ QTreeWidget                         │
│ ├─ 👑 Validators (4)               │
│ │  ├─ node_0 [Primary] 🟢 Trust:95│
│ │  ├─ node_1 🟢 Trust:88           │
│ │  ├─ node_2 🟡 Trust:75           │
│ │  └─ node_3 🟢 Trust:92           │
│ └─ Regular Nodes (6)                │
│    ├─ node_4 🟢 Balance:450        │
│    ├─ node_5 🔴 [Under Attack]     │
│    └─ ...                           │
│                                    │
│ Double-click için detay dialog     │
└────────────────────────────────────┘
```

**QTreeWidget Yapısı:**
- Top-level items: "Validators" ve "Regular Nodes"
- Child items: Her node bir satır
- Kolonlar: ID, Status Icon, Primary, Trust/Balance, Response Time
- Renk kodlama (status'e göre satır arka planı)
- Sorting enabled
- Double-click → `NodeDetailDialog` aç

**NodeDetailDialog:**
- Node tüm detayları (QFormLayout)
- Blockchain status
- PBFT info (validators için)
- Transaction history
- Close butonu

---

### 3. Dock Widgets

#### 3.1 Attack Control Panel (Left Dock)

**Dosya:** `frontend_qt/ui/widgets/attack_panel_widget.py`

**Sınıf:** `AttackPanelWidget(QWidget)`

**Layout: QToolBox**

```
┌─ DDoS Attack ────────────────┐
│ Target: [Dropdown: node_5 ▼] │
│ Intensity:                    │
│ Low [====|====] High          │
│ [▶️ Trigger Attack]           │
│                               │
├─ Byzantine Attack ────────────┤
│ Target: [Dropdown: node_1 ▼] │
│ (Only validators)             │
│ [▶️ Trigger Attack]           │
│                               │
├─ Sybil Attack ────────────────┤
│ Fake Nodes:                   │
│ 5 [====|====] 50              │
│ [▶️ Trigger Attack]           │
│                               │
├─ Majority Attack ─────────────┤
│ This will compromise 51% of   │
│ validators                    │
│ [▶️ Trigger Attack]           │
│                               │
├─ Network Partition ───────────┤
│ Split network into 2 groups   │
│ [▶️ Trigger Attack]           │
│                               │
├─ Selfish Mining ──────────────┤
│ Attacker: [Dropdown: node_2]  │
│ [▶️ Trigger Attack]           │
│                               │
└─ Active Attacks ──────────────┘
│ (QListWidget + Custom Items)  │
│ ┌───────────────────────────┐ │
│ │ ⚠️ DDoS on node_5        │ │
│ │ [████████░░] 80%         │ │
│ │ Remaining: 4s   [Stop]   │ │
│ └───────────────────────────┘ │
│ ┌───────────────────────────┐ │
│ │ ⚠️ Byzantine on node_1   │ │
│ │ [█████░░░░░] 50%         │ │
│ │ Remaining: 15s  [Stop]   │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

**QToolBox Items:**
1. DDoS Attack
   - Target: QComboBox (tüm node'lar)
   - Intensity: QSlider (1-10)
   - Trigger: QPushButton
2. Byzantine Attack
   - Target: QComboBox (sadece validators)
   - Trigger: QPushButton
3. Sybil Attack
   - Fake Nodes: QSlider (5-50)
   - Trigger: QPushButton
4. Majority Attack
   - Warning: QLabel
   - Trigger: QPushButton
5. Network Partition
   - Info: QLabel
   - Trigger: QPushButton
6. Selfish Mining
   - Attacker: QComboBox (tüm node'lar)
   - Trigger: QPushButton

**Active Attacks (Son item):**
- QListWidget
- Her attack için custom QWidget item:
  - Attack type + icon (QLabel)
  - Target info (QLabel)
  - Progress bar (QProgressBar)
  - Remaining time (QLabel)
  - Stop button (QPushButton)

---

#### 3.2 Metrics Dashboard (Right Dock)

**Dosya:** `frontend_qt/ui/widgets/metrics_widget.py`

**Sınıf:** `MetricsWidget(QWidget)`

**Layout: QScrollArea + QVBoxLayout**

```
┌─────────────────────────────┐
│ Response Time (Real-time)   │
│ ┌─────────────────────────┐ │
│ │ PyQtGraph PlotWidget    │ │
│ │ Multi-line (per node)   │ │
│ │ Last 50 data points     │ │
│ └─────────────────────────┘ │
├─────────────────────────────┤
│ Node Status Cards           │
│ ┌───────────┬───────────┐  │
│ │🟢 node_0  │🟢 node_1  │  │
│ │RT: 50ms   │RT: 48ms   │  │
│ │Trust: 95  │Trust: 88  │  │
│ │████████░░ │████████░  │  │
│ └───────────┴───────────┘  │
│ ┌───────────┬───────────┐  │
│ │🟡 node_2  │🔴 node_5  │  │
│ │RT: 120ms  │RT: 500ms  │  │
│ │Trust: 75  │Under Atk  │  │
│ │███████░░░ │████░░░░░░ │  │
│ └───────────┴───────────┘  │
├─────────────────────────────┤
│ Network Health              │
│ Overall: [████████░] 88%    │
│ Validators: [█████████] 95% │
│ Regular: [███████░░] 82%    │
├─────────────────────────────┤
│ System Metrics              │
│ Blocks/min: 12              │
│ TX/sec: 5.2                 │
│ Avg Block Time: 5.1s        │
└─────────────────────────────┘
```

**Widgets:**
- Real-time Graph: PyQtGraph PlotWidget
  - 10 curve (her node için biri)
  - Auto-scroll
  - Legend
- Status Cards: Custom QFrame widgets (2x kolonlu grid)
  - Status emoji (QLabel)
  - Node ID (QLabel)
  - Response time (QLabel)
  - Trust score bar (QProgressBar)
- Health Bars: QProgressBar widgets
- System Metrics: QLabel'lar (QFormLayout)

---

#### 3.3 PBFT Status & Messages (Bottom Dock)

**Dosya:** `frontend_qt/ui/widgets/pbft_widget.py`

**Sınıf:** `PBFTWidget(QWidget)`

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ PBFT Status (QGroupBox)                         │
│ Primary: node_0 | View: 0 | Consensus: 15      │
│ Validators: 4   | Messages: 234                 │
├─────────────────────────────────────────────────┤
│ Message Traffic (QTableWidget)                  │
│ ┌──────┬────────┬──────────┬─────────┬──────┐ │
│ │ Time │ Sender │ Receiver │ Type    │ View │ │
│ ├──────┼────────┼──────────┼─────────┼──────┤ │
│ │12:30 │ node_0 │ ALL      │ PREP    │ 0    │ │
│ │12:30 │ node_1 │ ALL      │ PREPARE │ 0    │ │
│ │12:30 │ node_2 │ ALL      │ PREPARE │ 0    │ │
│ │12:30 │ node_3 │ ALL      │ COMMIT  │ 0    │ │
│ └──────┴────────┴──────────┴─────────┴──────┘ │
│ (Max 100 rows, auto-scroll to top)             │
└─────────────────────────────────────────────────┘
```

**PBFT Status Section:**
- QLabels (horizontal layout)
- Update every 2 seconds

**Message Table:**
- QTableWidget
- Columns: Timestamp, Sender, Receiver, Type, View
- Renk kodlu message types:
  - PRE_PREPARE: #2196F3 (mavi)
  - PREPARE: #FF9800 (turuncu)
  - COMMIT: #4CAF50 (yeşil)
  - REPLY: #9C27B0 (mor)
- Auto-scroll to newest (top)
- Max 100 rows (performance)

---

### 4. Custom Widgets

#### 4.1 NetworkGraphWidget

**Dosya:** `frontend_qt/ui/widgets/network_graph_widget.py`

**Sınıf:** `NetworkGraphWidget(QGraphicsView)`

**İşlevsellik:**
- QGraphicsScene içinde custom items
- Node çizimi: Custom `NodeItem(QGraphicsEllipseItem)`
  - Renk: role ve status'e göre
  - Label: node ID (QGraphicsTextItem)
  - Shape: durum göstergesi (circle, triangle)
- Edge çizimi: `QGraphicsLineItem`
- Interaktivity:
  - Hover: Node detay tooltip
  - Click: Node seç (highlight)
  - Drag: Node taşı (sadece görsel, pozisyon değişmez)
  - Mouse wheel: Zoom in/out
  - Click & drag (empty space): Pan
- Layout algoritması: NetworkX spring_layout
  - Cache positions (her update'te yeniden hesaplama)

**Signals:**
- `node_clicked(node_id: str)` - Node seçildiğinde
- `node_double_clicked(node_id: str)` - Node detail için

---

#### 4.2 BlockchainGraphWidget

**Dosya:** `frontend_qt/ui/widgets/blockchain_graph_widget.py`

**Sınıf:** `BlockchainGraphWidget(QGraphicsView)`

**İşlevsellik:**
- QGraphicsScene içinde blok zincirleri
- Blok çizimi: Custom `BlockItem(QGraphicsRectItem)`
  - Rectangle (100x80 px)
  - Renk: blok durumuna göre
  - İçerik:
    - Index (büyük font)
    - Hash (ilk 8 karakter)
    - Miner ID
    - TX count
- Bağlantılar: QGraphicsLineItem (prev_hash referansı)
- Fork gösterimi: Branch yapısı (Y-axis offset)
- Horizontal scroll (blockchain büyüdükçe)
- Zoom: Mouse wheel
- Hover: Full block details (QToolTip)
- Double-click: Transaction detail dialog

**Block Positioning:**
- X-axis: Block index (100px aralık)
- Y-axis: Main chain=0, fork=+100 px

**Signals:**
- `block_clicked(block_index: int)` - Blok seçildiğinde
- `block_double_clicked(block_index: int)` - Transaction detail için

---

#### 4.3 NodeStatusCardWidget

**Dosya:** `frontend_qt/ui/widgets/node_status_card.py`

**Sınıf:** `NodeStatusCardWidget(QFrame)`

**Görünüm:**
```
┌─────────────────┐
│ 🟢 node_0      │ ← Status icon + ID
│ RT: 50ms       │ ← Response time
│ Trust: █████░  │ ← Trust score bar
│      95        │ ← Numeric value
└─────────────────┘
```

**Widgets:**
- QFrame (border + background)
- QVBoxLayout
- Status icon: QLabel (emoji: 🟢🟡🔴)
- Node ID: QLabel
- Response time: QLabel
- Trust score: QProgressBar + QLabel

**Styling:**
- QSS ile custom styling
- Hover effect (border highlight)
- Status'e göre border color

---

## 🔄 VERI AKIŞI ve API ENTEGRASYONU

### API Client

**Dosya:** `frontend_qt/core/api_client.py`

**Sınıf:** `APIClient`

**Metodlar:**
```python
class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    # Simulator Control
    def start_simulator(self) -> dict
    def stop_simulator(self) -> dict
    def reset_simulator(self) -> dict
    
    # Data Fetching
    def get_status(self) -> dict
    def get_nodes(self) -> list
    def get_node_detail(self, node_id: str) -> dict
    def get_blockchain(self) -> dict
    def get_fork_status(self) -> dict
    def get_pbft_status(self) -> dict
    def get_network_messages(self) -> dict
    def get_metrics(self) -> dict
    
    # Attack Triggers
    def trigger_attack(self, attack_type: str, params: dict) -> dict
    def stop_attack(self, attack_id: str) -> dict
    def get_attack_status(self) -> dict
    
    # Health Check
    def is_connected(self) -> bool
```

**Error Handling:**
- Try-except ile connection errors
- Timeout ayarı (5 saniye)
- Retry mekanizması (3 deneme)

---

### Data Manager

**Dosya:** `frontend_qt/core/data_manager.py`

**Sınıf:** `DataManager(QObject)`

**Sorumluluklar:**
- API'den gelen verileri parse etme
- Cache yönetimi (gereksiz API çağrılarını önleme)
- Data transformation (API response → UI models)
- Signal emitting (veri değiştiğinde)

**Signals:**
```python
class DataManager(QObject):
    # Data update signals
    status_updated = Signal(dict)
    nodes_updated = Signal(list)
    blockchain_updated = Signal(dict)
    pbft_updated = Signal(dict)
    metrics_updated = Signal(dict)
    attacks_updated = Signal(dict)
    messages_updated = Signal(list)
    
    # Error signals
    connection_error = Signal(str)
    api_error = Signal(str)
```

**Metodlar:**
```python
def update_all_data(self):
    """Tüm verileri API'den çek ve signaller emit et"""
    
def get_cached_nodes(self) -> list:
    """Cached node listesi döndür"""
    
def get_node_by_id(self, node_id: str) -> dict:
    """Spesifik node bilgisi"""
```

---

### Real-time Updater

**Dosya:** `frontend_qt/core/updater.py`

**Sınıf:** `DataUpdater(QThread)`

**İşleyiş:**
```python
class DataUpdater(QThread):
    def __init__(self, api_client: APIClient, data_manager: DataManager):
        super().__init__()
        self.api_client = api_client
        self.data_manager = data_manager
        self.running = False
        self.interval = 2000  # 2 saniye
    
    def run(self):
        """Background thread - sürekli API poll"""
        while self.running:
            try:
                # API çağrıları
                status = self.api_client.get_status()
                nodes = self.api_client.get_nodes()
                blockchain = self.api_client.get_blockchain()
                pbft = self.api_client.get_pbft_status()
                metrics = self.api_client.get_metrics()
                attacks = self.api_client.get_attack_status()
                messages = self.api_client.get_network_messages()
                
                # DataManager'a gönder (signaller emit edilir)
                self.data_manager.status_updated.emit(status)
                self.data_manager.nodes_updated.emit(nodes)
                self.data_manager.blockchain_updated.emit(blockchain)
                self.data_manager.pbft_updated.emit(pbft)
                self.data_manager.metrics_updated.emit(metrics)
                self.data_manager.attacks_updated.emit(attacks)
                self.data_manager.messages_updated.emit(messages)
                
            except Exception as e:
                self.data_manager.connection_error.emit(str(e))
            
            # Sleep
            self.msleep(self.interval)
    
    def start_updating(self):
        self.running = True
        self.start()
    
    def stop_updating(self):
        self.running = False
        self.wait()
```

**Önemli:**
- QThread kullanımı (UI thread'i bloklamaz)
- Signal/Slot ile UI güncelleme
- Exception handling
- Stop mekanizması

---

### UI Update Mekanizması

**Flow:**
```
[Backend API]
     ↓
[APIClient] (request)
     ↓
[DataUpdater Thread] (poll every 2s)
     ↓
[DataManager] (parse & emit signals)
     ↓
[UI Widgets] (slot functions, update display)
```

**Örnek Bağlantı:**
```python
# main_window.py içinde
def setup_connections(self):
    # DataManager signals → UI update slots
    self.data_manager.nodes_updated.connect(self.on_nodes_updated)
    self.data_manager.blockchain_updated.connect(self.on_blockchain_updated)
    self.data_manager.metrics_updated.connect(self.on_metrics_updated)
    # ...

@Slot(list)
def on_nodes_updated(self, nodes: list):
    """Node listesi güncellendiğinde"""
    self.nodes_page.update_node_tree(nodes)
    self.network_page.update_graph(nodes)
    self.attack_panel.update_target_dropdowns(nodes)
```

---

## 🎨 STYLING & THEME

### Qt Style Sheets (QSS)

**Dosya:** `frontend_qt/resources/styles/main.qss`

**Dark Theme Özellikleri:**
- Background: #1E1E1E (koyu gri)
- Foreground: #E0E0E0 (açık gri)
- Accent: #2196F3 (mavi)
- Success: #4CAF50 (yeşil)
- Warning: #FF9800 (turuncu)
- Error: #F44336 (kırmızı)

**QSS Örneği:**
```css
/* Main Window */
QMainWindow {
    background-color: #1E1E1E;
    color: #E0E0E0;
}

/* Dock Widgets */
QDockWidget {
    titlebar-close-icon: url(:/icons/close.png);
    titlebar-normal-icon: url(:/icons/float.png);
}

QDockWidget::title {
    background-color: #2D2D2D;
    padding: 5px;
}

/* Tool Box */
QToolBox::tab {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 3px;
    color: #E0E0E0;
    padding: 5px;
}

QToolBox::tab:selected {
    background-color: #2196F3;
    color: white;
}

/* Push Buttons */
QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #4D4D4D;
    color: #8D8D8D;
}

/* Table Widget */
QTableWidget {
    background-color: #2D2D2D;
    alternate-background-color: #252525;
    gridline-color: #3D3D3D;
    color: #E0E0E0;
    selection-background-color: #2196F3;
}

QHeaderView::section {
    background-color: #3D3D3D;
    color: #E0E0E0;
    padding: 5px;
    border: none;
    font-weight: bold;
}

/* Tree Widget */
QTreeWidget {
    background-color: #2D2D2D;
    alternate-background-color: #252525;
    color: #E0E0E0;
    selection-background-color: #2196F3;
}

QTreeWidget::item:selected {
    background-color: #2196F3;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    background-color: #2D2D2D;
    text-align: center;
    color: #E0E0E0;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 3px;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #3D3D3D;
    height: 6px;
    background: #2D2D2D;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #2196F3;
    border: 1px solid #1976D2;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

/* Status Cards */
.StatusCard {
    border: 2px solid #3D3D3D;
    border-radius: 8px;
    background-color: #2D2D2D;
    padding: 10px;
}

.StatusCard:hover {
    border-color: #2196F3;
}

.StatusCard[status="healthy"] {
    border-left: 4px solid #4CAF50;
}

.StatusCard[status="warning"] {
    border-left: 4px solid #FF9800;
}

.StatusCard[status="danger"] {
    border-left: 4px solid #F44336;
}
```

### qdarkstyle Entegrasyonu

**Alternatif:** Hazır dark theme kullanmak

```python
# main.py
import qdarkstyle
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
```

**Avantaj:** Hazır, tutarlı tema
**Dezavantaj:** Customization sınırlı

**Öneri:** Kendi QSS'imizi yazalım (daha fazla kontrol)

---

## 📂 KLASÖR YAPISI

```
BlockChainAgSimulasyon/
├── backend/                        # Backend (mevcut, değişmez)
│   ├── main.py
│   ├── simulator.py
│   ├── core/
│   ├── network/
│   └── attacks/
│
├── frontend_qt/                    # YENİ - PySide6 frontend
│   ├── main.py                     # Ana giriş noktası
│   │
│   ├── ui/                         # UI bileşenleri
│   │   ├── __init__.py
│   │   ├── main_window.py          # Ana pencere
│   │   │
│   │   ├── pages/                  # Sayfalar (QStackedWidget)
│   │   │   ├── __init__.py
│   │   │   ├── dashboard_page.py
│   │   │   ├── network_page.py
│   │   │   ├── blockchain_page.py
│   │   │   └── nodes_page.py
│   │   │
│   │   ├── widgets/                # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── attack_panel_widget.py
│   │   │   ├── metrics_widget.py
│   │   │   ├── pbft_widget.py
│   │   │   ├── network_graph_widget.py
│   │   │   ├── blockchain_graph_widget.py
│   │   │   └── node_status_card.py
│   │   │
│   │   └── dialogs/                # Dialog pencereleri
│   │       ├── __init__.py
│   │       ├── settings_dialog.py
│   │       ├── node_detail_dialog.py
│   │       ├── block_detail_dialog.py
│   │       └── about_dialog.py
│   │
│   ├── core/                       # Core logic
│   │   ├── __init__.py
│   │   ├── api_client.py           # Backend API client
│   │   ├── data_manager.py         # Veri yönetimi
│   │   ├── updater.py              # Real-time updater thread
│   │   └── models.py               # Data models
│   │
│   ├── resources/                  # Kaynaklar
│   │   ├── styles/
│   │   │   └── main.qss            # Qt Style Sheet
│   │   ├── icons/                  # SVG/PNG iconlar
│   │   │   ├── play.svg
│   │   │   ├── stop.svg
│   │   │   ├── reset.svg
│   │   │   └── settings.svg
│   │   └── fonts/                  # Custom fontlar (opsiyonel)
│   │
│   └── utils/                      # Utility fonksiyonlar
│       ├── __init__.py
│       ├── helpers.py              # Helper functions
│       └── constants.py            # Sabitler
│
├── config.py                       # Mevcut config (backend için)
├── requirements.txt                # Python dependencies
└── Doküman/
    ├── Projenin Ne Olduğu
    ├── Projenin Nasıl Olacağı
    ├── Yol Haritası.md
    ├── Tamamlanan Özellikler.md
    └── PySide6 UI Planlama.md      # Bu doküman
```

---

## 🔧 DEPLOYMENT

### PyInstaller Yapılandırması

**Dosya:** `frontend_qt/build.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/styles', 'resources/styles'),
        ('resources/icons', 'resources/icons'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pyqtgraph',
        'networkx',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BlockchainSimulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, console gizli
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico'  # Windows icon
)
```

### Build Komutu

```bash
# Spec dosyası ile build
pyinstaller frontend_qt/build.spec

# Çıktı
dist/BlockchainSimulator.exe
```

### Gereksinimler

**Dosya:** `requirements_qt.txt`

```
PySide6>=6.5.0
pyqtgraph>=0.13.0
networkx>=3.0
requests>=2.31.0
qdarkstyle>=3.1  # Opsiyonel
```

**Install:**
```bash
pip install -r requirements_qt.txt
```

---

## 🚀 BAŞLATMA

### Development

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend_qt
python main.py
```

### Production

**Build:**
```bash
pyinstaller frontend_qt/build.spec
```

**Çalıştırma:**
1. Backend'i başlat (`backend/main.py`)
2. `dist/BlockchainSimulator.exe` çift tıkla

**Not:** Backend ve frontend ayrı process'ler. Backend API olarak çalışmalı.

---

## 📋 ÖZELLİK KARŞILAŞTIRMASI

| Özellik | Streamlit | PySide6 |
|---------|-----------|---------|
| Real-time Updates | ✓ (refresh interval) | ✓✓ (QThread + Signal) |
| Performans | Orta | Yüksek |
| Customization | Sınırlı | Tam kontrol |
| Interaktivite | Orta | Yüksek |
| Deployment | Web (port gerekli) | Standalone exe |
| Görsel Kalite | İyi | Profesyonel |
| Network Map | streamlit-agraph | Custom QGraphicsScene |
| Blockchain View | HTML/CSS | Custom QGraphicsScene |
| Grafik | Plotly (web-based) | PyQtGraph (native) |
| Layout Esnekliği | Sabit | Dockable |
| Öğrenme Eğrisi | Düşük | Orta |

---

## 🎯 SONUÇ

Bu dokümanda PySide6 ile yapılacak UI'ın:
- Mimari yapısı
- Tüm widget seçimleri ve gerekçeleri
- API entegrasyonu
- Real-time güncelleme mekanizması
- Styling yaklaşımı
- Deployment stratejisi

detaylı olarak planlanmıştır.

**Sonraki Adım:** Milestone planı oluşturma ve kodlamaya başlama.
