📋 SORUN KATEGORİLERİ
🎨 UI / FRONTEND GÖRSELLEŞTİRME SORUNLARI
1. Layout ve Boyutlandırma

✏️ Network nodes tablosunu büyütmek
✏️ LEGEND kısmındaki öğeleri yan yana yazdırmak
✏️ OVERVIEW ve NETWORK HEALTH kısmını dikeyde küçültmek
✏️ Node Status Card kısmını yatayda genişletmek
✏️ Blockchain görselleştirmede büyültme/küçültme kaldırmak, sadece yatay kaydırma
✏️ Blockchain görselleştirmede içerik her zaman ortada olmalı
✏️ Message Traffic Table'a renk açıklamalarını sayfanın altına eklemek

2. Dashboard Düzenlemesi

✏️ Attack Panel'deki ACTIVE ATTACKS kısmını çıkarıp en alta eklemek
✏️ SYSTEM METRICS kısmını kaldırmak (önemsiz ise)

3. Görselleştirme ve Veri Gösterimi

✏️ Blockchain görselleştirmede blokların tüm verilerini ekranda göstermek (hover'da değil)
✏️ RECENT ACTIVITY LOG'u Node'lar tabında alta eklemek


🐛 BACKEND ENTEGRASYON VE LOGIC SORUNLARI
4. Fork Detection

⚠️ Fork Detection Status normal çalışma sırasında bile aktif
⚠️ Ne zaman çalışması gerektiğini belirlenmeli (sadece fork durumunda)

5. PBFT Güncelleme Sorunu

⚠️ PBFT Messages tabındaki PBFT-STATUS güncellenmemiyor

6. Sybil Attack Hatası

🔴 Sybil Attack çalışınca: 'dict' object has no attribute 'to_dict' hatası
🔴 Bu bir serialization sorunu

7. Network Map Bağlantı Sorunu

⚠️ Network MAP'te regular node'lar sadece node_0'a bağlanıyor
⚠️ Diğer node'lara bağlantı yok
⚠️ Blok üretimini sadece node_0 kısmı mı yapıyor?

8. Fork Görselleştirme

🔴 Fork görselleştirme düzgün çalışmıyor
🔴 Kontrol edilmesi gerekiyor


⚙️ SISTEM PERFORMANS VE OPTİMİZASYON
9. Backend Bağlantı Kopması

🔴 Optimizasyonda problem var
🔴 Arada Backend bağlantısı kopuyor
🔴 Bu kritik bir stabilite sorunu


🔒 GÜVENLIK VE KISITLAMALAR
10. Eşzamanlı Atak Limiti

✏️ Aynı anda sadece 1 atağa izin verilmeli
✏️ Şu anda birden fazla atak tetiklenebiliyor