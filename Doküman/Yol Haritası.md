# 🗺️ INTERACTIVE BLOCKCHAIN ATTACK SIMULATOR - YOL HARİTASI

## 📋 MILESTONE 1: Minimal Çalışan Sistem
**Amaç:** Basit blockchain + API + UI çalışır durumda

### 1.1 Temel Altyapı
**Dosya:** `config.py`

```python
CONFIG = {
    'network': {
        'total_nodes': 10,
        'validator_nodes': 4
    },
    'blockchain': {
        'block_time': 5,
        'initial_difficulty': 4
    },
    'api': {
        'host': '0.0.0.0',
        'port': 8000
    },
    'ui': {
        'refresh_interval': 2
    }
}
```

**Test:** Config değerleri okunabiliyor mu?

---

### 1.2 Blockchain Core
**Dosyalar:**
- `backend/core/transaction.py`
- `backend/core/block.py`
- `backend/core/blockchain.py`
- `backend/core/wallet.py`

**Transaction sınıfı:**
- Özellikler: sender, receiver, amount, timestamp, signature
- Metodlar: `sign()`, `verify()`

**Block sınıfı:**
- Özellikler: index, timestamp, transactions[], previous_hash, hash, nonce
- Metodlar: `calculate_hash()`, `mine_block()`

**Blockchain sınıfı:**
- Özellikler: chain[], pending_transactions[]
- Metodlar: `add_block()`, `is_valid()`, `get_latest_block()`

**Wallet sınıfı:**
- Özellikler: private_key, public_key, balance
- Metodlar: `generate_keys()`, `sign_transaction()`

**Test:** Genesis block oluşur mu? Transaction eklenip blok üretilebiliyor mu?

---

### 1.3 Basit Node Yapısı
**Dosya:** `backend/network/node.py`

**Node sınıfı:**
- Özellikler: id, role ("validator"/"regular"), blockchain, status
- Metodlar: `create_transaction()`, `mine_block()`

**Test:** Node oluşturuluyor mu? Blockchain'e blok ekleyebiliyor mu?

---

### 1.4 Simulator
**Dosya:** `backend/simulator.py`

**Simulator sınıfı:**
- Özellikler: nodes[], config
- Metodlar: `initialize_nodes()`, `start()`, `stop()`, `get_status()`

Asyncio ile otomatik blok üretimi:
```python
async def auto_block_production():
    while running:
        await asyncio.sleep(config.block_time)
        random_node.mine_block()
```

**Test:** 10 node başlatılıyor mu? Otomatik blok üretiliyor mu?

---

### 1.5 Minimal API
**Dosya:** `backend/main.py`

**Endpoints:**
- `GET /` - Health check
- `GET /status` - Sistem durumu (node sayısı, zincir uzunluğu)
- `GET /blockchain` - Tüm zincir
- `POST /start` - Simülasyonu başlat
- `POST /stop` - Simülasyonu durdur

**Test:** API çalışıyor mu? Status bilgisi geliyor mu?

---

### 1.6 Minimal Streamlit UI
**Dosya:** `frontend/main.py`

**Gösterim:**
- Sistem durumu (çalışıyor/durdu)
- Toplam node sayısı
- Zincir uzunluğu
- Başlat/Durdur butonları

**Test:** UI açılıyor mu? Backend'e bağlanıyor mu?

---

## ✅ MILESTONE 1 Tamamlandı
**Çıktı:** Basit blockchain çalışıyor, node'lar blok üretiyor, UI'dan izlenebiliyor.

---

## 📋 MILESTONE 2: PBFT Consensus

### 2.1 Message Broker
**Dosya:** `backend/network/message_broker.py`

**MessageBroker sınıfı:**
- Özellikler: message_queue[]
- Metodlar: `send_message()`, `broadcast()`, `get_messages_for_node()`
- Network delay simülasyonu ekle

**Test:** Mesajlar iletiliyor mu? Gecikme çalışıyor mu?

---

### 2.2 PBFT Handler
**Dosya:** `backend/network/pbft_handler.py`

**PBFTHandler sınıfı:**
- Özellikler: state, view, sequence_number
- Metodlar: `pre_prepare()`, `prepare()`, `commit()`, `validate_block()`
- 4 aşamalı PBFT protokolü

**Test:** Validator node'lar consensus yapabiliyor mu?

---

### 2.3 Node'a PBFT Entegrasyonu
**Güncelleme:** `backend/network/node.py`

