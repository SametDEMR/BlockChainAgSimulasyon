python backend/main.py
```
- Ekranda "Node node_0 sent PREPARE" gibi mesajlar görüyor musun?
- "✅ Node added block after CONSENSUS" mesajları var mı?
- Bana bir screenshot at veya mesajları kopyala.

**Kontrol 1.2 - Browser'da API'yi test et:**
```
http://localhost:8000/pbft/status
```
- `"total_consensus_reached"` değeri 0'dan farklı mı?
- Bu sayı her 5 saniyede artıyor mu? (sayfayı yenile yenile bak)
- Sonucu bana yaz.

---

### **SORUN 2: "total_consensus_reached: 0 olarak gözüküyor"**

**Kontrol 2.1 - Backend klasöründe şu dosyayı aç:**
```
backend/network/pbft_handler.py
```
- Dosyada `total_consensus_reached` diye bir değişken var mı?
- Bu değişkenin artırıldığı satırı bulabildin mi? (örnek: `self.total_consensus_reached += 1`)
- Varsa hangi satırda? Yoksa "yok" diye söyle.

**Kontrol 2.2 - Backend'de şu dosyayı aç:**
```
backend/main.py
```
- `/pbft/status` endpoint'ini bul
- Response'da `total_consensus_reached` field'ı döndürülüyor mu?
- Döndürülüyorsa hangi satırda? Kodun ekran görüntüsünü at.

---

### **SORUN 3: "İlerleme yüzdesinde değişiklik olmuyor"**

**Kontrol 3.1 - Frontend'de attack başlat, sonra API'yi kontrol et:**
1. Frontend'i aç, bir DDoS saldırısı başlat
2. Browser'da şu URL'yi aç:
```
http://localhost:8000/attack/status
```
3. Response'da şunlar var mı:
   - `"progress"` field'ı?
   - `"elapsed"` veya `"remaining"` field'ı?
   - Varsa değerleri ne? Screenshot at.

**Kontrol 3.2 - Frontend'de bu dosyayı aç:**
```
frontend-PySide6/ui/widgets/attack_panel_widget.py
```
- `update_active_attack` diye bir metod var mı?
- Bu metod progress bar'ı güncelliyor mu?
- Metodu bulup bana göster (satır numarası yeterli).

---

### **SORUN 4: "Trust score azalmıyor"**

**Kontrol 4.1 - Byzantine saldırı başlat, sonra:**
1. Backend console'da "trust score" yazan satırlar var mı?
2. Browser'da şu URL'yi aç:
```
http://localhost:8000/nodes
```
3. Byzantine olan node'un `trust_score` değeri ne?
4. 10 saniye bekle, tekrar yenile. Değişti mi?
5. Sonucu bana yaz.

**Kontrol 4.2 - Frontend'de Nodes sayfasına bak:**
- Byzantine node'un trust score'u görünüyor mu?
- Sayı değişiyor mu? (Backend'de değişiyorsa ama frontend'de değişmiyorsa, güncelleme sorunu var demektir)

---

### **SORUN 5: "Active attacks kısmındaki stop butonu çalışmıyor"**

**Kontrol 5.1 - Stop butonuna tıkla ve backend console'u izle:**
1. Bir saldırı başlat
2. "Stop" butonuna tıkla
3. Backend console'da "Attack stopped" gibi bir mesaj görüyor musun?
4. Gördüysen mesajı yaz, görmediysen "görmedim" de.

**Kontrol 5.2 - Frontend console'u kontrol et:**
- Frontend çalışırken, terminal'de hata mesajı var mı?
- Stop butonuna tıklayınca terminalde bir şey yazdırıyor mu?
- Varsa screenshot at.

**Kontrol 5.3 - Bu dosyayı aç:**
```
frontend-PySide6/ui/main_window.py
```
- `_on_attack_stop_requested` diye bir metod bul
- İçinde `api_client.stop_attack` çağrısı var mı?
- Varsa hangi satırda? Kodu göster.

---

### **SORUN 6: "Byzantine nodes dropdown'da bir şey gözükmüyor"**

**Kontrol 6.1 - Frontend'i aç:**
1. Attack Control Panel → Byzantine Attack section
2. Target dropdown'ı aç
3. İçinde kaç tane seçenek var?
4. Validator node'ların ID'lerini görüyor musun? (node_0, node_1, node_2, node_3)

**Kontrol 6.2 - Backend'den node listesini kontrol et:**
```
http://localhost:8000/nodes
```
- Response'da her node için `"role"` field'ı var mı?
- Validator node'larda `"role": "validator"` yazıyor mu?
- Screenshot at.

**Kontrol 6.3 - Bu dosyayı aç:**
```
frontend-PySide6/ui/widgets/attack_panel_widget.py
```
- `update_node_list` metodunu bul
- Byzantine attack dropdown'ı dolduran satırları bul
- Validator filtering yapılıyor mu? (örnek: `if node.get('role') == 'validator'`)
- Kodu göster.

---

### **SORUN 7: "Network map'te partition gözükmüyor"**

**Kontrol 7.1 - Partition saldırısı başlat, sonra:**
1. Backend console'da "Network partition" mesajı var mı?
2. Network Map sayfasına git
3. Node'lar arasındaki çizgiler (edge'ler) değişti mi?
4. Bazı bağlantılar kayboldu mu?
5. Screenshot at - partition öncesi ve sonrası.

**Kontrol 7.2 - API'yi kontrol et:**
```
http://localhost:8000/network/nodes
```
- Response'da partition bilgisi var mı?
- Varsa nasıl gösteriliyor? (örnek: `"partition": "group_a"`)
- Yoksa "yok" de.

---

### **SORUN 8: "Blockchain'de fork olmadı"**

**Kontrol 8.1 - Partition başlat, 30 saniye bekle:**
1. Blockchain sayfasına git
2. Chain Length kaç?
3. Her bloğun "Miner ID" sütununa bak - farklı gruplardan miner'lar var mı?
4. Screenshot at.

**Kontrol 8.2 - Backend console'u oku:**
- "Fork detected" mesajı var mı?
- Varsa hangi blok numarasından sonra? Yaz bana.

---

### **SORUN 9: "Network health çalışmıyor"**

**Kontrol 9.1 - DDoS saldırı başlat:**
1. Metrics Dashboard'daki "Network Health" bar'larına bak
2. Overall Health yüzdesi değişti mi?
3. Validators Health değişti mi?
4. Screenshot at - saldırı öncesi ve sonrası.

**Kontrol 9.2 - Node status kontrol et:**
```
http://localhost:8000/nodes