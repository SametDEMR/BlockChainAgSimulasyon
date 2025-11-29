# Tamamlanan Özellikler

## MILESTONE 1: Minimal Çalışan Sistem ✅

### 1.1 Temel Altyapı ✅
**Dosya:** `config.py`

**Özellikler:**
- Merkezi yapılandırma sistemi
- Network ayarları (10 node, 4 validator)
- Blockchain parametreleri (5 sn blok süresi, difficulty 4)
- API ayarları (port 8000)
- UI ayarları (2 sn refresh)
- 6 saldırı tipi için parametreler
- Logging yapılandırması
- Helper fonksiyonlar

---

### 1.2 Blockchain Core ✅
**Dosyalar:** `backend/core/`

#### Transaction (`transaction.py`)
- Transaction veri yapısı
- RSA tabanlı imzalama ve doğrulama
- Coinbase transaction desteği
- Serialization (to/from dict)

#### Wallet (`wallet.py`)
- RSA key pair generation (2048 bit)
- Adres oluşturma (SHA256 hash)
- Transaction imzalama
- Bakiye takibi
- Public key PEM formatı

#### Block (`block.py`)
- Block veri yapısı
- SHA256 hash hesaplama
- Proof of Work mining
- Transaction listesi yönetimi
- Block validation
- Serialization

#### Blockchain (`blockchain.py`)
- Genesis block otomatik oluşturma
- Zincir yönetimi
- Transaction pool (pending transactions)
- Mining işlemi (coinbase + pending tx)
- Zincir doğrulama (hash chain kontrolü)
- Bakiye hesaplama
- Longest chain kuralı

**Test:** `test_core.py` - Tüm core modüller entegre test edildi

---

### 1.3 Basit Node Yapısı ✅
**Dosya:** `backend/network/node.py`

**Özellikler:**
- Benzersiz node ID (UUID)
- Rol sistemi (validator/regular)
- Her node'un kendi blockchain kopyası
- Her node'un kendi wallet'ı
- Transaction oluşturma ve imzalama
- Block mining
- Blockchain senkronizasyonu
- Status tracking (healthy, under_attack, recovering)
- Response time metrikleri
- Trust score sistemi (0-100)
- Byzantine ve Sybil bayrakları
- İstatistikler (mined blocks, earned coins, created txs)

**Test:** `test_node.py` - Node davranışları test edildi

---

### 1.4 Simulator ✅
**Dosya:** `backend/simulator.py`