- Node'a `pbft: PBFTHandler` ekle
- `role == "validator"` ise PBFT çalıştır
- MessageBroker ile iletişim

**Test:** Validator'lar blok onaylıyor mu? Regular node'lar bekliyor mu?

---

### 2.4 Simulator'a PBFT
**Güncelleme:** `backend/simulator.py`

- MessageBroker başlat
- Validator node'larda PBFT aktif et
- Otomatik blok üretimi → PBFT ile onay

**Test:** Bloklar PBFT ile onaylanıyor mu?

---

### 2.5 API Genişletme
**Güncelleme:** `backend/main.py`

**Yeni endpoint:**
- `GET /network/nodes` - Tüm node detayları
- `GET /network/messages` - PBFT mesaj trafiği

**Test:** PBFT mesajları görülebiliyor mu?

---

### 2.6 UI'ya PBFT Göstergesi
**Güncelleme:** `frontend/main.py`

**Eklenti:**
- Validator listesi
- PBFT mesaj sayısı
- Consensus durumu

**Test:** PBFT çalıştığı görülüyor mu?

---

## ✅ MILESTONE 2 Tamamlandı
**Çıktı:** PBFT consensus çalışıyor, validator'lar blok onaylıyor.

---

## 📋 MILESTONE 3: İlk Saldırı (DDoS)

### 3.1 Attack Engine
**Dosya:** `backend/attacks/attack_engine.py`

**AttackEngine sınıfı:**
- Özellikler: active_attacks[]
- Metodlar: `trigger_attack()`, `stop_attack()`, `get_attack_status()`

**Test:** Saldırı tetiklenebiliyor mu?

---

### 3.2 DDoS Implementation
**Dosya:** `backend/attacks/ddos.py`

**DDoSAttack sınıfı:**
- Hedef node'a yoğun istek gönder
- Response time'ı artır
- Status'u "under_attack" yap
- 20 saniye sonra otomatik iyileşme

**Test:** Node yavaşlıyor mu? Metrikler değişiyor mu?

---

### 3.3 Node Metrik Sistemi
**Güncelleme:** `backend/network/node.py`

**Eklenti:**
- `response_time` metriği
- `status`: "healthy" / "under_attack" / "recovering"
- `get_metrics()` metodu

**Test:** Metrikler güncelleniyor mu?

---

### 3.4 API Saldırı Endpointleri
**Güncelleme:** `backend/main.py`

**Yeni endpoint:**
- `POST /attack/trigger` - Saldırı başlat
- `GET /attack/status` - Aktif saldırılar
- `GET /metrics` - Tüm node metrikleri

**Test:** Saldırı tetiklenebiliyor mu?

---

### 3.5 UI Attack Panel
**Yeni dosya:** `frontend/components/attack_panel.py`

**Gösterim:**
- DDoS butonu
- Hedef node seçimi
- Saldırı durumu göstergesi

**Test:** Butonla saldırı başlatılabiliyor mu?

---

### 3.6 UI Metrics Dashboard
**Yeni dosya:** `frontend/components/metrics_dashboard.py`

**Gösterim:**
- Response time grafikleri (Plotly)
- Node status'leri (renkli kartlar)
- Gerçek zamanlı güncelleme

**Test:** Saldırı sırasında metrikler değişiyor mu?

---

## ✅ MILESTONE 3 Tamamlandı
**Çıktı:** DDoS saldırısı çalışıyor, etkileri görselleştiriliyor.

---

## 📋 MILESTONE 4: Byzantine Node Saldırısı

### 4.1 Byzantine Attack
**Dosya:** `backend/attacks/byzantine.py`

**ByzantineAttack sınıfı:**
- Hedef validator yanlış hash gönderir
- PBFT'de prepare aşamasında hatalı blok öner
- View change tetiklenir
- Validator trust_score düşer

**Test:** Validator hatalı davranıyor mu? View change oluyor mu?

---

### 4.2 Trust Score Sistemi
**Güncelleme:** `backend/network/node.py`

**Eklenti:**
- `trust_score` metriği (başlangıç: 100)
- Hatalı davranışta -10
- Doğru davranışta +1

**Test:** Byzantine node'un trust_score'u düşüyor mu?

---

### 4.3 UI'ya Byzantine Göstergesi
**Güncelleme:** `frontend/components/attack_panel.py` ve `metrics_dashboard.py`

**Eklenti:**
- Byzantine butonu
- Validator seçimi
- Trust score göstergesi
- View change animasyonu

