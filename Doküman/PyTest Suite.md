Pytest Suite'e Dahil Edilecek Test Dosyaları
İşlem Özeti
8 dosyada 11 async test fonksiyonuna @pytest.mark.asyncio decorator'ı eklenecek.

Dosya Listesi ve Yapılacak Değişiklikler
1. tests/test_byzantine.py
Test sayısı: 1
Fonksiyon: test_byzantine_attack()
Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_byzantine_attack():
    ...

2. tests/test_ddos.py
Test sayısı: 1
Fonksiyon: test_ddos_attack()
Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_ddos_attack():
    ...

3. tests/test_node_pbft.py
Test sayısı: 2
Fonksiyonlar:

test_node_pbft_integration()
test_regular_vs_validator()

Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_node_pbft_integration():
    ...

@pytest.mark.asyncio
async def test_regular_vs_validator():
    ...

4. tests/test_selfish_mining.py
Test sayısı: 1
Fonksiyon: test_selfish_mining()
Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_selfish_mining():
    ...

5. tests/test_selfish_mining_ui.py
Test sayısı: 1
Fonksiyon: test_ui_private_chain()
Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_ui_private_chain():
    ...

6. tests/test_simulator_pbft.py
Test sayısı: 2
Fonksiyonlar:

test_simulator_pbft()
test_auto_production()

Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_simulator_pbft():
    ...

@pytest.mark.asyncio
async def test_auto_production():
    ...

7. tests/test_sybil.py
Test sayısı: 2
Fonksiyonlar:

test_sybil_attack()
test_auto_recovery()

Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_sybil_attack():
    ...

@pytest.mark.asyncio
async def test_auto_recovery():
    ...

8. tests/test_trust_score.py
Test sayısı: 1
Fonksiyon: test_trust_score()
Değişiklik:
pythonimport pytest

@pytest.mark.asyncio
async def test_trust_score():
    ...

Uygulama Adımları

Her dosyanın başına import pytest ekle (yoksa)
Her async def test_*() fonksiyonunun üstüne @pytest.mark.asyncio ekle
if __name__ == "__main__": blokları aynen kalsın (standalone çalışma için)

Beklenen Sonuç

Skipped: 11 → 0
Passed: 82 → 93
Total: 93 test