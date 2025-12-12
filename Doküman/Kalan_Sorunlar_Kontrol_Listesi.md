# KALAN SORUNLAR - KONTROL LİSTESİ

Bu doküman, manuel testte karşılaşılan kalan sorunları çözmek için hazırlanmıştır.
Her sorun için:
1. Hangi dosyaya bakacağınız
2. Ne arayacağınız
3. Neye cevap vereceğiniz

belirtilmiştir.

---

## 🔴 SORUN 1: Trust Score Azalmıyor

### Kontrol 1.1 - Byzantine attack trust score düşüyor mu?

**Adımlar:**
1. Backend'i çalıştır
2. Frontend'den Byzantine attack başlat (bir validator seç)
3. Backend console'u oku

**Kontrol edeceğin:**
- "trust score" kelimesi geçiyor mu?
- "Trust score decreased" gibi bir mesaj var mı?
- Varsa hangi node için?

**Cevap:** Backend console'daki trust score ile ilgili tüm satırları kopyala.

---

### Kontrol 1.2 - API'de trust score değişiyor mu?

**Browser'da aç:**
```
http://localhost:8000/nodes
```

**Kontrol edeceğin:**
- Byzantine node'un `trust_score` değeri ne?
- 10 saniye bekle, sayfayı yenile
- Trust score azaldı mı?

**Cevap:** Byzantine node'un trust score değerini yaz (başlangıç ve 10 saniye sonra).

---

### Kontrol 1.3 - Backend'de trust score azaltma kodu var mı?

**Dosyayı aç:**
```
backend/attacks/byzantine_attack.py
```

**Ara:**
```python
trust_score
```

**Kontrol edeceğin:**
- `target_node.trust_score` değiştiren bir satır var mı?
- Varsa hangi satırda?
- Yoksa "yok" de.

**Cevap:** Kod satırını kopyala veya "yok".

---

## 🔴 SORUN 2: Byzantine Nodes Dropdown Boş

### Kontrol 2.1 - Dropdown'da ne var?

**Adımlar:**
1. Frontend'i aç
2. Attack Control Panel → Byzantine Attack
3. Target dropdown'ı aç

**Kontrol edeceğin:**
- Kaç tane seçenek var?
- Hangi node'lar görünüyor?
- node_0, node_1, node_2, node_3 görünüyor mu?

**Cevap:** Dropdown'daki tüm seçenekleri listele.

---

### Kontrol 2.2 - Validator filtering yapılıyor mu?

**Dosyayı aç:**
```
frontend-PySide6/ui/widgets/attack_panel_widget.py
```

**Ara:**
`update_node_list` metodunu bul.

**Kontrol edeceğin:**
- Byzantine attack dropdown'ı dolduran satırları bul
- `if node.get('role') == 'validator'` gibi bir filtering var mı?
- Varsa hangi satırda?

**Cevap:** Filtering kodunu kopyala veya "yok".

---

### Kontrol 2.3 - Signal bağlantısı var mı?

**Dosyayı aç:**
```
frontend-PySide6/ui/main_window.py
```

**Ara:**
`update_node_list` çağrısını bul.

**Kontrol edeceğin:**
- `data_manager.nodes_updated.connect(attack_panel.update_node_list)` gibi bir satır var mı?
- Varsa hangi satırda?

**Cevap:** Signal bağlantı satırını kopyala veya "yok".

---

## 🔴 SORUN 3: Stop Butonu Çalışmıyor

### Kontrol 3.1 - Stop butonuna tıklayınca ne oluyor?

**Adımlar:**
1. Bir attack başlat
2. Stop butonuna tıkla
3. Backend console'u oku

**Kontrol edeceğin:**
- Backend'de "Attack stopped" mesajı görüyor musun?
- Varsa tam mesaj ne?
- Yoksa hiçbir şey olmuyor mu?

**Cevap:** Backend console çıktısını kopyala.

---

### Kontrol 3.2 - Frontend console'da hata var mı?

**Adımlar:**
1. Frontend çalışırken terminal'e bak
2. Stop butonuna tıkla
3. Terminal'de bir şey değişiyor mu?

**Kontrol edeceğin:**
- Hata mesajı var mı?
- "attack_stop_requested" gibi bir log var mı?

**Cevap:** Frontend terminal çıktısını kopyala.

---

### Kontrol 3.3 - Signal-slot bağlantısı var mı?

**Dosyayı aç:**
```
frontend-PySide6/ui/main_window.py
```

**Ara:**
`attack_stop_requested`

