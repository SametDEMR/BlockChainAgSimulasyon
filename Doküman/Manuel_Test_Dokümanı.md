# BLOCKCHAIN ATTACK SIMULATOR - MANUEL TEST DOKUMANI

Bu doküman, uygulamanın tüm özelliklerini adım adım test etmek için hazırlanmıştır.

---

## BÖLÜM 1: TEMEL BAŞLATMA TESTİ

### 1.1 Backend Başlatma
**Komut:**
```bash
cd E:\PYTHON\BlockChainAgSimulasyon
python backend/main.py
```

**Beklenen Çıktı:**
```
✅ Initialized 10 nodes (4 validators, 6 regular)
✅ MessageBroker configured with 10 nodes
✅ All nodes share genesis block: [16 karakterlik hash]...
============================================================
🚀 Blockchain Attack Simulator API
Nodes: 10 | Validators: 4
Attack Engine: Ready
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Başarı Kriterleri:**
- [ ] 10 node oluşturuldu (4 validator + 6 regular)
- [ ] MessageBroker 10 node ile yapılandırıldı
- [ ] Tüm node'lar aynı genesis block'u paylaşıyor
- [ ] Server 8000 portunda çalışıyor

**❌ Hata Durumları:**
- `Address already in use`: 8000 portu kullanımda, başka uygulama kapat
- `ModuleNotFoundError`: requirements.txt'i yükle
- Farklı genesis hash'leri: **SORUN VAR**

---

### 1.2 Frontend Başlatma
**Komut:**
```bash
cd E:\PYTHON\BlockChainAgSimulasyon
python frontend-PySide6/main.py
```

**Beklenen Görünüm:**
- Pencere açılır: "Blockchain Attack Simulator"
- Sol üst köşede: 🟢 Connected
- Start, Stop, Reset butonları görünür
- Sol panelde: Attack Control Panel
- Sağ panelde: Metrics Dashboard
- Alt panelde: PBFT Consensus Status

**✅ Başarı Kriterleri:**
- [ ] Uygulama açılıyor
- [ ] Status bar'da "🟢 Connected" yazıyor
- [ ] Hiçbir hata popup'ı yok

---

## BÖLÜM 2: BLOCKCHAIN ÜRETİMİ TESTİ

### 2.1 Simulator'ı Başlatma
**İşlem:**
1. Frontend'de **"▶ Start"** butonuna tıkla

**Backend Console'da Beklenen:**
```
▶️  Simulator started
```

**Frontend'de Beklenen:**
- Start butonu disabled olur
- Stop butonu enabled olur
- Status bar: "Simulator started"

**✅ Başarı Kriteri:**
- [ ] Backend'de "Simulator started" logu var

---

### 2.2 İlk Blok Üretimi (5 saniye içinde)
**Bekle:** 5-10 saniye

**Backend Console'da Beklenen:**
```
Node node_0 (PRIMARY) proposed block #1
Node node_1 sent PREPARE (trust: 101)
Node node_2 sent PREPARE (trust: 101)
Node node_3 sent PREPARE (trust: 101)
Node node_1 sent COMMIT (trust: 102)
Node node_2 sent COMMIT (trust: 102)
Node node_3 sent COMMIT (trust: 102)
✅ Node node_0 added block #1 after CONSENSUS! (trust: 103)
✅ Node node_1 added block #1 after CONSENSUS! (trust: 104)
```

**✅ Başarı Kriterleri:**
- [ ] PRIMARY node blok önerdi (pre-prepare)
- [ ] Diğer validator'lar PREPARE gönderdi
- [ ] Diğer validator'lar COMMIT gönderdi
- [ ] En az 3 node "added block #1 after CONSENSUS" logu verdi
- [ ] **ÖNEMLİ:** "Invalid previous_hash" YOKSA ✅

**❌ Hata Durumları:**
- "Invalid previous_hash" x9: Genesis block sorunu, backend'i restart et
- "Insufficient balance": Normal, ilk blokta olabilir
- Hiçbir log yok: auto_block_production çalışmıyor

---

### 2.3 Blockchain Page Kontrolü
**İşlem:**
1. Frontend'de **"⛓️ Blockchain"** tabına geç

**Beklenen Görünüm:**
- Chain Length: **2 veya daha fazla** (genesis + yeni bloklar)
- Block listesi görünür
- Her blok için:
  - Index numarası
  - Hash (0000... ile başlayan)
  - Previous Hash
  - Miner ID
  - Transaction sayısı

**✅ Başarı Kriterleri:**
- [ ] Chain Length > 1 (en az 2)
- [ ] Bloklar listeleniyor
- [ ] Her 5 saniyede +1 blok ekleniyor

**❌ Hata Durumları:**
- Chain Length = 1 (sadece genesis): **SORUN VAR** → PBFT consensus çalışmıyor

---

### 2.4 Dashboard Page Kontrolü
**İşlem:**
1. Frontend'de **"📊 Dashboard"** tabına geç

**Beklenen Görünüm:**
- Total Nodes: 10
- Active Nodes: 10
- Chain Length: **2 veya daha fazla**
- Block Production Rate: değişken
- Network Health: Healthy (yeşil)

**✅ Başarı Kriterleri:**
- [ ] Chain Length artıyor
- [ ] Active Nodes = 10
- [ ] Network Health yeşil

---

## BÖLÜM 3: API ENDPOİNT TESTİ

### 3.1 Manuel API Testi
**Browser'da veya Postman'de:**

**Test 1: Status**
```
GET http://localhost:8000/status
```
**Beklenen Response:**
```json
{
  "is_running": true,
  "total_nodes": 10,
  "active_nodes": 10,
  "validator_nodes": 4,
  "regular_nodes": 6,
  "total_blocks": 2 (veya daha fazla)
}
```

**Test 2: Blockchain**
```
GET http://localhost:8000/blockchain
```
**Beklenen Response:**
```json
{
  "chain_length": 2 (veya daha fazla),
  "chain": {
    "chain_length": 2,
    "difficulty": 4,
    "chain": [
      {
        "index": 0,
        "hash": "...",
        "previous_hash": "0",
        "transactions": []
      },
      {
        "index": 1,
        "hash": "0000...",
        "previous_hash": "[genesis hash]",
        "transactions": [...]
      }
    ]
  }
}
```

**✅ Başarı Kriterleri:**
- [ ] chain_length > 1
- [ ] Block #1'in previous_hash = Block #0'ın hash'i
- [ ] Her blok en az 1 transaction içeriyor (coinbase)

**Test 3: PBFT Status**
```
GET http://localhost:8000/pbft/status
```
**Beklenen Response:**
```json
{
  "enabled": true,
  "total_validators": 4,
  "primary": "node_0",
  "current_view": 0,
  "total_consensus_reached": 1 (veya daha fazla)
}
```

**✅ Başarı Kriteri:**
- [ ] total_consensus_reached > 0 ve artıyor

---

## BÖLÜM 4: ATTACK TESTLERİ

### 4.1 DDoS Attack Testi
**İşlem:**
1. Sol panelde "🌊 DDoS Attack" seçeneğini aç
2. Target dropdown'dan bir node seç (örn: node_5)
3. Intensity slider'ı 7'ye ayarla
4. **"▶️ Trigger DDoS Attack"** butonuna tıkla

**Backend Console'da Beklenen:**
```
✅ DDoS attack started on node_5
Attack ID: attack_[uuid]
```

**Frontend'de Beklenen:**
- "⚠️ Active Attacks" sayısı (1) olur
- Attack kartı görünür:
  - Type: DDoS
  - Target: node_5
  - Progress bar animasyonu
  - Stop butonu

**Nodes Page'de Beklenen:**
- node_5'in status'ü "under_attack" olur
- Response time artar
- Trust score azalır

**✅ Başarı Kriterleri:**
- [ ] Attack başladı mesajı geldi
- [ ] Active attacks listesinde görünüyor
- [ ] Target node'un status'ü değişti

**API Kontrolü:**
```
GET http://localhost:8000/attack/status
```
**Beklenen:**
```json
{
  "active_attacks": [
    {
      "id": "attack_...",
      "type": "ddos",
      "target": "node_5",
      "status": "active"
    }
  ]
}
```

---

### 4.2 Byzantine Attack Testi
**İşlem:**
1. "⚔️ Byzantine Attack" seçeneğini aç
2. Target dropdown'dan bir **VALIDATOR** seç (node_0, node_1, node_2, veya node_3)
3. **"▶️ Trigger Byzantine Attack"** butonuna tıkla

**Backend Console'da Beklenen:**
```
🔴 Byzantine attack triggered on node_1
Node node_1 is now Byzantine!
```

**PBFT Console Loglarında Beklenen:**
```
⚠️  Node node_2 detected MISMATCH in pre-prepare from node_1
⚠️  Node node_3 detected FAKE hash from node_1
```

**✅ Başarı Kriterleri:**
- [ ] Byzantine node işaretlendi
- [ ] Diğer node'lar Byzantine davranışı tespit etti
- [ ] Trust score düştü
- [ ] Consensus hala devam ediyor (3/4 honest node yeterli)

---

### 4.3 Sybil Attack Testi
**İşlem:**
1. "👥 Sybil Attack" seçeneğini aç
2. Fake Nodes slider'ı 15'e ayarla
3. **"▶️ Trigger Sybil Attack"** butonuna tıkla

**Backend Console'da Beklenen:**
```
🔴 Sybil node created: sybil_0
🔴 Sybil node created: sybil_1
...
🔴 Sybil node created: sybil_14
✅ Sybil attack started with 15 fake nodes
```

**Dashboard'da Beklenen:**
- Total Nodes: 25 (10 + 15)
- Sybil Nodes: 15

**Nodes Page'de:**
- 15 yeni node görünür
- is_sybil: true
- trust_score: 0

**✅ Başarı Kriterleri:**
- [ ] 15 fake node oluşturuldu
- [ ] Total nodes sayısı arttı
- [ ] Fake node'lar is_sybil=true

---

### 4.4 Majority Attack (51%) Testi
**İşlem:**
1. "⚡ Majority Attack (51%)" seçeneğini aç
2. **ÖNEMLİ:** Warning mesajını oku
3. **"▶️ Trigger Majority Attack"** butonuna tıkla

**Backend Console'da Beklenen:**
```
🔴 Majority attack triggered!
🔴 Compromised validator: node_0
🔴 Compromised validator: node_1
🔴 Compromised validator: node_2
✅ 3/4 validators compromised (75%)
```

**PBFT Status'te Beklenen:**
- Consensus başarısız olmaya başlar
- Malicious block'lar önerilir
- Honest node'lar reject eder

**✅ Başarı Kriterleri:**
- [ ] En az 3 validator compromised
- [ ] Network consensus zorlaşır
- [ ] Fork riski artar

---

### 4.5 Network Partition Testi
**İşlem:**
1. "🔌 Network Partition" seçeneğini aç
2. **"▶️ Trigger Network Partition"** butonuna tıkla

**Backend Console'da Beklenen:**
```
🔴 Network partition triggered!
Partition A: node_0, node_1, node_2, node_4, node_6
Partition B: node_3, node_5, node_7, node_8, node_9
```

**Network Map'te Beklenen:**
- Node'lar iki gruba ayrılır
- Gruplar arası bağlantılar kesilir

**Blockchain'de Beklenen:**
- İki grup farklı chain'ler oluşturur
- Fork oluşur

**✅ Başarı Kriterleri:**
- [ ] Network 2'ye bölündü
- [ ] Gruplar arası mesajlaşma yok
- [ ] Fork detected

---

### 4.6 Selfish Mining Testi
**İşlem:**
1. "💎 Selfish Mining" seçeneğini aç
2. Attacker dropdown'dan bir node seç
3. **"▶️ Trigger Selfish Mining"** butonuna tıkla

**Backend Console'da Beklenen:**
```
🟠 Node node_7 started SELFISH MINING
Private chain created
Node node_7 mining on private chain...
Node node_7 mined private block #2
🔴 Node node_7 REVEALED private chain (4 blocks > 3 public blocks)
```

**✅ Başarı Kriterleri:**
- [ ] Private chain oluşturuldu
- [ ] Attacker private chain'de mine ediyor
- [ ] Reveal edildiğinde uzun chain kazanır

---

## BÖLÜM 5: SORUN GİDERME TABLOSU

| Semptom | Neden | Çözüm |
|---------|-------|-------|
| Chain length = 1 kalıyor | Consensus çalışmıyor | Backend console'u kontrol et, "added block after CONSENSUS" logu var mı? |
| "Invalid previous_hash" x9 | Genesis farklı | Backend'i restart et, "All nodes share genesis" mesajını kontrol et |
| Attack trigger 422 error | API payload hatası | api_client.py düzeltildi, frontend'i restart et |
| Transaction insufficient balance | Normal | İlk blokta beklenen durum, mine reward birikince düzelir |
| No PBFT logs | Background task çalışmıyor | START butonuna bastın mı? Backend console'da "Simulator started" var mı? |
| Primary node blok önermiyor | Node active değil | /status endpoint'inden active_nodes kontrolü |
| Fork detected ama çözülmüyor | Longest chain rule | Normal davranış, en uzun chain kazanır |
| Frontend "Disconnected" | Backend çalışmıyor | Backend başlat, port kontrolü |
| Sybil nodes görünmüyor | Nodes listesi güncellenmiyor | /nodes endpoint'inden manuel kontrol |

---

## BÖLÜM 6: BAŞARILI TEST CHECKLIST

### Temel Fonksiyonalite
- [ ] Backend başarıyla başlıyor
- [ ] Frontend backend'e bağlanıyor
- [ ] Genesis block tüm node'larda aynı
- [ ] START butonu çalışıyor

### Blockchain Üretimi
- [ ] Primary validator blok öneriyor
- [ ] PBFT consensus sağlanıyor
- [ ] Bloklar zincire ekleniyor
- [ ] Chain length artıyor (her 5 saniyede +1)
- [ ] Transaction'lar oluşturuluyor

### UI Display
- [ ] Dashboard chain length gösteriyor
- [ ] Blockchain page blokları listliyor
- [ ] Nodes page node'ları gösteriyor
- [ ] PBFT widget consensus sayısını gösteriyor
- [ ] Metrics gerçek zamanlı güncelleniyor

### Attack Functionality
- [ ] DDoS attack başlatılabiliyor
- [ ] Byzantine attack çalışıyor
- [ ] Sybil attack fake node'lar ekliyor
- [ ] Majority attack validator'ları compromise ediyor
- [ ] Network partition network'ü bölebiliyor
- [ ] Selfish mining private chain oluşturuyor

### API Endpoints
- [ ] /status doğru veri dönüyor
- [ ] /blockchain chain_length > 1
- [ ] /pbft/status consensus sayısı artıyor
- [ ] /nodes tüm node'ları listliyor
- [ ] /attack/status active attack'leri gösteriyor

---

## BÖLÜM 7: PERFORMANS BENCHMARKLARı

### Normal Koşullarda (Attack yok)
- **Block Time:** ~5 saniye
- **PBFT Consensus:** 3 faz (pre-prepare, prepare, commit)
- **Transaction per Block:** 1-4 (coinbase + random txs)
- **Network Latency:** 10-50 ms
- **Trust Score:** 100

### Attack Altında
- **DDoS:** Response time 10x artar, packet loss %30
- **Byzantine:** Trust score 0'a düşer, consensus hala sağlanır
- **Sybil:** Total nodes 2x-3x artar
- **Majority:** Consensus %50+ başarısızlık
- **Partition:** 2 farklı chain, eventual fork
- **Selfish Mining:** Private chain 1-2 blok önde

---

## NOTLAR

1. **İlk 5-10 saniye:** Node'ların balance'ı 0, "insufficient balance" normal
2. **Mining reward:** Her blok için ~10 coin, balance birikir
3. **Transaction başlangıcı:** Balance > 0 olduktan sonra node'lar arası transfer başlar
4. **Genesis block:** Tüm node'larda aynı olmalı, farklıysa **backend restart gerekli**
5. **PBFT quorum:** 2f+1 = 3 honest validator yeterli (4 validatordan)
6. **Fork resolution:** En uzun chain kazanır (longest chain rule)

---

## HIZLI TEST KOMUTLARı

```bash
# Backend başlat
cd E:\PYTHON\BlockChainAgSimulasyon
python backend/main.py

# Frontend başlat (başka terminal)
python frontend-PySide6/main.py

# API test
curl http://localhost:8000/status
curl http://localhost:8000/blockchain
curl http://localhost:8000/pbft/status

# Test scripti
python test_blockchain_growth.py
```

---

**Hazırlayan:** Claude  
**Tarih:** 2024  
**Versiyon:** 1.0