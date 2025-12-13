# Blockchain Fork Görselleştirme Tasarım Dokümanı

## 📋 Genel Bakış

Blockchain simülatörüne fork (zincir ayrılması) durumlarını görsel olarak gösterme özelliği ekleme planı.

**Amaç:** Network partition veya diğer saldırılar sonucu oluşan fork'ları ekranda görselleştirmek, hangi zincirin kazandığını göstermek.

---

## 🎨 Görsel Tasarım

### Fork Görselleştirme Örneği

```
Genesis → Blok1 → Blok2 ─┬→ Blok3a → Blok4a → Blok5a → ... → Blok18a ✓ (KAZANAN ZİNCİR)
                         │   🟢 Active                          🏆 Winner
                         │
                         └→ Blok3b → Blok4b → Blok5b → ... → Blok10b ✗ (ORPHANED)
                             🔴 Orphaned (Yarı şeffaf)
```

### Yerleşim Stratejisi

**Y-Axis Pozisyonlama:**
- Ana zincir (Genesis → ... → Son blok): `y = 0` (orta)
- Fork A: `y = 150px` (üst)
- Fork B: `y = -150px` (alt)
- Fork C: `y = 300px` (daha üst)

**X-Axis:**
- Blok index'e göre: Her blok 120px aralık
- Fork split noktası: Aynı X koordinatı, farklı Y

---

## 🔧 Backend Gereksinimleri

### 1. Fork Tracking Sistemi

Backend'de fork durumlarını takip edecek sistem:

```python
class ForkManager:
    def __init__(self):
        self.forks = {}  # {fork_id: ForkInfo}
        self.active_forks = set()
        
    def detect_fork(self, block_a, block_b):
        """İki blok aynı prev_hash'e sahipse fork başlatır"""
        if block_a.prev_hash == block_b.prev_hash:
            fork_id = f"fork_{uuid4()}"
            self.create_fork(fork_id, block_a.index)
            
    def resolve_fork(self, winner_fork_id):
        """Fork çözümlendiğinde kazanan belirlenir"""
        for fork_id, fork_info in self.forks.items():
            if fork_id == winner_fork_id:
                fork_info.status = "active"
                fork_info.is_winner = True
            else:
                fork_info.status = "orphaned"
                fork_info.is_winner = False
```

### 2. Blok Yapısına Ekleme

```python
class Block:
    def __init__(self, ...):
        # Mevcut alanlar
        self.index = index
        self.hash = hash
        self.prev_hash = prev_hash
        # ...
        
        # YENİ ALANLAR
        self.fork_id = None  # Hangi fork'a ait (None = main chain)
        self.is_orphaned = False  # Orphan oldu mu?
```

### 3. API Response Formatı

**GET /api/blockchain/status**

```json
{
  "chain_length": 25,
  "blocks": [
    {
      "index": 0,
      "hash": "genesis_hash",
      "prev_hash": null,
      "fork_id": null,
      "is_orphaned": false,
      "miner": "genesis",
      "timestamp": "2024-01-01T00:00:00",
      "transactions": []
    },
    {
      "index": 2,
      "hash": "block2_hash",
      "prev_hash": "block1_hash",
      "fork_id": "main",
      "is_orphaned": false
    },
    {
      "index": 3,
      "hash": "block3a_hash",
      "prev_hash": "block2_hash",
      "fork_id": "fork_alpha",
      "is_orphaned": false
    },
    {
      "index": 3,
      "hash": "block3b_hash",
      "prev_hash": "block2_hash",
      "fork_id": "fork_beta",
      "is_orphaned": true
    }
  ],
  "forks": [
    {
      "id": "fork_alpha",
      "start_block_index": 3,
      "end_block_index": 18,
      "status": "active",
      "length": 16,
      "is_winner": true,
      "created_at": "2024-01-01T10:30:00",
      "resolved_at": "2024-01-01T10:45:00"
    },
    {
      "id": "fork_beta",
      "start_block_index": 3,
      "end_block_index": 10,
      "status": "orphaned",
      "length": 8,
      "is_winner": false,
      "created_at": "2024-01-01T10:30:00",
      "resolved_at": "2024-01-01T10:45:00"
    }
  ],
  "fork_events": [
    {
      "event_type": "fork_created",
      "timestamp": "2024-01-01T10:30:00",
      "block_index": 3,
      "fork_ids": ["fork_alpha", "fork_beta"],
      "cause": "network_partition"
    },
    {
      "event_type": "fork_resolved",
      "timestamp": "2024-01-01T10:45:00",
      "winner_fork_id": "fork_alpha",
      "loser_fork_ids": ["fork_beta"],
      "resolution_reason": "longest_chain"
    }
  ]
}
```