**Kontrol edeceğin:**
- `attack_panel.attack_stop_requested.connect(...)` satırı var mı?
- `_on_attack_stop_requested` metodu var mı?
- Varsa hangi satırlarda?

**Cevap:** Her iki satırı da kopyala veya "yok".

---

### Kontrol 3.4 - API endpoint'i çalışıyor mu?

**Adımlar:**
1. Bir attack başlat ve attack_id'yi not et
2. Browser'da şunu dene:

```
POST http://localhost:8000/attack/stop
Body: {"attack_id": "attack_1"}
```

**Kontrol edeceğin:**
- Response ne?
- Backend console'da bir değişiklik oluyor mu?

**Cevap:** API response'unu kopyala.

---

## 🔴 SORUN 4: Network Health Çalışmıyor

### Kontrol 4.1 - Frontend'de health bar'ları görünüyor mu?

**Adımlar:**
1. Frontend'i aç
2. Metrics Dashboard'a bak

**Kontrol edeceğin:**
- "Network Health" başlığı görünüyor mu?
- 3 progress bar var mı? (Overall, Validators, Regular)
- Yüzde değerleri ne?

**Cevap:** 3 bar'ın yüzde değerlerini yaz.

---

### Kontrol 4.2 - DDoS saldırısında health değişiyor mu?

**Adımlar:**
1. Network health değerlerini not et
2. DDoS attack başlat
3. 10 saniye bekle
4. Health bar'lara tekrar bak

**Kontrol edeceğin:**
- Overall health azaldı mı?
- Hedef node regular ise Regular health azaldı mı?

**Cevap:** Saldırı öncesi ve sonrası health değerlerini yaz.

---

### Kontrol 4.3 - Node status API'de değişiyor mu?

**Adımlar:**
1. DDoS attack başlat (örn: node_5)
2. Browser'da aç:

```
http://localhost:8000/nodes
```

**Kontrol edeceğin:**
- node_5'in `status` field'ı ne?
- `"healthy"` mi yoksa `"under_attack"` mı?

**Cevap:** Hedef node'un status değerini yaz.

---

### Kontrol 4.4 - Frontend health calculation kodu var mı?

**Dosyayı aç:**
```
frontend-PySide6/ui/widgets/metrics_widget.py
```

**Ara:**
`update_health` metodunu bul.

**Kontrol edeceğin:**
- Bu metod içinde health hesaplaması yapılıyor mu?
- `healthy_nodes / total_nodes` gibi bir formül var mı?
- `status == "healthy"` kontrolü yapılıyor mu?

**Cevap:** Health calculation satırlarını kopyala.

---

## 🔴 SORUN 5: Network Partition Görselleştirmesi

### Kontrol 5.1 - Backend'de partition oluşuyor mu?

**Adımlar:**
1. Network Partition attack başlat
2. Backend console'u oku

**Kontrol edeceğin:**
- "Network partition" mesajı var mı?
- "Partition A" ve "Partition B" node'ları listeleniyor mu?
- Hangi node'lar hangi grupta?

**Cevap:** Console'daki partition mesajlarını kopyala.

---

### Kontrol 5.2 - API'de partition bilgisi var mı?

**Browser'da aç:**
```
http://localhost:8000/nodes
```

**Kontrol edeceğin:**
- Her node'da `partition_group` field'ı var mı?
- Değerleri ne? ("A", "B", null?)

**Cevap:** Birkaç node'un partition_group değerlerini yaz.

---

### Kontrol 5.3 - Frontend network map partition gösteriyor mu?

**Adımlar:**
1. Network Map sayfasına git
2. Partition attack başlat
3. Network map'i izle

