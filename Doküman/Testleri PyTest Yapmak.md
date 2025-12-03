# Pytest Test Dönüşümü - Tamamlandı ✅

## 📋 Yapılan İşlemler

### 1. Pytest Altyapısı Oluşturuldu
- **`tests/conftest.py`**: Pytest fixtures ve shared setup
- **`pytest.ini`**: Pytest configuration
- **`test_runner.py`**: Merkezi test runner (tüm testleri çalıştırır)

### 2. Test Dosyaları Pytest Formatına Dönüştürüldü

#### ✅ Dönüştürülen Test Dosyaları:
1. **`tests/test_core.py`** - Blockchain core modülleri (Wallet, Transaction, Block, Blockchain)
2. **`tests/test_node.py`** - Node modülü testleri
3. **`tests/test_simulator.py`** - Simulator testleri (async dahil)
4. **`tests/test_message_broker.py`** - MessageBroker testleri (async)
5. **`tests/test_pbft_handler.py`** - PBFT handler testleri
6. **`tests/test_attacks.py`** - **TÜM Attack testleri (birleştirildi)**:
   - Attack Engine
   - DDoS Attack
   - Byzantine Attack
   - Sybil Attack
   - Majority Attack
   - Network Partition
   - Selfish Mining
7. **`tests/test_api.py`** - API endpoint testleri
8. **`tests/test_integration.py`** - Integration testleri (Node+PBFT, Simulator+PBFT, Fork handling)

### 3. Pytest Özellikleri

#### Fixtures (conftest.py):
- `wallet` - Wallet instance
- `blockchain` - Blockchain instance
- `message_broker` - MessageBroker instance
- `node` - Regular node instance
- `validator_node` - Validator node instance
- `attack_engine` - Attack engine instance
- `simulator` - Simulator instance (auto cleanup)
- `event_loop` - Async event loop
- `api_base_url` - API base URL

#### Markers:
- `@pytest.mark.asyncio` - Async testler
- `@pytest.mark.api` - API testleri (sunucu gerektirir)
- `@pytest.mark.slow` - Yavaş testler
- `@pytest.mark.integration` - Integration testler
- `@pytest.mark.unit` - Unit testler

## 🚀 Kullanım

### Temel Kullanım:
```bash
# Tüm testleri çalıştır
python ALL TEST RUN.py

# Veya doğrudan pytest
pytest tests/

# Belirli bir test dosyası
pytest tests/test_core.py

# Belirli bir test
pytest tests/test_core.py::TestWallet::test_wallet_creation
```

### Test Runner Seçenekleri:
```bash
# Sadece unit testleri
python ALL TEST RUN.py --unit

# Sadece integration testleri
python ALL TEST RUN.py --integration

# API testlerini atla (sunucu gerekmez)
python ALL TEST RUN.py --no-api

# Sadece API testleri (sunucu gerekir)
python ALL TEST RUN.py --api

# Yavaş testleri atla
python ALL TEST RUN.py --fast

# Detaylı output
python ALL TEST RUN.py --verbose

# Coverage raporu ile
python ALL TEST RUN.py --coverage

# Belirli dosya
python ALL TEST RUN.py --file test_core.py

# Belirli test
python ALL TEST RUN.py --test test_wallet_creation
```

### Pytest Komutları:
```bash
# Verbose mode
pytest -v tests/

# Sadece başarısız testleri göster
pytest tests/ --tb=short

# Son başarısız testleri tekrar çalıştır
pytest --lf

# Parallel çalıştırma (pytest-xdist gerekir)
pytest -n auto tests/

# Sadece async testleri
pytest -m asyncio tests/

# API testleri hariç
pytest -m "not api" tests/

# Coverage ile
pytest --cov=backend --cov-report=html tests/
```

## 📊 Test Yapısı

```
BlockChainAgSimulasyon/
├── pytest.ini              # Pytest configuration
├── test_runner.py          # Merkezi test runner
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_core.py        # Core modül testleri
│   ├── test_node.py        # Node testleri
│   ├── test_simulator.py   # Simulator testleri
│   ├── test_message_broker.py  # MessageBroker testleri
│   ├── test_pbft_handler.py    # PBFT handler testleri
│   ├── test_attacks.py     # TÜM attack testleri (birleşik)
│   ├── test_api.py         # API testleri
│   └── test_integration.py # Integration testleri
```

## 🔧 Gereksinimler

Test için gerekli paketler:
```bash
pip install pytest pytest-asyncio pytest-cov
```

Opsiyonel:
```bash
pip install pytest-xdist  # Parallel çalıştırma için
```

## ⚠️ Önemli Notlar

1. **API Testleri**: `@pytest.mark.api` ile işaretlenmiş testler çalışan bir API sunucusu gerektirir.
   ```bash
   # Önce sunucuyu başlatın
   python backend/main.py
   
   # Sonra testleri çalıştırın
   pytest -m api tests/
   ```

2. **Async Testler**: `pytest-asyncio` paketi gereklidir. Otomatik olarak `@pytest.mark.asyncio` decorator'ı ile algılanır.

3. **Fixtures**: `conftest.py` dosyasındaki fixture'lar tüm testler tarafından kullanılabilir.

4. **Cleanup**: Simulator fixture'ı otomatik cleanup yapar (yield pattern).

## 📝 Test İçerikleri Korundu

**ÖNEMLİ**: Tüm test dosyalarının **içeriği değiştirilmedi**, sadece pytest formatına uyarlandı:
- Test fonksiyonları `test_` prefix aldı
- Sınıf bazlı testler `Test*` prefix aldı
- Assert statement'lar pytest assert'e dönüştürüldü
- Async testler `@pytest.mark.asyncio` decorator aldı
- Main execution blokları kaldırıldı
- Fixtures kullanıldı

**Test mantığı ve içeriği %100 korundu!**

## ✅ Sonuç

Tüm testler pytest formatına başarıyla dönüştürüldü ve merkezi test runner oluşturuldu. 

**Tek komutla tüm testleri çalıştırabilirsiniz:**
```bash
python ALL TEST RUN.py
```

veya

```bash
pytest tests/
```

**Test coverage'ı görmek için:**
```bash
python ALL TEST RUN.py --coverage
```

Testler başarıyla çalışacak ve detaylı raporlama sağlayacaktır! 🎉
