"""
UI Test for Byzantine Attack - Milestone 4.3

Bu test dosyası backend'i otomatik başlatır ve UI'yi test etmek için talimatlar verir.
"""

import subprocess
import time
import sys
import os

print("=" * 80)
print("UI TEST - MILESTONE 4.3: Byzantine Attack UI")
print("=" * 80)

print("\n📋 Test Adımları:")
print("\n1️⃣  Backend API'yi başlat")
print("   Komut: python backend/main.py")
print("   Bekleyin: API başlayana kadar (~3 saniye)")

print("\n2️⃣  Frontend UI'yi başlat (AYRI TERMINAL)")
print("   Komut: streamlit run frontend/main.py")
print("   Otomatik açılacak: http://localhost:8501")

print("\n3️⃣  UI'de Test Senaryosu:")
print("   a) ▶️ Start butonuna tıklayın")
print("   b) '🎯 Attack Control' tabına gidin")
print("   c) Attack Type: 'Byzantine' seçin")
print("   d) Target Node: Bir validator seçin (örn: node_0)")
print("   e) '🚀 Trigger Attack' butonuna tıklayın")

print("\n4️⃣  Gözlemlenecek Değişiklikler:")
print("   ✅ Byzantine Attack Status paneli aktif olmalı")
print("   ✅ Target node 'under_attack' durumuna geçmeli")
print("   ✅ Target node'un Trust Score düşmeye başlamalı")
print("   ✅ Diğer validator'ların Trust Score'u artmalı")
print("   ✅ Progress bar saldırı süresini göstermeli")
print("   ✅ 30 saniye sonra otomatik iyileşme olmalı")

print("\n5️⃣  Validator Tabında Kontrol:")
print("   ✅ Trust Score Summary görünmeli")
print("   ✅ Byzantine node yanında '⚠️ BYZANTINE' işareti olmalı")
print("   ✅ Trust score'lar renk kodlu olmalı:")
print("      - Yeşil: ≥90")
print("      - Turuncu: 70-89")
print("      - Kırmızı: <70")
print("   ✅ Detail panelinde tüm metrikler görünmeli")

print("\n6️⃣  PBFT Tabında Kontrol:")
print("   ✅ Primary validator gösterilmeli")
print("   ✅ Consensus sayıları görünmeli")
print("   ✅ View changes takip edilmeli")

print("\n" + "=" * 80)
print("BACKEND BAŞLATILIYOR...")
print("=" * 80)

# Backend'i başlat
backend_process = None
try:
    backend_process = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    print("\n✅ Backend başlatıldı (PID: {})".format(backend_process.pid))
    print("\n⏳ API'nin hazır olması bekleniyor...")
    time.sleep(5)
    
    print("\n" + "=" * 80)
    print("ŞIMDI FRONTEND'İ BAŞLATIN (AYRI TERMINAL):")
    print("=" * 80)
    print("\nKomut:")
    print("   streamlit run frontend/main.py")
    print("\nVeya:")
    print("   cd E:\\PYTHON\\BlockChainAgSimulasyon")
    print("   streamlit run frontend\\main.py")
    
    print("\n" + "=" * 80)
    print("Backend çalışıyor. Durdurmak için Ctrl+C'ye basın.")
    print("=" * 80)
    
    # Backend'in çalışmasını bekle
    backend_process.wait()
    
except KeyboardInterrupt:
    print("\n\n⏹️  Backend durduruluyor...")
    if backend_process:
        backend_process.terminate()
        backend_process.wait()
    print("✅ Backend durduruldu")
    
except Exception as e:
    print(f"\n❌ Hata: {e}")
    if backend_process:
        backend_process.terminate()

print("\n" + "=" * 80)
print("Test tamamlandı!")
print("=" * 80)