**Özellikler:**
- Config tabanlı node oluşturma
- Validator/Regular node ayırımı
- Start/Stop kontrolleri
- Asyncio ile otomatik blok üretimi
- Block broadcasting (tüm node'lara yayma)
- Node lookup (ID ile arama)
- Status tracking
- Reset fonksiyonu
- Background task yönetimi

**Test:** `test_simulator.py` - Simülasyon ve auto-production test edildi

---

### 1.5 Minimal API ✅
**Dosya:** `backend/main.py`

**Endpoints:**
- `GET /` - Health check
- `GET /status` - Simülatör durumu
- `GET /blockchain` - İlk node'un blockchain'i
- `GET /nodes` - Tüm node listesi
- `GET /nodes/{node_id}` - Spesifik node detayı
- `POST /start` - Simülasyonu başlat + background task
- `POST /stop` - Simülasyonu durdur + task cancel
- `POST /reset` - Simülasyonu sıfırla

**Özellikler:**
- FastAPI framework
- CORS middleware (tüm originler)
- Background task entegrasyonu
- Asyncio task yönetimi
- Proper cleanup on shutdown
- Swagger UI (`/docs`)
- ReDoc (`/redoc`)

**Test:** `test_api.py` - Tüm endpoint'ler test edildi

---

### 1.6 Minimal Streamlit UI ✅
**Dosya:** `frontend/main.py`

**Özellikler:**
- Start/Stop/Reset butonları
- Gerçek zamanlı metrikler:
  - Status (Running/Stopped)
  - Total Nodes
  - Active Nodes
  - Chain Length
- Node listesi (3 tab):
  - All Nodes: Tüm node'lar, status, balance
  - Validators: Validator detayları, trust score
  - Regular: Regular node'lar, balance
- Config görüntüleme (collapsible)
- Otomatik yenileme (2 saniye)
- API bağlantı kontrolü
- Responsive layout (wide mode)

**Kullanım:**
```bash
# API başlat
python backend/main_old_1.py

# UI başlat
streamlit run frontend/main_old_1.py
```

---

## MILESTONE 2: PBFT Consensus ✅

### 2.1 Message Broker ✅
**Dosya:** `backend/network/message_broker.py`

**Özellikler:**
- Node kayıt sistemi (`register_node`, `unregister_node`)
- Asenkron mesaj gönderimi (`send_message`)
- Broadcast desteği (`broadcast`)
- Network delay simülasyonu (0.1-0.5 saniye)
- Her node için ayrı mesaj kuyruğu
- Mesaj alma (`get_messages_for_node`)
- Mesaj görüntüleme (`peek_messages_for_node`)
- Tip filtreli mesaj alma
- Kuyruk yönetimi (`clear_queue`, `clear_all_queues`)
- İstatistik takibi (toplam mesaj, broadcast sayısı)

**Message Sınıfı:**
- sender_id, receiver_id, message_type, content, timestamp
- Serialization (to_dict)

**Test:** `test_message_broker.py` - Mesajlaşma ve delay simülasyonu test edildi

---

### 2.2 PBFT Handler ✅
**Dosya:** `backend/network/pbft_handler.py`

**Özellikler:**
- 4 fazlı PBFT protokolü:
  1. **Pre-Prepare**: Primary validator blok önerir
  2. **Prepare**: Validator'lar hazır olduklarını bildirir
  3. **Commit**: Validator'lar commit kararı verir
  4. **Reply**: Konsensüs sağlandı, blok eklenir
- Byzantine Fault Tolerance hesaplaması (f = (n-1)/3)
- Gereken oy sayısı (2f + 1)
- Primary selection (view % total_validators)
- View change mekanizması
- Mesaj log sistemi (sequence_number -> phase -> messages)
- Konsensüs durumu kontrolü
- İstatistikler (consensus reached, view changes, blocks validated)

**PBFTMessage Sınıfı:**
- phase, view, sequence_number, block_hash, node_id, timestamp

**Test:** `test_pbft_handler.py` - PBFT protokolü ve Byzantine senaryo test edildi

---

### 2.3 Node'a PBFT Entegrasyonu ✅
**Dosya:** `backend/network/node.py` (güncellendi)

**Eklenenler:**
- `pbft: PBFTHandler` - Her validator için PBFT instance
- `message_broker` referansı - Node'lar arası iletişim
- `propose_block()` - Primary validator blok önerir (async)
- `process_pbft_messages()` - Bekleyen PBFT mesajlarını işler (async)
- `_handle_pre_prepare()` - Pre-prepare işle, prepare gönder
- `_handle_prepare()` - Prepare işle, commit gönder
- `_handle_commit()` - Commit işle, konsensüs kontrol
- PBFT istatistikleri `get_status()`'ta

**Değişiklikler:**
- `__init__` parametreleri: `total_validators`, `message_broker`
- Validator'lar PBFT kullanır, Regular'lar mine eder
- Node ID'ler PBFT için sabit (`node_0`, `node_1`, vb.)

**Test:** `test_node_pbft.py` - Node+PBFT entegrasyonu test edildi

---

### 2.4 Simulator'a PBFT ✅
**Dosya:** `backend/simulator.py` (güncellendi)

**Eklenenler:**
- `message_broker: MessageBroker` - Merkezi mesaj broker
- `pbft_message_processing()` - PBFT mesajları işleme background task
- Node'lara MessageBroker referansı
- Validator node'lara sabit ID atama (`node_0`, `node_1`, vb.)
- `get_pbft_messages()` - PBFT mesajlarını döndür (debug)
- PBFT istatistikleri `get_status()`'ta

**Güncellenenler:**
- `auto_block_production()` - Validator'lar için PBFT blok önerisi
- `initialize_nodes()` - MessageBroker'a node kaydı
- `reset()` - MessageBroker temizleme

**Test:** `test_simulator_pbft.py` - Simulator+PBFT tam entegrasyon test edildi

---

### 2.5 API Genişletme ✅
**Dosya:** `backend/main.py` (güncellendi)

**Yeni Endpoints:**
- `GET /network/nodes` - Node detayları + mesaj kuyruk boyutu + PBFT bilgisi
- `GET /network/messages` - PBFT mesaj trafiği, mesaj tipleri breakdown
- `GET /pbft/status` - PBFT konsensüs durumu, primary, view, validator'lar

**Güncellenenler:**
- `/start` - 2 background task başlatır (production + PBFT processing)
- `/stop` - Her iki task'i de durdurur
- `/status` - PBFT istatistikleri eklendi

**PBFT Status Response:**
```json
{
  "enabled": true,
  "total_validators": 4,
  "primary": "node_0",
  "current_view": 0,
  "total_consensus_reached": 5,
  "validators": [...]
}
```

**Test:** `test_api_pbft.py` - Yeni endpoint'ler test edildi

---

### 2.6 UI'ya PBFT Göstergesi ✅
**Dosya:** `frontend/main.py` (güncellendi)

**Eklenenler:**
- **PBFT Consensus Status Panel:**
  - Primary Validator göstergesi
  - Current View
  - Consensus Reached sayısı
  - Total Validators
  - Validator details (expandable)
- **PBFT Message Traffic Panel:**
  - Total Messages
  - PBFT Messages
  - Message Types sayısı
  - Message type breakdown (expandable)
- **Validator Tab Güncelleme:**
  - Primary validator'da 👑 badge
  - PBFT view gösterimi
  - Trust score

**Yeni API Fonksiyonları:**
- `get_pbft_status()` - PBFT durumu çek
- `get_network_messages()` - Network mesajları çek

**Test:** Manuel UI testi - PBFT göstergeleri çalışıyor

---

## MILESTONE 5: Sybil Saldırısı ✅

### 5.1 Sybil Attack Implementation ✅
**Dosya:** `backend/attacks/sybil.py`

**SybilAttack sınıfı:**
- `trigger(num_nodes)` - Saldırıyı başlat
- `stop()` - Saldırıyı durdur
- `get_status()` - Saldırı durumu
- `_auto_recovery()` - Otomatik iyileşme (60 saniye)

**Özellikler:**
- Çok sayıda sahte node oluşturma (varsayılan: 20)
- Sahte node'lara `is_sybil=True` bayrağı
- Otomatik iyileşme (60 saniye sonra)
- Manuel durdurma desteği
- Kademeli node temizleme
- Detaylı status ve effects tracking

**Güncelleme:** `backend/simulator.py`
- `_create_sybil_node()` - Sahte node oluştur
- `_remove_sybil_node()` - Sahte node kaldır

**Test:** `tests/test_sybil.py` - Sybil attack testi PASSED

---

### 5.2 Sybil Attack API Endpoints ✅
**Güncelleme:** `backend/main.py`

**Yeni Endpoints:**
- `POST /attack/sybil/trigger?num_nodes=20` - Sybil saldırısını tetikle
- `GET /attack/sybil/status` - Saldırı durumunu al
- `POST /attack/sybil/stop` - Saldırıyı durdur

**Test:** `tests/test_sybil_api.py` - API endpoint'leri PASSED

---

### 5.3 Network Visualizer ✅
**Yeni dosya:** `frontend/components/network_visualizer.py`

**Özellikler:**
- streamlit-agraph ile interactive network haritasi
- Renk kodlu node gösterimi:
  - 🔷 Mavi: Validator
  - 🟢 Yeşil: Regular
  - 🔴 Kırmızı: Sybil
  - 🟠 Turuncu: Byzantine
- Shape'ler:
  - dot: Normal
  - triangleDown: Under attack
  - diamond: Recovering
- Mesh topology simülasyonu
- Legend ve node istatistikleri

**Güncelleme:** `frontend/components/attack_panel.py`
- Sybil attack seçeneği eklendi
- `trigger_sybil_attack()` - Saldırı tetikleme
- `display_sybil_status()` - Saldırı durumu gösterimi
- `stop_sybil_attack()` - Saldırı durdurma
- Fake nodes slider (5-50)
- Progress bar (cleanup durumu)
- Fake node IDs listesi

**Güncelleme:** `frontend/main.py`
- Network Map tab'i eklendi (5 tab toplam)
- display_network_visualizer import

**Test:** Manuel UI testi - Network visualizer çalışıyor

---

## ✅ MILESTONE 5 Tamamlandı
**Çıktı:** Sybil saldırısı çalışıyor, ağ haritasında görünüyor.

---

## Proje Yapısı (Güncel)

```
BlockChainAgSimulasyon/
├── config.py                       # Merkezi yapılandırma
├── requirements.txt                # Bağımlılıklar
├── test_core.py                    # Core modül testleri
├── test_node.py                    # Node testleri
├── test_simulator.py               # Simulator testleri
├── test_api.py                     # API testleri
├── test_message_broker.py          # MessageBroker testleri (YENİ)
├── test_pbft_handler.py            # PBFT handler testleri (YENİ)
├── test_node_pbft.py               # Node+PBFT testleri (YENİ)
├── test_simulator_pbft.py          # Simulator+PBFT testleri (YENİ)
├── test_api_pbft.py                # API PBFT endpoint testleri (YENİ)
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI server (GÜNCELLENDI)
│   ├── simulator.py                # Network simülatörü (GÜNCELLENDI)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── wallet.py
│   │   ├── block.py
│   │   └── blockchain.py
│   └── network/
│       ├── __init__.py
│       ├── node.py                 # Node sınıfı (GÜNCELLENDI)
│       ├── message_broker.py       # MessageBroker (YENİ)
│       └── pbft_handler.py         # PBFT Handler (YENİ)
└── frontend/
    └── main.py                     # Streamlit UI (GÜNCELLENDI)
```

---

## Teknik Detaylar (Güncel)

### Kriptografi
- RSA 2048-bit key pairs
- SHA256 hashing
- PSS padding (imza için)

### Konsensüs
- **Validator'lar:** PBFT (Practical Byzantine Fault Tolerance)
  - 4 fazlı protokol
  - 2f+1 voting
  - View change mekanizması
- **Regular Node'lar:** Proof of Work (4 leading zeros)
- Mining reward: 50 coins

### Network
- 10 node (4 validator, 6 regular)
- MessageBroker ile asenkron mesajlaşma
- Network delay simülasyonu (0.1-0.3 saniye)
- Otomatik blok üretimi (5 saniye)
- Otomatik PBFT mesaj işleme (0.5 saniye)

### API
- FastAPI (async)
- CORS enabled
- 2 background task (production + PBFT)
- RESTful endpoints
- PBFT monitoring endpoints

### Frontend
- Streamlit
- Real-time updates (2 saniye)
- PBFT status göstergeleri
- Message traffic monitoring
- Responsive design

---

## Test Sonuçları

### MILESTONE 1 ✅
- ✅ **Core Modules:** Transaction, Wallet, Block, Blockchain - PASSED
- ✅ **Node System:** Node creation, mining, sync - PASSED
- ✅ **Simulator:** Node management, auto-production - PASSED
- ✅ **API:** All endpoints responding - PASSED
- ✅ **UI:** Frontend loads and displays data - PASSED

### MILESTONE 2 ✅
- ✅ **MessageBroker:** Messaging, broadcast, delay simulation - PASSED
- ✅ **PBFT Handler:** 4-phase protocol, view change, Byzantine scenario - PASSED
- ✅ **Node+PBFT:** Integration, propose, process messages - PASSED
- ✅ **Simulator+PBFT:** Full integration, auto-production - PASSED
- ✅ **API PBFT:** New endpoints, PBFT monitoring - PASSED
- ✅ **UI PBFT:** Status panels, message traffic, validator details - PASSED

### MILESTONE 3 ✅
- ✅ **Attack Engine:** Attack management system - PASSED
- ✅ **DDoS Attack:** DDoS implementation and effects - PASSED
- ✅ **Node Metrics:** Metrics system and tracking - PASSED
- ✅ **Attack API:** Attack endpoints working - PASSED
- ✅ **UI Attack Panel:** Attack control interface - PASSED
- ✅ **UI Metrics:** Metrics dashboard and visualization - PASSED

### MILESTONE 4 ✅
- ✅ **Byzantine Attack:** Byzantine node implementation - PASSED
- ✅ **Trust Score:** Automatic trust score system - PASSED
- ✅ **Byzantine Detection:** Fake hash detection working - PASSED
- ✅ **UI Byzantine:** Byzantine attack panel and indicators - PASSED
- ✅ **UI Trust Score:** Trust score visualization with colors - PASSED
- ✅ **UI Validator Tab:** Enhanced validator display - PASSED

---

## Sonraki Adımlar

**MILESTONE 5: Sybil Saldırısı**
- Sybil attack implementation
- Sahte node oluşturma
- Network visualizer
- Sybil node işaretleme

**MILESTONE 6+: Diğer Saldırılar**
- %51 Saldırısı
- Network Partition
- Selfish Mining

---

## MILESTONE 3: İlk Saldırı (DDoS) ✅

### 3.1 Attack Engine ✅
**Dosya:** `backend/attacks/attack_engine.py`

**Özellikler:**
- AttackType enum (DDoS, Byzantine, Sybil, Majority, Partition, Selfish Mining)
- AttackStatus enum (Idle, Active, Recovering, Completed)
- Attack class (sınıf yapısı)
- AttackEngine class (saldırı yönetimi)
- Saldırı trigger, stop, status fonksiyonları
- Saldırı geçmişi (history tracking)
- İstatistikler

**Test:** `test_attack_engine.py` - Attack engine testi PASSED

---

### 3.2 DDoS Implementation ✅
**Dosya:** `backend/attacks/ddos.py`

**Özellikler:**
- DDoSAttack sınıfı
- Intensity levels (low, medium, high)
- Response time artırımı (10x)
- Status değişimi (under_attack)
- Otomatik iyileşme (20 saniye)
- Metrik değişiklikleri (CPU, memory, latency, packet loss)

**Test:** `test_ddos.py` - DDoS attack testi PASSED

---

### 3.3 Node Metrik Sistemi ✅
**Güncelleme:** `backend/network/node.py`

**Eklenti:**
- `response_time` metriği (varsayılan: 50ms)
- `status`: "healthy" / "under_attack" / "recovering"
- `get_metrics()` metodu:
  - cpu_usage, memory_usage
  - response_time, network_latency
  - packet_loss, requests_per_second
  - errors_count, trust_score
- `set_under_attack()` - Metrik değişiklikleri
- `recover()` - İyileşme mekanizması

**Test:** `test_node_metrics.py` - Node metrikleri testi PASSED

---

### 3.4 API Saldırı Endpointleri ✅
**Güncelleme:** `backend/main.py`

**Yeni endpoint:**
- `POST /attack/trigger` - Saldırı başlat (type, target, parameters)
- `GET /attack/status` - Aktif saldırılar + geçmiş
- `GET /attack/status/{attack_id}` - Spesifik saldırı durumu
- `POST /attack/stop/{attack_id}` - Saldırıyı durdur
- `GET /metrics` - Tüm node metrikleri
- `GET /metrics/{node_id}` - Spesifik node metrikleri

**Test:** `test_api_attacks.py` - Attack API endpoint'leri PASSED

---

### 3.5 UI Attack Panel ✅
**Yeni dosya:** `frontend/components/attack_panel.py`

**Gösterim:**
- Attack type selectörü (DDoS, Byzantine, vb.)
- Target node selectörü
- Intensity slider (DDoS için)
- Trigger Attack butonu
- Active Attacks paneli:
  - Attack ID, type, status
  - Target, parameters
  - Effects list (expandable)
  - Stop butonu
- Attack History paneli:
  - Son 5 saldırı
  - Attack details, duration

**Test:** Manuel UI testi - Attack panel çalışıyor

---

### 3.6 UI Metrics Dashboard ✅
**Yeni dosya:** `frontend/components/metrics_dashboard.py`

**Gösterim:**
- Response Time grafikleri (Plotly line chart)
- Trust Score kartları (node bazında)
- Status göstergeleri (renkli kartlar):
  - Yeşil: healthy
  - Sarı: recovering
  - Kırmızı: under_attack
- Gerçek zamanlı güncelleme
- Node detail view (expandable)

**Test:** Manuel UI testi - Metrics dashboard çalışıyor

---

## ✅ MILESTONE 3 Tamamlandı
**Çıktı:** DDoS saldırısı çalışıyor, etkileri görselleştiriliyor.

---

## MILESTONE 4: Byzantine Node Saldırısı ✅

### 4.1 Byzantine Attack ✅
**Dosya:** `backend/attacks/byzantine.py`

**ByzantineAttack sınıfı:**
- `trigger(target_node_id)` - Saldırıyı başlat
- `stop()` - Saldırıyı durdur
- `get_status()` - Saldırı durumu
- `_auto_recovery()` - Otomatik iyileşme (30 saniye)

**Özellikler:**
- Hedef validator yanlış hash gönderir (64x'0')
- PBFT pre-prepare mesajında fake hash
- Diğer validator'lar tespit eder ve reddeder
- Trust score ceza: -20 (trigger), -20 (recovery)
- Node status: healthy → under_attack → recovering → healthy
- Byzantine flag set/unset

**Test:** `test_byzantine.py` - Byzantine attack PASSED

---

### 4.2 Trust Score Sistemi ✅
**Güncelleme:** `backend/network/node.py`

**Eklenti:**
- `_handle_pre_prepare()`: Byzantine detection + trust +1
  - Fake hash detection (64x'0')
  - Hash mismatch detection
  - Yanlış mesajları reddet
- `_handle_prepare()`: Trust +1 (doğru davranış)
- `_handle_commit()`: Trust +2 (consensus bonus)

**Trust Score Mekanizması:**
- Başlangıç: 100
- Doğru davranış ödülleri:
  - Pre-prepare işleme: +1
  - Prepare gönderme: +1
  - Commit gönderme: +1
  - Consensus başarı: +2 (bonus)
- Hatalı davranış cezaları:
  - Byzantine saldırı başlangıcı: -20
  - Byzantine saldırı bitişi: -20
  - Fake hash tespit: mesaj reddedilir, trust artmaz
- Range: 0-100

**Test:** `test_trust_score.py` - Trust score mekanizması PASSED

---

### 4.3 UI'ya Byzantine Göstergesi ✅
**Güncelleme:** `frontend/components/attack_panel.py`

**Eklenti:**
- Byzantine attack type seçeneği
- `trigger_byzantine_attack()` fonksiyonu
- `display_byzantine_status()` - Aktif saldırı paneli:
  - Target node bilgisi
  - Elapsed/Remaining time
  - Progress bar
  - Stop butonu
  - Target node detayları (expandable)
- `stop_byzantine_attack()` - Saldırıyı durdur

**Güncelleme:** `frontend/main.py`

**Validator Tabı Güncellemesi:**
- Trust Score Summary (average)
- Her validator için:
  - Primary badge (👑)
  - Byzantine warning (⚠️)
  - Renk kodlu trust score:
    - 🟢 Yeşil: ≥90 (Healthy)
    - 🟠 Turuncu: 70-89 (Warning)
    - 🔴 Kırmızı: <70 (Danger)
  - Status emoji (🟢🟡🔴)
  - PBFT consensus count
- Expandable details:
  - Chain length, Balance
  - Blocks mined, Response time
  - PBFT view, View changes

**Test:** `test_ui_byzantine.py` - UI test rehberi

---

## ✅ MILESTONE 4 Tamamlandı
**Çıktı:** Byzantine saldırısı çalışıyor, PBFT etkileniyor, trust score sistemi aktif.

---

## Proje Yapısı (Güncel)

```
BlockChainAgSimulasyon/
├── config.py                       # Merkezi yapılandırma
├── requirements.txt                # Bağımlılıklar
├── test_byzantine.py                # Byzantine attack test (YENİ)
├── test_trust_score.py              # Trust score test (YENİ)
├── test_ui_byzantine.py             # UI test rehberi (YENİ)
├── test_core.py                     # Core modül testleri
├── test_node.py                     # Node testleri
├── test_simulator.py                # Simulator testleri
├── test_api.py                      # API testleri
├── test_message_broker.py           # MessageBroker testleri
├── test_pbft_handler.py             # PBFT handler testleri
├── test_node_pbft.py                # Node+PBFT testleri
├── test_simulator_pbft.py           # Simulator+PBFT testleri
├── test_api_pbft.py                 # API PBFT endpoint testleri
├── test_attack_engine.py            # Attack engine testleri (YENİ)
├── test_ddos.py                     # DDoS attack testleri (YENİ)
├── test_node_metrics.py             # Node metrics testleri (YENİ)
├── test_api_attacks.py              # Attack API testleri (YENİ)
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI server (GÜNCELLENMİŞ)
│   ├── simulator.py                # Network simülatörü (GÜNCELLENMİŞ)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── wallet.py
│   │   ├── block.py
│   │   └── blockchain.py
│   ├── network/
│   │   ├── __init__.py
│   │   ├── node.py                 # Node sınıfı (GÜNCELLENMİŞ)
│   │   ├── message_broker.py       # MessageBroker
│   │   └── pbft_handler.py         # PBFT Handler
│   └── attacks/
│       ├── __init__.py             # (GÜNCELLENMİŞ)
│       ├── attack_engine.py        # Attack yönetimi (YENİ)
│       ├── ddos.py                 # DDoS attack (YENİ)
│       └── byzantine.py            # Byzantine attack (YENİ)
└── frontend/
    ├── main.py                     # Streamlit UI (GÜNCELLENMİŞ)
    └── components/
        ├── attack_panel.py         # Attack kontrol paneli (GÜNCELLENMİŞ)
        └── metrics_dashboard.py    # Metrics dashboard (YENİ)
```

---

## Teknik Detaylar (Güncel)