**Fork Status Enum:**
- `active`: Aktif, üretim devam ediyor
- `resolved`: Çözümlendi, kazanan belli
- `orphaned`: Orphan oldu, artık kullanılmıyor

---

## 🎨 Frontend Görselleştirmesi

### 1. QGraphicsView Layout

**ChainDrawer Sınıfı Güncellemesi:**

```python
class ChainDrawer:
    BLOCK_WIDTH = 120
    BLOCK_HEIGHT = 100
    FORK_Y_OFFSET = 150  # Fork'lar arası dikey mesafe
    
    def calculate_layout(self, blockchain_data):
        blocks = blockchain_data['blocks']
        forks = blockchain_data.get('forks', [])
        
        # Fork ID -> Y pozisyonu mapping
        fork_y_positions = self._assign_fork_positions(forks)
        
        layout = {
            'blocks': [],
            'connections': []
        }
        
        for block in blocks:
            fork_id = block.get('fork_id')
            
            # X pozisyonu: Blok index'e göre
            x = block['index'] * self.BLOCK_WIDTH
            
            # Y pozisyonu: Fork ID'ye göre
            if fork_id is None or fork_id == 'main':
                y = 0  # Ana zincir
            else:
                y = fork_y_positions.get(fork_id, 0)
            
            layout['blocks'].append({
                'data': block,
                'position': (x, y)
            })
        
        # Bağlantı çizgileri
        layout['connections'] = self._create_connections(blocks, layout['blocks'])
        
        return layout
    
    def _assign_fork_positions(self, forks):
        """Fork'lara Y pozisyonu atar"""
        positions = {}
        y_offset = self.FORK_Y_OFFSET
        
        # Active fork'ları üste
        active_forks = [f for f in forks if f['status'] == 'active']
        for i, fork in enumerate(active_forks):
            positions[fork['id']] = y_offset * (i + 1)
        
        # Orphaned fork'ları alta
        orphaned_forks = [f for f in forks if f['status'] == 'orphaned']
        for i, fork in enumerate(orphaned_forks):
            positions[fork['id']] = -y_offset * (i + 1)
        
        return positions
    
    def _create_connections(self, blocks, positioned_blocks):
        """Bloklar arası bağlantı çizgileri"""
        connections = []
        
        # Blok hash -> pozisyon mapping
        block_positions = {
            b['data']['hash']: b['position'] 
            for b in positioned_blocks
        }
        
        for block in blocks:
            if block['prev_hash'] and block['prev_hash'] in block_positions:
                start_pos = block_positions[block['prev_hash']]
                end_pos = block_positions[block['hash']]
                
                connections.append({
                    'start': start_pos,
                    'end': end_pos,
                    'is_fork_split': start_pos[1] != end_pos[1]
                })
        
        return connections
```

### 2. Block Item Görselleştirmesi

**Renk ve Stil:**

```python
class BlockItem(QGraphicsRectItem):
    # Renk tanımları
    COLORS = {
        'genesis': '#2196F3',      # Mavi
        'normal': '#4CAF50',       # Yeşil
        'malicious': '#F44336',    # Kırmızı
        'orphaned': '#9E9E9E',     # Gri
        'winner': '#FFD700'        # Altın
    }
    
    def update_appearance(self, block_data):
        # Fork durumuna göre stil
        if block_data.get('is_orphaned'):
            color = self.COLORS['orphaned']
            self.setOpacity(0.5)  # Yarı şeffaf
            border_width = 2
        elif block_data.get('is_winner'):
            color = self.COLORS['winner']
            self.setOpacity(1.0)
            border_width = 4  # Kalın border
        elif block_data.get('index') == 0:
            color = self.COLORS['genesis']
            border_width = 2
        else:
            color = self.COLORS['normal']
            border_width = 2
        
        # Renk uygula
        brush = QBrush(QColor(color))
        self.setBrush(brush)
        
        # Border
        pen = QPen(QColor('#FFFFFF'))
        pen.setWidth(border_width)
        self.setPen(pen)
```

