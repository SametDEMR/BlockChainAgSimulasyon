# KALAN SORUNLAR - KONTROL LİSTESİ

Bu doküman, manuel testte karşılaşılan kalan sorunları çözmek için hazırlanmıştır.
Her sorun için:
1. Hangi dosyaya bakacağınız
2. Ne arayacağınız
3. Neye cevap vereceğiniz

belirtilmiştir.
------

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