**Kontrol edeceğin:**
- Node renkleri değişiyor mu?
- Gruplar arası çizgiler (edge'ler) kayboldu mu?
- Herhangi bir görsel değişiklik var mı?

**Cevap:** Ekran görüntüsü at veya "değişiklik yok" de.

---

### Kontrol 5.4 - Network graph update kodu var mı?

**Dosyayı aç:**
```
frontend-PySide6/ui/widgets/network_graph_widget.py
```

**Ara:**
`partition_group`

**Kontrol edeceğin:**
- Bu keyword geçiyor mu kodda?
- Node renkleri partition_group'a göre ayarlanıyor mu?

**Cevap:** İlgili kod satırını kopyala veya "yok".

---

## 🔴 SORUN 6: Blockchain'de Fork Oluşmuyor

### Kontrol 6.1 - Backend'de fork tespit ediliyor mu?

**Adımlar:**
1. Network Partition attack başlat
2. 30 saniye bekle
3. Backend console'u oku

**Kontrol edeceğin:**
- "Fork detected" mesajı var mı?
- "Two chains" gibi bir ifade geçiyor mu?

**Cevap:** Fork ile ilgili tüm console mesajlarını kopyala.

---

### Kontrol 6.2 - API'de fork bilgisi var mı?

**Browser'da aç:**
```
http://localhost:8000/blockchain/fork-status
```

**Kontrol edeceğin:**
- `has_fork` field'ı true mu?
- Fork details var mı?

**Cevap:** API response'unu kopyala.

---

### Kontrol 6.3 - Partition sırasında farklı bloklar üretiliyor mu?

**Adımlar:**
1. Partition başlat
2. Her 5 saniyede `/blockchain` endpoint'ini kontrol et
3. 30 saniye bekle

**Kontrol edeceğin:**
- Chain length artıyor mu?
- Son blokların miner'ları farklı gruplardan mı?

**Cevap:** Son 3 bloğun miner ID'lerini yaz.

---

### Kontrol 6.4 - Frontend blockchain page multi-chain gösteriyor mu?

**Adımlar:**
1. Blockchain sayfasına git
2. Partition attack sonrası bak

**Kontrol edeceğin:**
- Tek bir zincir mi görünüyor?
- Paralel iki dal var mı?
- Fork işareti var mı?

**Cevap:** Ekran görüntüsü at veya "tek zincir" de.

---

## 🔴 SORUN 7: Uzun Zincir Kazanması Görünmüyor

### Kontrol 7.1 - Partition kaldırılınca merge oluyor mu?

**Adımlar:**
1. Partition attack başlat
2. 30 saniye bekle
3. Stop butonu ile attack'i durdur
4. Backend console'u oku

**Kontrol edeceğin:**
- "Merge" mesajı var mı?
- "Longest chain" ifadesi geçiyor mu?
- Hangi chain kazandı?

**Cevap:** Console'daki merge mesajlarını kopyala.

---

### Kontrol 7.2 - API'de winning chain bilgisi var mı?

**Partition bitince browser'da aç:**
```
http://localhost:8000/blockchain
```

**Kontrol edeceğin:**
- Chain length ne?
- Önceki iki chain'den biri kayboldu mu?

**Cevap:** Merge sonrası chain length'i yaz.

---

### Kontrol 7.3 - Frontend'de merge animasyonu var mı?

**Kontrol edeceğin:**
- Blockchain page'de bir notification göründü mü?
- "Longest chain won" gibi bir mesaj var mı?
- Losing chain fade out oldu mu?

**Cevap:** Ekran görüntüsü at veya "değişiklik yok" de.

---

## 🟡 SORUN 8: Attack %100 Olunca Silinmiyor (Düşük Öncelik)

### Kontrol 8.1 - Backend cleanup çalışıyor mu?

**Adımlar:**
1. Bir attack başlat (20 saniye)
2. 25 saniye bekle
3. Backend console'u oku

**Kontrol edeceğin:**
- "Attack completed" mesajı var mı?
- "Moved to history" gibi bir ifade var mı?

**Cevap:** Console çıktısını kopyala.

---

### Kontrol 8.2 - API'de completed attack hala active mı?

**Attack süresi dolduktan sonra:**
```
http://localhost:8000/attack/status
```

**Kontrol edeceğin:**
- `active_attacks` listesinde hala var mı?
- Yoksa `recent_history`'de mi?

**Cevap:** API response'unu kopyala.

---

## 📋 ÇALIŞMA PLANI

**Her sorun için:**
1. Tüm kontrolleri yap
2. Cevapları topla
3. Bana gönder
4. Birlikte çözüm üretelim

**Hangi sorundan başlamak istersin?**

**Önerilen sıra:**
1. Trust Score (en kolay)
2. Byzantine Dropdown (kolay)
3. Stop Butonu (orta)
4. Network Health (orta)
5. Network Partition (zor)
6. Fork Görselleştirmesi (zor)
7. Uzun Zincir (zor)
8. Attack Cleanup (düşük öncelik)

---

## 🎯 NOTLAR

- Her kontrolde backend ve frontend'i restart etmeyi unutma
- API testlerini browser'da yap (Postman değil)
- Console çıktılarını tam kopyala (ilk-son 5 satır yeterli)
- Ekran görüntüleri almayı unutma (özellikle görselleştirme sorunlarında)

**Başlamak için hazır mısın?**