### 3. Bağlantı Çizgileri

```python
def create_fork_connection(self, start_pos, end_pos):
    """Fork split için Y-şeklinde çizgi"""
    line = QGraphicsPathItem()
    path = QPainterPath()
    
    # Başlangıç noktası
    path.moveTo(start_pos[0], start_pos[1])
    
    # Y-split için control point
    mid_x = (start_pos[0] + end_pos[0]) / 2
    
    # Bezier curve ile yumuşak geçiş
    path.quadTo(mid_x, start_pos[1], mid_x, end_pos[1])
    path.lineTo(end_pos[0], end_pos[1])
    
    line.setPath(path)
    
    # Fork çizgisi stili
    pen = QPen(QColor('#FF9800'))  # Turuncu
    pen.setWidth(3)
    pen.setStyle(Qt.DashLine)  # Kesik çizgi
    line.setPen(pen)
    
    return line
```

### 4. Legend (Açıklama Paneli)

```python
def _create_legend(self):
    """Fork durumları için legend"""
    legend = QGroupBox("Legend")
    layout = QVBoxLayout(legend)
    
    items = [
        ("🟢 Active Fork", "Aktif zincir, blok üretimi devam ediyor"),
        ("🏆 Winner Fork", "Kazanan zincir (en uzun)"),
        ("🔴 Orphaned", "Orphan bloklar, artık kullanılmıyor"),
        ("🔷 Genesis", "Genesis block"),
        ("⚠️ Fork Split", "Zincirin ayrıldığı nokta")
    ]
    
    for icon, description in items:
        lbl = QLabel(f"{icon} - {description}")
        layout.addWidget(lbl)
    
    return legend
```

---

## 📊 UI Bileşenleri

### Blockchain Explorer Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Blockchain Statistics                                   │
│ Total Blocks: 25 | Forks: 2 | Active Forks: 1          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔎 Controls:                                            │
│ [Zoom In] [Zoom Out] [Fit View] [Auto-scroll]          │
│ Show: ☑ Genesis ☑ Normal ☑ Malicious ☑ Orphan         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                                                          │
│                 BLOCKCHAIN GRAPH                         │
│     (QGraphicsView - Fork görselleştirmesi)             │
│                                                          │
│  [Blok0]→[Blok1]→[Blok2]─┬→[Blok3a]→...→[Blok18a]✓    │
│                           └→[Blok3b]→...→[Blok10b]✗    │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Legend                                                   │
│ 🟢 Active Fork - Aktif zincir                          │
│ 🏆 Winner Fork - Kazanan zincir                        │
│ 🔴 Orphaned - Artık kullanılmayan bloklar              │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Veri Akışı

### 1. Fork Oluşma Süreci

```
Network Partition Attack Başlatıldı
         ↓
Backend: Ağ ikiye bölündü
         ↓
Her iki network kendi bloklarını üretiyor
         ↓
Backend: Fork detected (Blok 3a ve 3b aynı prev_hash)
         ↓
ForkManager: Yeni fork oluştur (fork_alpha, fork_beta)
         ↓
API Response: blocks + forks bilgisi döndür
         ↓
Frontend: ChainDrawer ile layout hesapla
         ↓
BlockchainGraphWidget: Y-axis'te farklı pozisyonlarda göster
```

### 2. Fork Çözümleme

```
Network Partition Sona Erdi
         ↓
Node'lar birbirini görüyor
         ↓
Backend: En uzun zinciri belirle (fork_alpha: 16 blok, fork_beta: 8 blok)
         ↓
ForkManager: fork_alpha = winner, fork_beta = orphaned
         ↓
API Response: fork status güncellendi
         ↓
Frontend: fork_beta blokları yarı şeffaf, gri renk
         ↓
fork_alpha blokları altın border ile vurgula
```

---

## 🛠️ Uygulama Adımları

### Faz 1: Backend Fork Tracking (Öncelik: Yüksek)

1. **ForkManager sınıfı oluştur**
   - Fork detection logic
   - Fork resolution (longest chain rule)
   - Fork event logging

2. **Block modeline fork_id ekle**
   - Migration (veritabanı varsa)
   - Serialization güncelleme