**Test:** Byzantine saldırı görselleşiyor mu?

---

## ✅ MILESTONE 4 Tamamlandı
**Çıktı:** Byzantine saldırısı çalışıyor, PBFT etkileniyor.

---

## 📋 MILESTONE 5: Sybil Saldırısı

### 5.1 Sybil Attack
**Dosya:** `backend/attacks/sybil.py`

**SybilAttack sınıfı:**
- Çok sayıda sahte node ekle (20-30)
- Sahte node'lar `is_sybil=True` flag'i taşır
- Ağ topolojisini bozar

**Test:** Sahte node'lar ekleniyor mu?

---

### 5.2 Network Visualizer
**Yeni dosya:** `frontend/components/network_visualizer.py`

**Gösterim:**
- streamlit-agraph kullan
- Node'ları göster (normal=yeşil, validator=mavi, sybil=kırmızı)
- Bağlantıları çiz
- Interactive zoom/pan

**Test:** Ağ haritası görünüyor mu? Sybil node'lar işaretli mi?

---

### 5.3 UI Ana Sayfaya Network Map
**Güncelleme:** `frontend/main.py`

**Eklenti:**
- Network visualizer component'i ekle
- Gerçek zamanlı güncelleme

**Test:** Sybil saldırı sırasında kırmızı node'lar görünüyor mu?

---

## ✅ MILESTONE 5 Tamamlandı
**Çıktı:** Sybil saldırısı çalışıyor, ağ haritasında görünüyor.

---

## 📋 MILESTONE 6: %51 Saldırısı

### 6.1 Majority Attack
**Dosya:** `backend/attacks/majority_attack.py`

**MajorityAttack sınıfı:**
- Validator'ların %51'ini saldırgan yap
- Saldırgan grup kendi bloklarını onaylar
- Çift harcama simüle et
- Zincir çatallanması

**Test:** Saldırgan grup kontrol ediyor mu?

---

### 6.2 Chain Fork Handling
**Güncelleme:** `backend/core/blockchain.py`

**Eklenti:**
- `fork_detected` flag'i
- `resolve_fork()` - en uzun zincir kazanır
- Fork history kaydet

**Test:** Fork tespit ediliyor mu? Çözülüyor mu?

---

### 6.3 Blockchain Visualizer
**Yeni dosya:** `frontend/components/blockchain_visualizer.py`

**Gösterim:**
- Tüm blokları kartlar halinde göster
- Normal blok = yeşil
- Saldırıya uğramış = kırmızı
- Fork = paralel dal göster

**Test:** Zincir ve fork görünüyor mu?

---

### 6.4 UI'ya Blockchain View
**Güncelleme:** `frontend/main.py`

**Eklenti:**
- Blockchain visualizer component
- Scroll edilebilir zincir
- Fork indicator

**Test:** %51 saldırı sırasında fork görünüyor mu?

---

## ✅ MILESTONE 6 Tamamlandı
**Çıktı:** %51 saldırısı çalışıyor, fork görselleşiyor.

---

## 📋 MILESTONE 7: Network Partition

### 7.1 Partition Attack
**Dosya:** `backend/attacks/network_partition.py`

**NetworkPartition sınıfı:**
- Ağı ikiye böl (Grup A ve Grup B)
- MessageBroker'da partition simüle et
- İki grup birbirini göremiyor
- Paralel zincir oluşur

**Test:** İki grup bağımsız çalışıyor mu?

---

### 7.2 Partition Resolution
**Güncelleme:** `backend/attacks/network_partition.py`

**Eklenti:**
- Partition kaldırıldığında merge
- En uzun zincir kazanır
- Kısa zincir orphan olur

**Test:** Merge sonrası tek zincir mi kalıyor?

---

### 7.3 UI Partition Göstergesi
**Güncelleme:** `frontend/components/network_visualizer.py`

**Eklenti:**
- Partition çizgisi göster
- İki grubu renkle ayır
- Merge animasyonu

**Test:** Partition görsel olarak anlaşılıyor mu?

---

## ✅ MILESTONE 7 Tamamlandı
**Çıktı:** Network partition çalışıyor, merge görselleşiyor.

---

## 📋 MILESTONE 8: Selfish Mining

### 8.1 Selfish Mining Attack
**Dosya:** `backend/attacks/selfish_mining.py`

