# 🧪 UI Manuel Test Dokümanı - Interactive Blockchain Attack Simulator

## 📋 İÇİNDEKİLER

1. [Başlangıç Kontrolleri](#başlangıç-kontrolleri)
2. [Dashboard Sayfası](#dashboard-sayfası)
3. [Nodes Sayfası](#nodes-sayfası)
4. [Network Map Sayfası](#network-map-sayfası)
5. [Blockchain Explorer Sayfası](#blockchain-explorer-sayfası)
6. [PBFT Messages Sayfası](#pbft-messages-sayfası)
7. [Attack Control Panel (Dashboard Sol)](#attack-control-panel)
8. [Metrics Dashboard (Dashboard Sağ)](#metrics-dashboard)
9. [PBFT Status (Dashboard Alt)](#pbft-status)
10. [Hata Durumları](#hata-durumları)

---

## ⚙️ ÖN KOŞULLAR

### Backend'in Çalıştırılması

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Beklenen Çıktı:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend'in Çalıştırılması

```bash
# Terminal 2 - Frontend
cd frontend-PySide6
python main.py

# Beklenen:
# Ana pencere açılır (1200x800 px)
# Başlık: "Blockchain Attack Simulator"
```

---

## 1️⃣ BAŞLANGIÇ KONTROLLERİ

### 1.1 Uygulama Açılışı

**İŞLEM:** Uygulamayı başlat (`python main.py`)

**BEKLENEN SONUÇLAR:**
- ✅ Ana pencere 1200x800 boyutunda açılır
- ✅ Pencere başlığı: "Blockchain Attack Simulator"
- ✅ 5 tab görünür: 📊 Dashboard, 🖥️ Nodes, 🗺️ Network Map, ⛓️ Blockchain, 📨 PBFT Messages
- ✅ Dashboard tab'i aktif (açık)
- ✅ Status bar'da 2 label görünür:
  - **Connection Status:** "🔴 Disconnected" (kırmızı) VEYA "🟢 Connected" (yeşil)
  - **Last Update:** "Last update: Never" VEYA timestamp

**BACKEND ÇALIŞIYORSA:**
- Connection Label: **🟢 Connected**

**BACKEND ÇALIŞMIYORSA:**
- Connection Label: **🔴 Disconnected**
- Status bar message: "Connection error: ..."

---

### 1.2 Backend Bağlantı Testi

**İŞLEM:** Backend kapalıyken uygulamayı aç

**BEKLENEN SONUÇLAR:**
- ✅ Status bar: "🔴 Disconnected"
- ✅ Dashboard'da tüm metrikler sıfır/boş
- ✅ Start butonu **devre dışı** (disabled/grayed out)

**İŞLEM:** Backend'i başlat (uygulama açıkken)

**BEKLENEN SONUÇLAR:**
- ✅ 2-5 saniye içinde status bar "🟢 Connected" olur
- ✅ Start butonu **aktif** hale gelir
- ✅ Dashboard metrikleri güncellenir

---

## 2️⃣ DASHBOARD SAYFASI

### 2.1 Kontrol Butonları (Üst Bölüm)

#### ▶️ Start Butonu

**ÖN KOŞUL:** Backend bağlı, simülatör durdurulmuş

**İŞLEM:** "Start" butonuna tıkla

**BEKLENEN SONUÇLAR:**
1. **Buton Durumları:**
   - ✅ Start butonu **devre dışı** (grayed out)
   - ✅ Stop butonu **aktif** hale gelir
   - ✅ Reset butonu **aktif** hale gelir

2. **Status Label (Dashboard üst):**
   - ✅ "🟢 Running" görünür (yeşil)

3. **2 Saniye İçinde (İlk Güncelleme):**
   - ✅ System Overview bölümünde sayılar güncellenir:
     - **Total Nodes:** 10 (veya config'deki değer)
     - **Active Nodes:** 10
     - **Chain Length:** 1+ (başlangıç değeri)
     - **Network Health:** 100% (tüm node'lar healthy)
   - ✅ PBFT Consensus bölümünde:
     - **Primary:** node_0 (veya ilk validator)
     - **Current View:** 0
     - **Consensus Count:** 0+ (zamanla artar)
     - **Total Validators:** 4
   - ✅ Recent Activity log'da yeni olaylar görünmeye başlar:
     - "Block #X mined by node_Y"
     - "PBFT consensus reached"
     - vb.

4. **Status Bar:**
   - ✅ Last Update timestamp güncellenir (örn: "Last update: 2s ago")

5. **Metrics Dashboard (Sağ Bölüm):**
   - ✅ Response Time grafiği çizilmeye başlar (her node için bir eğri)
   - ✅ Node Status Cards oluşur (10 kart, 2 sütun grid)
   - ✅ Network Health Bars güncellenir (Overall: 100%)
   - ✅ System Metrics güncellenir (Blocks/min, TX/sec, Avg Block Time)

6. **PBFT Status (Alt Bölüm):**
   - ✅ PBFT Status labels güncellenir
   - ✅ Message Traffic table'da PBFT mesajları görünmeye başlar

---

#### ⏸ Stop Butonu

**ÖN KOŞUL:** Simülatör çalışıyor

**İŞLEM:** "Stop" butonuna tıkla

**BEKLENEN SONUÇLAR:**
1. **Buton Durumları:**
   - ✅ Stop butonu **devre dışı**
   - ✅ Start butonu **aktif**
   - ✅ Reset butonu **aktif** (kalır)

2. **Status Label:**
   - ✅ "🔴 Stopped" görünür (kırmızı)

3. **Veri Akışı:**
   - ✅ Tüm real-time güncellemeler **durur**
   - ✅ Grafik ve metrikler son değerde kalır (temizlenmez)
   - ✅ PBFT mesajları artmaz

4. **Status Bar:**
   - ✅ Last Update timestamp durur, son güncelleme zamanını gösterir

**NOT:** Veriler ekranda kalır, sadece yeni veri gelmez.

---

#### 🔄 Reset Butonu

**ÖN KOŞUL:** Herhangi bir durum (çalışıyor veya durdurulmuş)

**İŞLEM:** "Reset" butonuna tıkla

**BEKLENEN SONUÇLAR:**
1. **Simülatör Durumu:**
   - ✅ Eğer çalışıyorsa önce **durdurulur**
   - ✅ Backend'e reset API çağrısı yapılır

2. **Tüm Sayfalar Temizlenir:**
   - ✅ Dashboard metrikleri sıfırlanır
   - ✅ Nodes tree boşaltılır
   - ✅ Network Map temizlenir (node'lar kaybolur)
   - ✅ Blockchain Explorer temizlenir
   - ✅ PBFT Messages table'ı temizlenir

3. **Attack Panel:**
   - ✅ Tüm **active attacks** listesi temizlenir
   - ✅ Dropdownlar varsayılan değerlere döner

4. **Metrics Dashboard:**
   - ✅ Response Time grafiği temizlenir
   - ✅ Node Status Cards kaybolur
   - ✅ Health Bars sıfırlanır (0%)
   - ✅ System Metrics sıfırlanır

5. **Status:**
   - ✅ Status label: "🔴 Stopped"
   - ✅ Start butonu **aktif**

6. **Backend Yeniden Başlatılır:**
   - ✅ Start'a tekrar basınca yeni bir simülasyon başlar
   - ✅ Yeni genesis block oluşur
   - ✅ Node ID'leri yeniden atanır

---

### 2.2 System Overview (Metrikler)

**ÖN KOŞUL:** Simülatör çalışıyor

**BEKLENEN GÖRSELLEŞTİRME:**

```
System Overview
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ Total Nodes    │ Active Nodes   │ Chain Length   │ Network Health │
│      10        │       10       │      45        │      98%       │
│   (QLCDNumber) │  (QLCDNumber)  │  (QLCDNumber)  │ (QProgressBar) │
└────────────────┴────────────────┴────────────────┴────────────────┘
```

**DEĞER KONTROLÜ:**
- **Total Nodes:** Backend'deki toplam node sayısı (varsayılan: 10)
- **Active Nodes:** 
  - Normal durumda: Total Nodes ile aynı
  - Sybil attack sonrası: Total Nodes artar (sahte node'lar eklenir)
- **Chain Length:** 
  - Genesis block ile 1'den başlar
  - Her 5 saniyede (block_time) +1 artar
- **Network Health:** 
  - Hesaplama: `(healthy_nodes / total_nodes) * 100`
  - Normal: 100%
  - DDoS attack sırasında: Düşer (örn: 90%, çünkü 1 node under_attack)

**TEST SENARYOSU:**
1. Start'a bas → Total Nodes: 10, Active: 10, Chain: 1, Health: 100%
2. 10 saniye bekle → Chain Length artmış olmalı (örn: 3)
3. DDoS attack tetikle (1 node) → Health: 90% (9/10)
4. Attack bitince → Health: 100% tekrar

---

### 2.3 PBFT Consensus Bölümü

**BEKLENEN GÖRSELLEŞTİRME:**

```
PBFT Consensus
Primary: node_0  |  View: 0
Consensus Reached: 15  |  Validators: 4
```

**DEĞER KONTROLÜ:**
- **Primary:** 
  - İlk validator (varsayılan: node_0)
  - View change olursa değişir (örn: node_1, node_2)
- **View:** 
  - Başlangıç: 0
  - Byzantine attack veya network partition sonrası artabilir
- **Consensus Reached:** 
  - Her başarılı blok için +1
  - Chain Length ile yakın değerde olmalı
- **Validators:** 
  - Config'deki validator sayısı (varsayılan: 4)

**TEST SENARYOSU:**
1. Start → Primary: node_0, View: 0, Consensus: 0
2. 10 saniye bekle → Consensus artmış olmalı (örn: 2-3)
3. Byzantine attack (node_1) → View change olabilir (View: 1)

---

### 2.4 Recent Activity Log

**BEKLENEN GÖRSELLEŞTİRME:**

```
Recent Activity
┌──────────────────────────────────────┐
│ • Block #45 mined by node_2         │
│ • PBFT consensus reached             │
│ • DDoS attack started on node_5      │
│ • Block #44 mined by node_7          │
│ • ...                                │
└──────────────────────────────────────┘
(Son 20 event, en yeni üstte)
```

**LOG TÜRLERİ:**
1. **Block Mined:** "Block #X mined by node_Y"
2. **Consensus:** "PBFT consensus reached"
3. **Attack Started:** "DDoS attack started on node_5"
4. **Attack Stopped:** "DDoS attack stopped"
5. **View Change:** "PBFT view changed to 1"
6. **Fork Detected:** "Fork detected at block #X"

**TEST SENARYOSU:**
1. Start → Log'da ilk olaylar belirir
2. Her 5 saniyede yeni blok eventi
3. Attack tetikle → Attack eventi log'a eklenir
4. Attack stop et → Stop eventi görünür

---

## 3️⃣ NODES SAYFASI

### 3.1 Node Tree Görünümü

**ÖN KOŞUL:** Simülatör çalışıyor

**İŞLEM:** "🖥️ Nodes" tab'ine tıkla

**BEKLENEN GÖRÜNÜM:**

```
QTreeWidget
├─ 👑 Validators (4)
│  ├─ node_0 [Primary] 🟢 Trust:95 RT:50ms
│  ├─ node_1 🟢 Trust:88 RT:48ms
│  ├─ node_2 🟡 Trust:75 RT:120ms
│  └─ node_3 🟢 Trust:92 RT:55ms
└─ Regular Nodes (6)
   ├─ node_4 🟢 Balance:450 RT:45ms
   ├─ node_5 🔴 [Under Attack] RT:500ms
   └─ ...
```

**KOLON BAŞLIKLARI:**
1. **Node ID:** node_0, node_1, vb.
2. **Status:** 🟢 Healthy, 🔴 Under Attack, 🟡 Recovering
3. **Role/Info:** [Primary], Trust Score veya Balance
4. **Response Time:** RT: Xms

**STATUS İCONLARI:**
- 🟢 **Healthy:** Normal çalışma
- 🔴 **Under Attack:** DDoS, Byzantine, vb. saldırı altında
- 🟡 **Recovering:** Saldırı sonrası iyileşme

**ÖZELLİK KONTROLÜ:**

1. **Validators Grubu:**
   - ✅ Başlıkta "(4)" validator sayısı
   - ✅ Primary validator'da "[Primary]" badge
   - ✅ Trust Score gösterimi (0-100)
   - ✅ Response time (ms)

2. **Regular Nodes Grubu:**
   - ✅ Başlıkta "(6)" regular node sayısı
   - ✅ Balance gösterimi (coin)
   - ✅ Response time (ms)

3. **Sıralama (Sorting):**
   - ✅ Kolon başlıklarına tıkla → Sıralama değişir
   - Örn: Trust Score'a tıkla → En yüksek trust üstte

---

### 3.2 Node Tıklama (Selection)

**İŞLEM:** Bir node'a **tek tıkla**

**BEKLENEN SONUÇ:**
- ✅ Node satırı **vurgulanır** (seçilmiş renk)
- ✅ Arka plan rengi mavi olur (selection color)

**NOT:** Şu an sadece selection, detay dialog yok.

---

### 3.3 Node Status Değişimleri (Real-time)

**TEST SENARYOSU:**

1. **Normal Durum:**
   - Tüm node'lar: 🟢 Healthy

2. **DDoS Attack Tetikle (node_5):**
   - ✅ node_5: 🔴 [Under Attack]
   - ✅ Response Time artmış (örn: 50ms → 500ms)
   - ✅ Balance/Trust score değişmez

3. **Attack Bitince (20 saniye sonra):**
   - ✅ node_5: 🟡 Recovering (5 saniye)
   - ✅ Response Time düşmeye başlar
   - ✅ Sonra: 🟢 Healthy

4. **Byzantine Attack (node_1):**
   - ✅ node_1: 🔴 [Under Attack]
   - ✅ Trust Score düşer (örn: 95 → 75)
   - ✅ Attack bitince: 🟡 → 🟢

5. **Sybil Attack (20 sahte node):**
   - ✅ Regular Nodes grubu genişler: "(6)" → "(26)"
   - ✅ Yeni node'lar: 🔴 (Sybil flag)
   - ✅ ID'ler: sybil_node_0, sybil_node_1, vb.
   - ✅ Attack bitince: Sahte node'lar kaybolur

---

### 3.4 Byzantine ve Sybil İşaretleme

**KONTROL:**

**Byzantine Node:**
- ✅ Status: 🟠 (turuncu veya kırmızı, implementasyona göre)
- ✅ Trust Score çok düşük (örn: 30-40)
- ✅ "[Byzantine]" badge (opsiyonel)

**Sybil Node:**
- ✅ ID: "sybil_node_X" formatında
- ✅ Status: 🔴 (sahte node)
- ✅ Balance: 0 (madencilik yapmaz)

**Malicious (Majority Attack):**
- ✅ Validator'lar: 🔴
- ✅ "[Malicious]" badge veya tooltip

---

## 4️⃣ NETWORK MAP SAYFASI

### 4.1 Network Graph Görünümü

**ÖN KOŞUL:** Simülatör çalışıyor

**İŞLEM:** "🗺️ Network Map" tab'ine tıkla

**BEKLENEN GÖRÜNÜM:**

```
Control Buttons
[Zoom In] [Zoom Out] [Fit View] [Reset]

┌─────────────────────────────────────────┐
│                                         │
│   🔷 node_0 (Validator, Primary)       │
│        \                                │
│         🟢 node_4 (Regular)             │
│        /     \                          │
│   🔷 node_1    🟢 node_5 (Under Attack) │
│                                         │
│   (Interactive: hover, zoom, drag)     │
│                                         │
└─────────────────────────────────────────┘

Legend
🔷 Validator  🟢 Regular  🔴 Sybil
🟠 Byzantine  🟡 Under Attack
```

**NODE RENKLERİ:**
- 🔷 **Mavi (#2196F3):** Validator
- 🟢 **Yeşil (#4CAF50):** Regular
- 🔴 **Kırmızı (#F44336):** Sybil
- 🟠 **Turuncu (#FF9800):** Byzantine
- 🟡 **Sarı (#FFC107):** Under Attack

**BAĞLANTI ÇİZGİLERİ:**
- ✅ Node'lar arası gri çizgiler (mesh topology simülasyonu)
- ✅ Her node en az 2-3 diğer node'a bağlı

---

### 4.2 Zoom ve Pan Kontrolleri

**Zoom In Butonu:**

**İŞLEM:** [Zoom In] butonuna tıkla

**BEKLENEN:**
- ✅ Graph %110 büyür
- ✅ Node'lar daha büyük görünür
- ✅ Multiple tıklama ile daha da büyütülebilir

**Zoom Out Butonu:**

**İŞLEM:** [Zoom Out] butonuna tıkla

**BEKLENEN:**
- ✅ Graph %90 küçülür
- ✅ Daha fazla node görünür hale gelir

**Mouse Wheel Zoom:**

**İŞLEM:** Mouse wheel'i yukarı/aşağı kaydır

**BEKLENEN:**
- ✅ Wheel up: Zoom in
- ✅ Wheel down: Zoom out
- ✅ Smooth zoom (her adım %10)

**Pan (Kaydırma):**

**İŞLEM:** Boş alana tıklayıp sürükle

**BEKLENEN:**
- ✅ Graph hareket eder (pan)
- ✅ Cursor: Hand icon
- ✅ Sürükleme serbest (tüm yönler)

**Fit View Butonu:**

**İŞLEM:** [Fit View] butonuna tıkla

**BEKLENEN:**
- ✅ Tüm node'lar görünecek şekilde zoom ayarlanır
- ✅ Graph merkeze alınır

**Reset Butonu:**

**İŞLEM:** [Reset] butonuna tıkla

**BEKLENEN:**
- ✅ Zoom %100'e döner
- ✅ Graph orijinal pozisyonda
- ✅ Seçimler temizlenir

---

### 4.3 Node İnteraktivitesi

**Hover (Üzerine Gelme):**

**İŞLEM:** Mouse'u bir node üzerine getir

**BEKLENEN:**
- ✅ Node border kalınlaşır (2px → 4px)
- ✅ Border rengi beyaz olur (highlight)
- ✅ **Tooltip görünür:**
  ```
  Node ID: node_0
  Role: Validator
  Status: Healthy
  Response Time: 50ms
  Trust Score: 95
  ```
- ✅ Mouse çıkınca border orijinal haline döner

**Click (Tıklama):**

**İŞLEM:** Bir node'a tıkla

**BEKLENEN:**
- ✅ Node **seçilir** (highlight kalır)
- ✅ Border renginde kalıcı vurgu (beyaz veya accent color)
- ✅ Başka bir node'a tıklanana kadar seçili kalır

**Drag (Sürükleme):**

**İŞLEM:** Bir node'u tıklayıp sürükle

**BEKLENEN:**
- ✅ Node hareket eder (yeni pozisyon)
- ✅ **Bağlı edge'ler otomatik güncellenir** (çizgiler takip eder)
- ✅ Pozisyon değişikliği sadece görsel (backend etkilenmez)

---

### 4.4 Real-time Status Güncellemeleri

**TEST SENARYOSU:**

**1. Normal Durum:**
- 4 mavi validator, 6 yeşil regular node

**2. DDoS Attack (node_5):**
- ✅ node_5 rengi **🟡 sarı** olur (under_attack)
- ✅ Tooltip: "Status: Under Attack"

**3. Attack Bitince:**
- ✅ node_5 rengi **🟢 yeşil** tekrar (healthy)

**4. Byzantine Attack (node_1):**
- ✅ node_1 rengi **🟠 turuncu** (byzantine)
- ✅ Tooltip: "Status: Byzantine"

**5. Sybil Attack (20 sahte node):**
- ✅ Graph'ta 20 yeni **🔴 kırmızı node** belirir
- ✅ Konumlar otomatik hesaplanır (NetworkX spring layout)
- ✅ Yeni node'lar diğerlerine bağlanır (edge'ler eklenir)
- ✅ Attack bitince: Kırmızı node'lar kaybolur

**6. Majority Attack (51% validator):**
- ✅ 2-3 validator rengi **🔴 kırmızı** (malicious)
- ✅ Tooltip: "Status: Malicious"

**7. Network Partition:**
- ✅ Node'lar iki gruba ayrılır (görsel olarak net olmayabilir, edge'ler kopar)

---

### 4.5 Legend (Açıklama) Paneli

**BEKLENEN GÖRÜNÜM:**

```
Legend
🔷 Validator   🟢 Regular
🔴 Sybil       🟠 Byzantine
🟡 Under Attack
```

**KONTROL:**
- ✅ 5 node tipi açıklanmış
- ✅ Renkler doğru

---

## 5️⃣ BLOCKCHAIN EXPLORER SAYFASI

### 5.1 Blockchain İstatistikleri

**ÖN KOŞUL:** Simülatör çalışıyor

**İŞLEM:** "⛓️ Blockchain" tab'ine tıkla

**BEKLENEN ÜST PANELİ:**

```
Stats
Total Blocks: 45  |  Forks: 0
Pending TXs: 3    |  Orphans: 0
```

**DEĞER KONTROLÜ:**
- **Total Blocks:** Genesis + mined bloklar (Chain Length ile aynı)
- **Forks:** 
  - Normal: 0
  - Network Partition veya Majority Attack sonrası: 1+
- **Pending TXs:** 
  - Henüz bloğa eklenmemiş transaction'lar
  - 0-5 arası değişir
- **Orphans:** 
  - Fork resolve sonrası orphan kalan bloklar
  - Normal: 0

---

### 5.2 Blockchain Görselleştirme

**BEKLENEN GÖRÜNÜM:**

```
[Genesis] → [Blk1] → [Blk2] → [Blk3] → [Blk4] → ...
   🔷        🟢       🟢       🟢       🔴

Fork (varsa):
[Blk2] → [Blk2b] (orphan)
           🌫️

Horizontal scroll →
```

**BLOK RENK KODLARI:**
- 🔷 **Mavi (#2196F3):** Genesis block
- 🟢 **Yeşil (#4CAF50):** Normal block
- 🔴 **Kırmızı (#F44336):** Malicious validator tarafından üretilmiş
- 🌫️ **Gri (#9E9E9E):** Orphan block (fork çözümü sonrası)

**BLOK KARTI İÇERİĞİ:**

```
┌─────────────┐
│   Block #3  │ ← Index (büyük font)
│  a7f3b...   │ ← Hash (ilk 8 karakter)
│ Miner: node_2│ ← Miner ID
│   TX: 5     │ ← Transaction sayısı
└─────────────┘
```

---

### 5.3 Blok İnteraktivitesi

**Hover:**

**İŞLEM:** Mouse'u bir blok üzerine getir

**BEKLENEN:**
- ✅ **Tooltip görünür:**
  ```
  Block #3
  Hash: a7f3b2c4d5e6f7g8h9i0j1k2l3m4n5o6
  Previous Hash: 1a2b3c4d...
  Miner: node_2
  Transactions: 5
  Timestamp: 2025-01-01 12:30:45
  Nonce: 12345
  ```
- ✅ Blok border vurgulanır

**Click:**

**İŞLEM:** Bir bloğa tıkla

**BEKLENEN:**
- ✅ Blok seçilir (highlight kalır)

**Double-Click:**

**İŞLEM:** Bir bloğa çift tıkla

**BEKLENEN:**
- ✅ **Transaction Detail Dialog** açılır
- ✅ Dialog içeriği:
  ```
  Block #3 Transactions
  
  1. TX #0
     Sender: node_1
     Receiver: node_5
     Amount: 10 coins
     Signature: valid ✓
  
  2. TX #1
     ...
  
  [Close]
  ```

---

### 5.4 Fork Görselleştirme

**TEST SENARYOSU:**

**1. Network Partition Tetikle:**
- ✅ Blockchain görünümünde fork oluşur:
  ```
  [Blk5] → [Blk6] → [Blk7a] (Group A)
              ↓
           [Blk7b] (Group B)
  ```
- ✅ İki branch görünür (Y-axis offset)

**2. Partition Stop (Merge):**
- ✅ Bir branch kazanır (en uzun zincir)
- ✅ Kaybeden branch **gri** (orphan) olur
- ✅ Orphan bloklar alt branşta kalır

**3. Stats Panel:**
- ✅ Forks: 1
- ✅ Orphans: 1-2 (kaybeden branch)

---

### 5.5 Malicious Block Tespiti

**TEST SENARYOSU:**

**Majority Attack Tetikle:**

**BEKLENEN:**
- ✅ Malicious validator tarafından üretilen bloklar **🔴 kırmızı**
- ✅ Tooltip'te "Miner: node_0 (Malicious)" gösterimi
- ✅ Normal validator blokları 🟢 yeşil kalır

---

## 6️⃣ PBFT MESSAGES SAYFASI

### 6.1 PBFT Status Paneli

**ÖN KOŞUL:** Simülatör çalışıyor

**İŞLEM:** "📨 PBFT Messages" tab'ine tıkla

**BEKLENEN ÜST PANEL:**

```
PBFT Status
Primary: node_0  |  View: 0  |  Consensus: 15
Validators: 4    |  Messages: 234
```

**DEĞER KONTROLÜ:**
- **Primary:** İlk validator (view % total_validators)
- **View:** PBFT view number (view change ile artar)
- **Consensus:** Başarılı consensus sayısı
- **Validators:** 4
- **Messages:** Toplam PBFT mesaj sayısı (artar)

---

### 6.2 Message Traffic Table

**BEKLENEN GÖRÜNÜM:**

```
Message Traffic
┌──────────┬────────┬──────────┬──────────┬──────┐
│ Time     │ Sender │ Receiver │ Type     │ View │
├──────────┼────────┼──────────┼──────────┼──────┤
│ 12:30:45 │ node_0 │ ALL      │ PREP     │ 0    │
│ 12:30:45 │ node_1 │ ALL      │ PREPARE  │ 0    │
│ 12:30:45 │ node_2 │ ALL      │ PREPARE  │ 0    │
│ 12:30:45 │ node_3 │ ALL      │ COMMIT   │ 0    │
│ 12:30:46 │ node_0 │ ALL      │ REPLY    │ 0    │
└──────────┴────────┴──────────┴──────────┴──────┘
(En yeni üstte, max 100 row)
```

**MESAJ TİPLERİ VE RENKLERİ:**
- **PRE_PREPARE:** 🔵 Mavi (#2196F3) - Primary'nin blok önerisi
- **PREPARE:** 🟠 Turuncu (#FF9800) - Validator'ların hazır olduğu mesajı
- **COMMIT:** 🟢 Yeşil (#4CAF50) - Commit kararı
- **REPLY:** 🟣 Mor (#9C27B0) - Consensus tamamlandı

**KONTROL:**
- ✅ Table her 2 saniyede güncellenir (yeni mesajlar üstte)
- ✅ Timestamp formatı: HH:MM:SS
- ✅ Receiver: "ALL" (broadcast mesajları)
- ✅ View: Şu anki PBFT view
- ✅ Renk kodlaması satır arka planında

---

### 6.3 PBFT Mesaj Akışı

**TEST SENARYOSU:**

**1. Normal Consensus (5 saniyede 1 blok):**

**BEKLENEN MESAJ SIRASI:**
1. **PRE_PREPARE** (Primary → ALL): "Blok #X önerildi"
2. **PREPARE** (her validator → ALL): "Hazırım" (3-4 mesaj)
3. **COMMIT** (her validator → ALL): "Commit kararı" (3-4 mesaj)
4. **REPLY** (Primary → ALL): "Consensus başarılı"

**KONTROL:**
- ✅ Bu 4 faz sırası korunur
- ✅ Her faz için doğru renk
- ✅ View: 0 (normal)

**2. Byzantine Attack Sırasında:**

**BEKLENEN:**
- ✅ Byzantine validator **fake hash** gönderir (PRE_PREPARE)
- ✅ Diğer validator'lar **reddeder** (PREPARE mesajı yok)
- ✅ Consensus **başarısız** (COMMIT/REPLY yok)
- ✅ **View change** tetiklenir → View: 1
- ✅ Yeni primary ile tekrar consensus

---

### 6.4 View Change Gösterimi

**İŞLEM:** Byzantine attack tetikle veya primary çöker

**BEKLENEN:**
- ✅ PBFT Status panelinde **View: 1** (veya daha yüksek)
- ✅ **Primary: node_1** (veya bir sonraki validator)
- ✅ Message table'da **VIEW_CHANGE** tip mesajları (opsiyonel, implementasyona göre)

---

## 7️⃣ ATTACK CONTROL PANEL (Dashboard Sol)

### 7.1 Panel Erişimi

**İŞLEM:** Dashboard tab'ine git

**BEKLENEN GÖRÜNÜM:**

Sol tarafta **Attack Control Panel** widget'ı (Dashboard içine gömülü):

```
Attack Control Panel
┌─────────────────────────┐
│ 🌊 DDoS Attack         │
├─────────────────────────┤
│ ⚔️ Byzantine Attack     │
├─────────────────────────┤
│ 👥 Sybil Attack         │
├─────────────────────────┤
│ ⚡ Majority Attack (51%) │
├─────────────────────────┤
│ 🔌 Network Partition    │
├─────────────────────────┤
│ 💎 Selfish Mining       │
├─────────────────────────┤
│ ⚠️ Active Attacks (0)   │
└─────────────────────────┘
```

**KONTROL:**
- ✅ 7 section görünür (QToolBox items)
- ✅ Son section: Active Attacks (dinamik sayı)

---

### 7.2 DDoS Attack Panel

**İŞLEM:** "🌊 DDoS Attack" bölümüne tıkla (genişlet)

**BEKLENEN İÇERİK:**

```
🌊 DDoS Attack
Target: [Dropdown: node_5 ▼]
Intensity:
Low [=====|====] High
    (Slider: 1-10, default: 5)
[▶️ Trigger Attack] (buton)
```

**KONTROL:**
- ✅ **Target Dropdown:**
  - Tüm node'lar listelenir (validators + regular)
  - Varsayılan: İlk node (node_0 veya boş)
- ✅ **Intensity Slider:**
  - Min: 1, Max: 10, Default: 5
  - Label altında değer gösterimi: "5"
- ✅ **Trigger Button:**
  - Yeşil veya mavi renk
  - Text: "Trigger Attack"

---

#### DDoS Attack Tetikleme

**İŞLEM:**
1. Target: **node_5** seç
2. Intensity: **7** ayarla
3. **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ Active Attacks section'ı genişler
- ✅ Başlık: "⚠️ Active Attacks (1)"
- ✅ Yeni attack item eklenir:
  ```
  ┌───────────────────────────┐
  │ 🌊 DDOS on node_5         │ ← Icon + Type + Target
  │ [████████░░] 80%          │ ← Progress bar
  │ Remaining: 4s   [Stop]    │ ← Time + Stop button
  └───────────────────────────┘
  ```

**2. Metrics Dashboard (Response Time Graph):**
- ✅ node_5'in eğrisi **yükselir** (50ms → 500ms, 10x artış)
- ✅ Grafik real-time güncellenir

**3. Metrics Dashboard (Node Status Cards):**
- ✅ node_5 kartı:
  - Status icon: **🔴 Under Attack**
  - RT: **500ms** (10x artış)
  - Border color: **Kırmızı**

**4. Network Map:**
- ✅ node_5 rengi **🟡 sarı** (under_attack)

**5. Nodes Page:**
- ✅ node_5: **🔴 [Under Attack]** RT: 500ms

**6. PBFT Messages:**
- ✅ node_5 PBFT mesajları göndermeye devam eder (role=regular ise consensus'a dahil değildir zaten)

**7. Dashboard Activity Log:**
- ✅ Yeni log: "DDoS attack started on node_5"

**8. 20 Saniye Sonra (Otomatik İyileşme):**
- ✅ Active Attacks'tan **kaldırılır**
- ✅ Başlık: "⚠️ Active Attacks (0)"
- ✅ node_5: **🟡 Recovering** (5 saniye)
- ✅ RT düşmeye başlar: 500ms → 250ms → 100ms → 50ms
- ✅ Sonra: **🟢 Healthy**
- ✅ Log: "DDoS attack stopped on node_5"

---

#### DDoS Attack Manuel Durdurma

**İŞLEM:** Attack item'daki **[Stop]** butonuna tıkla

**BEKLENEN:**
- ✅ Attack **hemen** durdurulur
- ✅ Active Attacks'tan kaldırılır
- ✅ node_5: 🟡 Recovering → 🟢 Healthy
- ✅ Log: "DDoS attack stopped (manually)"

---

### 7.3 Byzantine Attack Panel

**İŞLEM:** "⚔️ Byzantine Attack" bölümüne tıkla

**BEKLENEN İÇERİK:**

```
⚔️ Byzantine Attack
Target: [Dropdown: node_1 ▼]
(Only validators shown)
Warning: This will compromise a validator
[▶️ Trigger Attack]
```

**KONTROL:**
- ✅ **Target Dropdown:**
  - **Sadece validator'lar** listelenir (node_0, node_1, node_2, node_3)
  - Regular node'lar görünmez
- ✅ **Warning Label:**
  - "This will compromise a validator" metni
- ✅ **Trigger Button:**
  - Kırmızımsı renk (tehlikeli işlem)

---

#### Byzantine Attack Tetikleme

**İŞLEM:**
1. Target: **node_1** seç
2. **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ "⚔️ BYZANTINE on node_1" item eklenir
- ✅ Progress bar, remaining time, Stop button

**2. Nodes Page:**
- ✅ node_1: **🟠 Byzantine** veya **🔴 Under Attack**
- ✅ Trust Score düşer: 95 → **75** (-20 penalty)

**3. Network Map:**
- ✅ node_1 rengi **🟠 turuncu** (byzantine)

**4. PBFT Messages:**
- ✅ node_1 **fake hash** gönderir (PRE_PREPARE mesajında)
- ✅ Diğer validator'lar **reddeder**
- ✅ Consensus **başarısız** (bu round için)
- ✅ **View change** tetiklenir → View: 1
- ✅ Yeni primary: node_2 (veya bir sonraki)

**5. PBFT Status:**
- ✅ View: **1** (artar)
- ✅ Primary: **node_2** (değişir)
- ✅ Consensus count artmaz (başarısız round)

**6. Dashboard Activity Log:**
- ✅ "Byzantine attack started on node_1"
- ✅ "PBFT view changed to 1"

**7. 30 Saniye Sonra (Otomatik İyileşme):**
- ✅ node_1: 🟡 Recovering → 🟢 Healthy
- ✅ Trust Score **düşük kalır** (75, tekrar artmaz otomatik)
- ✅ View **değişmez** (1'de kalır, manuel reset gerekir)

---

### 7.4 Sybil Attack Panel

**İŞLEM:** "👥 Sybil Attack" bölümüne tıkla

**BEKLENEN İÇERİK:**

```
👥 Sybil Attack
Fake Nodes:
5 [=====|=====] 50
    (Slider: 5-50, default: 10)
[▶️ Trigger Attack]
```

**KONTROL:**
- ✅ **Fake Nodes Slider:**
  - Min: 5, Max: 50, Default: 10
  - Label: "10 fake nodes"

---

#### Sybil Attack Tetikleme

**İŞLEM:**
1. Fake Nodes: **20** ayarla
2. **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ "👥 SYBIL (20 nodes)" item eklenir

**2. Dashboard → System Overview:**
- ✅ Total Nodes: **30** (10 + 20)
- ✅ Active Nodes: **30**
- ✅ Network Health düşer: 100% → **33%** (10 healthy / 30 total)

**3. Nodes Page:**
- ✅ Regular Nodes grubu: **(26)** (6 + 20)
- ✅ Yeni node'lar:
  - ID: **sybil_node_0**, **sybil_node_1**, ...
  - Status: **🔴 Sybil**
  - Balance: 0
  - RT: 0ms (aktif değil)

**4. Network Map:**
- ✅ 20 yeni **🔴 kırmızı node** belirir
- ✅ Konumlar otomatik hesaplanır (NetworkX layout)
- ✅ Yeni edge'ler eklenir (bağlantılar)
- ✅ Graph otomatik fit view yapar (tüm node'lar görünsün)

**5. Dashboard Activity Log:**
- ✅ "Sybil attack started (20 fake nodes)"

**6. 60 Saniye Sonra (Otomatik İyileşme):**
- ✅ Sahte node'lar **kaldırılır** (teker teker, kademeli)
- ✅ Total Nodes: **10** tekrar
- ✅ Network Health: **100%**
- ✅ Network Map'te kırmızı node'lar kaybolur
- ✅ Log: "Sybil attack stopped (20 nodes removed)"

---

### 7.5 Majority Attack Panel

**İŞLEM:** "⚡ Majority Attack (51%)" bölümüne tıkla

**BEKLENEN İÇERİK:**

```
⚡ Majority Attack (51%)
Warning: This will compromise 51% of validators
[▶️ Trigger Attack] (kırmızı buton)
```

**KONTROL:**
- ✅ **Warning:** Tehlike mesajı
- ✅ **Trigger Button:** Kırmızı renk (dangerous)

---

#### Majority Attack Tetikleme

**İŞLEM:** **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ "⚡ MAJORITY ATTACK" item eklenir

**2. Nodes Page (Validators):**
- ✅ 2-3 validator **malicious** olur (51%):
  - Örnek: node_0, node_1 (2/4 = 50%+ ise yeterli)
  - Status: **🔴 Malicious**
  - Trust Score düşer: -30 penalty

**3. Network Map:**
- ✅ Malicious validator'lar **🔴 kırmızı**

**4. Blockchain Explorer:**
- ✅ Malicious validator'ların ürettiği bloklar **🔴 kırmızı**
- ✅ Normal validator'lar 🟢 yeşil
- ✅ **Fork** oluşabilir (iki zincir)

**5. PBFT Consensus:**
- ✅ Malicious validator'lar **kendi bloklarını onaylar**
- ✅ Honest validator'lar **reddeder**
- ✅ View change sık olur

**6. Dashboard → Network Health:**
- ✅ Düşer: 100% → **50%** (2/4 validator malicious)

**7. Dashboard Activity Log:**
- ✅ "Majority attack started (51% validators compromised)"
- ✅ "Fork detected at block #X" (opsiyonel)

**8. 60 Saniye Sonra (Otomatik İyileşme):**
- ✅ Malicious validator'lar **temizlenir**
- ✅ Trust Score düşük kalır (restore edilmez)
- ✅ Fork **resolve** edilir (en uzun zincir kazanır)
- ✅ Kısa zincir **orphan** olur

---

### 7.6 Network Partition Panel

**İŞLEM:** "🔌 Network Partition" bölümüne tıkla

**BEKLENEN İÇERİK:**

```
🔌 Network Partition
Info: Network will be split into 2 groups
[▶️ Trigger Attack]
```

**KONTROL:**
- ✅ **Info Label:** Açıklama metni
- ✅ **Trigger Button:** Turuncu renk

---

#### Network Partition Tetikleme

**İŞLEM:** **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ "🔌 PARTITION" item eklenir

**2. Network Map:**
- ✅ Node'lar iki gruba ayrılır (görsel olarak fark edilmeyebilir)
- ✅ Edge'ler **kopar** (gruplar arası bağlantı yok)
  - Örnek: Group A (node_0-4), Group B (node_5-9)

**3. PBFT Messages:**
- ✅ Her grup **kendi PBFT** yapar (bağımsız)
- ✅ Group A mesajları Group B'ye ulaşmaz (blocked)

**4. Blockchain Explorer:**
- ✅ **İki paralel zincir** oluşur:
  - Group A: [Genesis] → [Blk1] → [Blk2a] → [Blk3a] → ...
  - Group B: [Genesis] → [Blk1] → [Blk2b] → [Blk3b] → ...
- ✅ Fork gösterimi

**5. Blockchain Stats:**
- ✅ Forks: **1** (veya 2, implementasyona göre)

**6. Dashboard Activity Log:**
- ✅ "Network partition started (2 groups)"
- ✅ "Fork detected"

**7. 45 Saniye Sonra (Otomatik Merge):**
- ✅ Partition **kaldırılır**
- ✅ Gruplar **birleşir** (merge)
- ✅ **En uzun zincir kazanır** (longest chain rule)
- ✅ Kısa zincir **orphan** olur
- ✅ Orphan Blocks sayısı artar

**8. Blockchain Explorer (Merge Sonrası):**
- ✅ Kazanan zincir 🟢 yeşil
- ✅ Orphan zincir 🌫️ gri
- ✅ Log: "Partition resolved (longest chain wins)"

---

### 7.7 Selfish Mining Panel

**İŞLEM:** "💎 Selfish Mining" bölümüne tıkla

**BEKLENEN İÇERİK:**

```
💎 Selfish Mining
Attacker: [Dropdown: node_2 ▼]
Info: Attacker will keep blocks private
[▶️ Trigger Attack]
```

**KONTROL:**
- ✅ **Attacker Dropdown:** Tüm node'lar (validators + regular)
- ✅ **Info Label:** Açıklama

---

#### Selfish Mining Tetikleme

**İŞLEM:**
1. Attacker: **node_2** seç
2. **Trigger Attack** butonuna tıkla

**BEKLENEN SONUÇLAR:**

**1. Attack Panel → Active Attacks:**
- ✅ "💎 SELFISH MINING (node_2)" item eklenir

**2. Blockchain Explorer:**
- ✅ node_2'nin blokları **private chain**'de tutulur (görünmez)
- ✅ Public chain normal devam eder
- ✅ **İki zincir görünür:**
  - Public chain: 🟢 yeşil
  - Private chain: 🟠 turuncu (node_2'nin blokları)

**3. Dashboard → Chain Length:**
- ✅ Public chain length artmaya devam eder
- ✅ Private chain **daha hızlı** (node_2 blok üretiyor ama yayınlamıyor)

**4. 30 Saniye Sonra (Reveal Strategy):**
- ✅ node_2 private chain'i **yayınlar** (reveal)
- ✅ Private chain public'ten **uzunsa:**
  - Private chain kazanır
  - Public chain **orphan** olur
- ✅ **Eğer public daha uzunsa:**
  - Private chain **atılır** (kayıp)
  - Public chain kazanır

**5. Dashboard Activity Log:**
- ✅ "Selfish mining started (node_2)"
- ✅ "Private chain revealed (X blocks)"
- ✅ "Selfish mining succeeded/failed"

---

### 7.8 Multiple Simultaneous Attacks

**TEST SENARYOSU:**

**İŞLEM:**
1. DDoS attack tetikle (node_5)
2. Byzantine attack tetikle (node_1)
3. Sybil attack tetikle (10 sahte node)

**BEKLENEN:**
- ✅ **Active Attacks (3)** item'ı
- ✅ Her attack ayrı item olarak listelenir:
  ```
  ⚠️ Active Attacks (3)
  ┌─────────────────────┐
  │ 🌊 DDOS on node_5   │
  │ [█████░░░] 50%      │
  │ ...                 │
  ├─────────────────────┤
  │ ⚔️ BYZANTINE on n1  │
  │ [████████] 80%      │
  │ ...                 │
  ├─────────────────────┤
  │ 👥 SYBIL (10 nodes) │
  │ [███░░░░░] 30%      │
  │ ...                 │
  └─────────────────────┘
  ```
- ✅ Tüm attack'ların etkileri birlikte görünür:
  - Network Health: Çok düşer (örn: 40%)
  - Network Map: Birden çok renk değişimi
  - PBFT: View change, consensus başarısızlıkları

---

## 8️⃣ METRICS DASHBOARD (Dashboard Sağ)

### 8.1 Response Time Graph (Real-time)

**ÖN KOŞUL:** Simülatör çalışıyor

**BEKLENEN GÖRÜNÜM:**

```
Response Time (Real-time)
┌─────────────────────────────────┐
│ 500 ┤                           │
│     │   🔴 node_5 (spike)       │
│ 400 ┤  /                        │
│     │ /                         │
│ 300 ┤/                          │
│     │                           │
│ 200 ┤                           │
│     │                           │
│ 100 ┤─────────────────────────  │ ← Other nodes (50ms avg)
│     │                           │
│   0 └───────────────────────────┘
│       Last 50 data points       │
└─────────────────────────────────┘
Legend: node_0, node_1, ..., node_9
```

**KONTROL:**
- ✅ **PyQtGraph PlotWidget** (250px yükseklik)
- ✅ **10 eğri** (her node için biri)
- ✅ **Renk kodlaması:**
  - node_0: Mavi, node_1: Yeşil, node_2: Kırmızı, vb.
  - 10 farklı renk cycling
- ✅ **X-axis:** Zaman (son 50 nokta)
- ✅ **Y-axis:** Response time (ms)
- ✅ **Legend:** Node ID'leri ile renk eşleştirme
- ✅ **Grid:** Arka planda grid çizgileri
- ✅ **Dark theme:** Arka plan #2D2D2D

**REAL-TIME GÜNCELLEME:**

**Normal Durum:**
- ✅ Tüm eğriler 50ms civarında yatay
- ✅ Her 2 saniyede yeni data point eklenir
- ✅ Graph **otomatik scroll** (en yeni sağda)

**DDoS Attack (node_5):**
- ✅ node_5 eğrisi **sıçrama** yapar (50ms → 500ms)
- ✅ Spike görünür
- ✅ Diğer eğriler stabil

**Attack Bitince:**
- ✅ node_5 eğrisi **düşer** (500ms → 250ms → 50ms)
- ✅ Smooth recovery

---

### 8.2 Node Status Cards (Grid Layout)

**BEKLENEN GÖRÜNÜM:**

```
Node Status Cards
┌─────────────┬─────────────┐
│ 🟢 node_0  │ 🟢 node_1  │
│ RT: 50ms   │ RT: 48ms   │
│ Trust: ███ │ Trust: ███ │
│     95     │     88     │
├─────────────┼─────────────┤
│ 🟡 node_2  │ 🟢 node_3  │
│ RT: 120ms  │ RT: 55ms   │
│ Trust: ██░ │ Trust: ███ │
│     75     │     92     │
├─────────────┼─────────────┤
│ 🟢 node_4  │ 🔴 node_5  │
│ RT: 45ms   │ RT: 500ms  │
│ Bal: 450   │ [Under Atk]│
│ ████████░  │ ░░░░░░░░░░ │
└─────────────┴─────────────┘
... (10 kart, 2 sütun)
```

**CARD DETAYLARI:**

**Validator Kartı (node_0):**
```
┌─────────────────┐
│ 🟢 node_0      │ ← Status icon + ID
│ RT: 50ms       │ ← Response time
│ Trust: █████░  │ ← Trust score bar (0-100)
│      95        │ ← Numeric value
└─────────────────┘
```

**Regular Node Kartı (node_4):**
```
┌─────────────────┐
│ 🟢 node_4      │
│ RT: 45ms       │
│ Balance: 450   │ ← Coin balance
│ ████████░      │ ← Balance bar (scale)
└─────────────────┘
```

**KONTROL:**
- ✅ **10 kart** (her node için bir tane)
- ✅ **2-column grid** layout (5 satır)
- ✅ **Status icons:**
  - 🟢 Healthy: Yeşil
  - 🔴 Under Attack: Kırmızı
  - 🟡 Recovering: Sarı
  - ⚪ Unknown: Beyaz (hata durumu)
- ✅ **Border color:**
  - Healthy: Yeşil border-left (4px)
  - Under Attack: Kırmızı
  - Recovering: Sarı
- ✅ **Progress bar color:**
  - Validator: Yeşil (trust score)
  - Regular: Mavi (balance)
- ✅ **Hover effect:**
  - Border rengi daha koyu olur

**REAL-TIME GÜNCELLEME:**

**DDoS Attack (node_5):**
- ✅ node_5 kartı:
  - Icon: 🟢 → 🔴
  - RT: 45ms → 500ms
  - Border: Kırmızı

**Byzantine Attack (node_1):**
- ✅ node_1 kartı:
  - Icon: 🟢 → 🔴
  - Trust: 88 → 68 (-20)
  - Bar: █████ → ███░░

**Sybil Attack (20 sahte node):**
- ✅ **20 yeni kart** eklenir (scroll gerekebilir)
- ✅ Sahte node kartları:
  - ID: sybil_node_0, sybil_node_1, ...
  - Icon: 🔴 (Sybil)
  - RT: 0ms (pasif)
  - Balance: 0

---

### 8.3 Network Health Bars

**BEKLENEN GÖRÜNÜM:**

```
Network Health
Overall: [████████░] 88%
Validators: [█████████] 95%
Regular: [███████░░] 82%
```

**KONTROL:**
- ✅ **3 QProgressBar** (0-100 range)
- ✅ **Renk:** Yeşil (#4CAF50)
- ✅ **Format:** %p% (percentage gösterimi)
- ✅ **Hesaplama:**
  - **Overall:** `(healthy_nodes / total_nodes) * 100`
  - **Validators:** `(healthy_validators / total_validators) * 100`
  - **Regular:** `(healthy_regular / total_regular) * 100`

**TEST SENARYOLARI:**

**Normal Durum:**
- ✅ Overall: 100% (10/10)
- ✅ Validators: 100% (4/4)
- ✅ Regular: 100% (6/6)

**DDoS Attack (1 regular node):**
- ✅ Overall: 90% (9/10)
- ✅ Validators: 100% (4/4)
- ✅ Regular: 83% (5/6)

**Byzantine Attack (1 validator):**
- ✅ Overall: 90% (9/10)
- ✅ Validators: 75% (3/4)
- ✅ Regular: 100% (6/6)

**Majority Attack (2 validators):**
- ✅ Overall: 80% (8/10)
- ✅ Validators: 50% (2/4)
- ✅ Regular: 100% (6/6)

**Sybil Attack (20 sahte):**
- ✅ Overall: 33% (10/30, sahte node'lar unhealthy)
- ✅ Validators: 100% (4/4, etkilenmez)
- ✅ Regular: 23% (6/26, sahte node'lar regular sayılır)

---

### 8.4 System Metrics

**BEKLENEN GÖRÜNÜM:**

```
System Metrics
Blocks/min: 12
TX/sec: 5.2
Avg Block Time: 5.1s
```

**KONTROL:**
- ✅ **3 metric label** (QGridLayout)
- ✅ **Bold font** (14px)
- ✅ **Formatting:**
  - Blocks/min: Integer (örn: 12)
  - TX/sec: Float, 1 decimal (örn: 5.2)
  - Avg Block Time: Float, 1 decimal + "s" suffix (örn: 5.1s)

**DEĞER HESAPLAMALARI:**

**Blocks/min:**
- Backend API'den alınır
- Hesaplama: `(son 60 saniyede üretilen blok sayısı)`
- Normal: 12 (5 saniye block time → 12 blok/60 saniye)

**TX/sec:**
- Hesaplama: `(toplam transaction / toplam süre)`
- Örnek: 100 TX / 20 saniye = 5.0 TX/sec

**Avg Block Time:**
- Hesaplama: `(toplam blok süresi / blok sayısı)`
- Normal: 5.0s (config'deki block_time)

**REAL-TIME GÜNCELLEME:**
- ✅ Her 2 saniyede backend'den yeni değerler
- ✅ Değerler dinamik değişir

---

## 9️⃣ PBFT STATUS (Dashboard Alt)

### 9.1 PBFT Status Labels

**BEKLENEN GÖRÜNÜM:**

```
PBFT Status
Primary: node_0  |  View: 0  |  Consensus: 15
Validators: 4    |  Messages: 234
```

**KONTROL:**
- ✅ **5 QLabel** (horizontal layout)
- ✅ **Değerler:**
  - **Primary:** İlk validator (view % total_validators)
    - Örnek: View 0 → node_0, View 1 → node_1, View 2 → node_2, vb.
  - **View:** PBFT view number (view change ile artar)
  - **Consensus:** Başarılı consensus sayısı (her blok için +1)
  - **Validators:** 4 (sabit, config'den)
  - **Messages:** Toplam PBFT mesaj sayısı (artar)

**REAL-TIME GÜNCELLEME:**

**Normal Durum:**
- ✅ Her 2 saniyede güncellenir
- ✅ Consensus count artar (+1 her blok)
- ✅ Messages count artar (+4-5 her blok, PRE_PREPARE, PREPARE, COMMIT, REPLY)

**Byzantine Attack Sonrası:**
- ✅ **View change:** View 0 → 1
- ✅ **Primary değişir:** node_0 → node_1

---

## 🔟 HATA DURUMLARI

### 10.1 Backend Bağlantı Hatası

**SENARYO:** Backend çalışmıyor

**BEKLENEN:**
- ✅ Status bar: **🔴 Disconnected**
- ✅ Start butonu **devre dışı**
- ✅ Tüm metrikler sıfır/boş
- ✅ Status bar mesajı: "Connection error: Connection refused"

**SENARYO:** Backend çalışırken çöker

**BEKLENEN:**
- ✅ 2-5 saniye içinde status bar: **🔴 Disconnected**
- ✅ Real-time güncellemeler **durur**
- ✅ Son değerler ekranda kalır
- ✅ Attack'lar devam eder (frontend tarafında progress bar)

---

### 10.2 API Hataları

**SENARYO:** Attack tetikleme başarısız (backend hatası)

**İŞLEM:** DDoS attack tetikle (backend 500 döndürür)

**BEKLENEN:**
- ✅ Attack **eklenmez** (Active Attacks'ta görünmez)
- ✅ Status bar'da hata mesajı: "Attack failed: Internal server error"
- ✅ Hata mesajı 5 saniye sonra kaybolur

**SENARYO:** Stop attack başarısız

**İŞLEM:** Active attack'ı durdur (backend hatası)

**BEKLENEN:**
- ✅ Attack **ekranda kalır** (kaldırılmaz)
- ✅ Status bar: "Failed to stop attack: ..."

---

### 10.3 Veri Tutarsızlıkları

**SENARYO:** Backend'den malformed data (missing fields)

**BEKLENEN:**
- ✅ UI **crash etmez**
- ✅ Eksik fieldlar **default değerler** alır
- ✅ Hata log'lanır (console)
- ✅ Kullanıcı normal kullanmaya devam edebilir

**SENARYO:** Node ID değişikliği (reset sonrası)

**BEKLENEN:**
- ✅ Eski node'lar temizlenir
- ✅ Yeni node'lar eklenir
- ✅ Graph, tree, cards yeniden oluşur

---

## 📝 TEST CHECKLIST

### Başlangıç
- [ ] Uygulama açılır (1200x800)
- [ ] Backend bağlantısı kurulur (🟢 Connected)
- [ ] 5 tab görünür
- [ ] Dashboard varsayılan açık

### Dashboard Kontrolleri
- [ ] Start butonu çalışır
- [ ] Stop butonu çalışır
- [ ] Reset butonu çalışır
- [ ] System Overview metrikleri güncellenir
- [ ] PBFT Consensus bilgileri doğru
- [ ] Recent Activity log dolar

### Nodes Sayfası
- [ ] Node tree oluşur (Validators + Regular)
- [ ] Status icons doğru
- [ ] Trust Score/Balance gösterilir
- [ ] Node selection çalışır
- [ ] Real-time status güncellemeleri

### Network Map
- [ ] Graph görünür (10 node)
- [ ] Node renkleri doğru (role bazlı)
- [ ] Zoom In/Out çalışır
- [ ] Mouse wheel zoom
- [ ] Pan çalışır
- [ ] Fit View çalışır
- [ ] Hover tooltip görünür
- [ ] Node click selection
- [ ] Node drag + edge update
- [ ] Real-time status değişimleri

### Blockchain Explorer
- [ ] Stats paneli doğru (Total Blocks, Forks, vb.)
- [ ] Blockchain graph görünür
- [ ] Blok renkleri doğru (genesis, normal, malicious, orphan)
- [ ] Hover tooltip çalışır
- [ ] Blok click selection
- [ ] Fork görselleştirmesi

### PBFT Messages
- [ ] PBFT Status paneli doğru
- [ ] Message Traffic table dolar
- [ ] Mesaj renkleri doğru (type bazlı)
- [ ] Real-time mesaj ekleme

### Attack Panel
- [ ] 7 section görünür
- [ ] **DDoS:** Target, Intensity, Trigger
- [ ] **Byzantine:** Validator-only dropdown, Trigger
- [ ] **Sybil:** Fake count slider, Trigger
- [ ] **Majority:** Warning, Trigger
- [ ] **Partition:** Info, Trigger
- [ ] **Selfish Mining:** Attacker dropdown, Trigger
- [ ] **Active Attacks:** Item ekleme, progress bar, stop button

### Metrics Dashboard
- [ ] Response Time graph çalışır
- [ ] Node Status Cards oluşur
- [ ] Network Health Bars güncellenir
- [ ] System Metrics doğru

### Attack Testleri
- [ ] DDoS attack tetiklenir, etkiler görünür, stop çalışır
- [ ] Byzantine attack tetiklenir, view change, trust düşer
- [ ] Sybil attack tetiklenir, sahte node'lar eklenir
- [ ] Majority attack tetiklenir, malicious validator'lar
- [ ] Network Partition tetiklenir, fork oluşur
- [ ] Selfish Mining tetiklenir, private chain
- [ ] Multiple simultaneous attacks

### Hata Durumları
- [ ] Backend çalışmıyorsa connection error
- [ ] Attack tetikleme başarısız olursa hata mesajı
- [ ] Malformed data crash etmez

---

## 🎯 SONUÇ

Bu doküman, Interactive Blockchain Attack Simulator projesinin PySide6 UI'ını manuel olarak test etmek için **kapsamlı bir rehberdir**.

Her işlem için:
- ✅ **Beklenen sonuçlar** detaylıca açıklanmıştır
- ✅ **Görsel örnekler** verilmiştir
- ✅ **Test senaryoları** tanımlanmıştır
- ✅ **Hata durumları** belirtilmiştir

**Kullanım:**
1. Backend'i başlat
2. Frontend'i başlat
3. Bu dokümandaki her section'ı sırayla test et
4. Checkboxları işaretle
5. Hataları kaydet

**Başarılı Test Kriteri:**
Tüm checkboxlar işaretli ise UI testi başarılıdır. ✅

---

**Doküman Sonu**