3. **API endpoint'leri güncelle**
   - `/api/blockchain/status` → forks array ekle
   - `/api/fork/events` → fork event history

**Test:**
- Network partition attack → 2 fork oluşmalı
- Partition sona erdiğinde → kazanan belirlenmeli
- API response → doğru fork bilgileri

### Faz 2: Frontend Layout Engine (Öncelik: Yüksek)

1. **ChainDrawer güncelleme**
   - Y-axis pozisyon hesaplama
   - Fork split detection
   - Connection line path calculation

2. **BlockItem görsel güncellemesi**
   - Fork durumuna göre renklendirme
   - Opacity (orphan bloklar)
   - Border width (winner fork)

**Test:**
- Mock data ile 2 fork görselleştirme
- Fork merge görselleştirme
- Zoom/pan çalışmalı

### Faz 3: UI/UX İyileştirmeleri (Öncelik: Orta)

1. **Fork bilgi paneli**
   - Active forks listesi
   - Fork istatistikleri
   - Fork event timeline

2. **Animasyonlar**
   - Blok eklenirken fade-in
   - Fork split animasyonu
   - Fork resolve transition

3. **Tooltip**
   - Block hover: Hangi fork'ta, status
   - Connection hover: Fork split/merge açıklaması

**Test:**
- User experience testleri
- Performance (100+ blok ile)

### Faz 4: Gelişmiş Özellikler (Öncelik: Düşük)

1. **Fork comparison tool**
   - İki fork'u yan yana göster
   - Blok içerik karşılaştırması

2. **Fork replay**
   - Fork oluşma anını tekrar oynat
   - Step-by-step görselleştirme

3. **Export/Share**
   - Fork görselini resim olarak kaydet
   - Fork event'lerini JSON export

---

## 🎯 Başarı Kriterleri

### Minimum Viable Product (MVP)

- ✅ Backend'de fork tracking çalışıyor
- ✅ API fork bilgilerini döndürüyor
- ✅ Frontend iki fork'u farklı Y pozisyonlarında gösteriyor
- ✅ Fork split ve merge görselleştiriliyor
- ✅ Orphan bloklar gri ve yarı şeffaf

### İdeal Ürün

- ✅ MVP özellikleri
- ✅ Fork bilgi paneli (istatistikler, timeline)
- ✅ Smooth animations
- ✅ Tooltips ve açıklamalar
- ✅ Performance: 100+ blok sorunsuz render
- ✅ Responsive (zoom/pan/fit)

---

## 📝 Notlar

### Backend Dikkat Edilecekler

- Fork detection thread-safe olmalı
- Aynı anda 3+ fork handle edebilmeli
- Memory leak riski (eski fork'lar cleanup)

### Frontend Dikkat Edilecekler

- QGraphicsScene performance (100+ item)
- Z-index yönetimi (overlap'lerde)
- Scroll position (yeni blok eklenince)

### Test Senaryoları

1. **Basit Fork:**
   - Blok 5'te split → 2 fork
   - Blok 10'da merge → 1 kazanan

2. **Multiple Forks:**
   - 3 farklı fork aynı anda
   - Farklı zamanlarda resolve

3. **Nested Fork:**
   - Fork içinde fork (teorik)

---

## 🔗 İlgili Dosyalar

**Backend:**
- `backend/blockchain/fork_manager.py` (yeni)
- `backend/models/block.py` (güncelleme)
- `backend/api/blockchain.py` (güncelleme)

**Frontend:**
- `ui/pages/blockchain_page.py` (güncelleme)
- `ui/widgets/blockchain_graph_widget.py` (güncelleme)
- `ui/widgets/block_item.py` (güncelleme)
- `ui/utils/chain_drawer.py` (güncelleme)

---

## 📅 Tahmini Süre

- **Faz 1 (Backend):** 2-3 gün
- **Faz 2 (Frontend Core):** 3-4 gün
- **Faz 3 (UI/UX):** 2-3 gün
- **Faz 4 (Advanced):** 3-5 gün (opsiyonel)

**Toplam MVP:** ~1 hafta
**Toplam İdeal:** ~2 hafta

---

**Doküman Versiyonu:** 1.0  
**Oluşturulma Tarihi:** 2024-12-13  
**Son Güncelleme:** 2024-12-13