**SelfishMining sınıfı:**
- Saldırgan node private chain tutar
- Public chain'den 2+ blok ileride olunca yayınla
- Public chain geçersiz olur
- Saldırgan kazanç elde eder

**Test:** Private chain tutulabiliyor mu? Yayınlanıyor mu?

---

### 8.2 Private Chain Tracking
**Güncelleme:** `backend/network/node.py`

**Eklenti:**
- `private_chain[]` - selfish miner için
- `reveal_private_chain()` metodu

**Test:** Private chain public'ten uzun mu?

---

### 8.3 UI Private Chain View
**Güncelleme:** `frontend/components/blockchain_visualizer.py`

**Eklenti:**
- Private chain = turuncu renk
- Public chain = yeşil
- Reveal anında animasyon

**Test:** İki zincir ayrı görünüyor mu?

---

## ✅ MILESTONE 8 Tamamlandı
**Çıktı:** Selfish mining çalışıyor, private chain görselleşiyor.

---

## 📋 MILESTONE 9: Test ve İyileştirme

### 9.1 Unit Testler
**Dosyalar:** `tests/test_*.py`

- `test_blockchain.py` - Core blockchain testleri
- `test_node.py` - Node davranış testleri
- `test_pbft.py` - PBFT consensus testleri
- Her saldırı için test

**Test:** Tüm testler geçiyor mu?

---

### 9.2 Integration Testler
**Dosya:** `tests/test_integration.py`

- Tam sistem simülasyonu
- Her saldırı senaryosu test
- Otomatik iyileşme kontrol

**Test:** Entegrasyon testleri geçiyor mu?

---

### 9.3 Logging Sistemi (Opsiyonel)
**Dosya:** `backend/utils/logger.py`

- Kritik olayları logla
- Saldırı tetikleme
- Consensus değişimleri
- UI'da log viewer

**Test:** Loglar okunabilir mi?

---

### 9.4 Performans İyileştirme
- Asyncio optimizasyonu
- MessageBroker queue yönetimi
- UI yenileme frekansı ayarı

**Test:** 100 node ile çalışıyor mu?

---

### 9.5 UI Polish
- Renk şeması
- Animasyon iyileştirme
- Tooltip'ler
- Help dokümantasyonu

**Test:** Kullanıcı dostu mu?

---

## ✅ MILESTONE 9 Tamamlandı
**Çıktı:** Tüm sistem stabil, test edilmiş, optimize.

---

## 🎉 PROJE TAMAMLANDI

**Teslim Edilebilir:**
- ✅ 10 node'lu blockchain ağı
- ✅ PBFT consensus
- ✅ 6 saldırı senaryosu
- ✅ Gerçek zamanlı görselleştirme
- ✅ Interactive kontrol paneli
- ✅ Otomatik iyileşme
- ✅ Test suite
- ✅ Config-driven yapı

---

## 📝 TASARIM KARARLARI

### Mimari Kararlar
- **Modül Yapısı:** Blockchain ayrı modül (Opsiyon A) - değiştirilmesi kolay
- **PBFT Konumu:** Her node kendi PBFT mantığı (Opsiyon 2) - gerçekçi simülasyon
- **API İletişim:** REST API (WebSocket değil) - basit ve yeterli
- **Node İletişim:** Merkezi MessageBroker (Opsiyon A) - ağ gecikmesi simüle edilebilir
- **Config Format:** Python dict - esnek
- **UI Framework:** Streamlit + Plotly + streamlit-agraph
- **Blok Üretimi:** Asyncio task - FastAPI uyumlu

### Davranış Kararları
- **Veri Kalıcılığı:** Yok - RAM'de geçici
- **Saldırı Sırası:** Basitten zora (DDoS → Selfish Mining)
- **İyileşme:** Otomatik - saldırı etkisi görüldükten sonra
- **Byzantine:** Yanlış hash gönder
- **Network Partition:** En uzun zincir kazanır
- **Node Çökmesi:** Yok sayılır, diğerleri devam
- **Test Stratejisi:** Unit + Integration testler

### UI Kararları
- **Network Map:** streamlit-agraph (interactive)
- **Blockchain View:** HTML/CSS kartlar
- **Grafikler:** Plotly (interaktif)
- **UI Modülerliği:** Component bazlı - değiştirilebilir

---

## 🚀 BAŞLANGIÇ KOMUTU

```bash
# Backend
cd backend
python main_old_1.py

# Frontend (ayrı terminal)
cd frontend-streamlit
streamlit run main_old_1.py
```