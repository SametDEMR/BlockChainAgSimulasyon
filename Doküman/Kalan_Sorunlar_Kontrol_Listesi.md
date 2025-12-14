# KALAN SORUNLAR - KONTROL LİSTESİ

Bu doküman, manuel testte karşılaşılan kalan sorunları çözmek için hazırlanmıştır.
Her sorun için:
1. Hangi dosyaya bakacağınız
2. Ne arayacağınız
3. Neye cevap vereceğiniz

belirtilmiştir.

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
-----

optimizasyon ile ilgili bazı problemler var bunlar kontrol edilecek. Düzenlemeler yapılacak.
Zİncir uzunluğunun 2den 9a 9dan 16ya anında fırlaması gibi.
BAckend konsol çıktıları azaltılabilir.
PBFT mesaj çıktısı hala gözükmüyor.