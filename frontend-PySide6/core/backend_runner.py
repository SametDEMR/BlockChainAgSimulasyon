"""
Backend Runner - Runs FastAPI backend in a QThread
"""
from PySide6.QtCore import QThread, Signal
import uvicorn
import sys
import os
import socket
import asyncio
import logging
from typing import Optional

# Logging'i kapat (PyInstaller uyumluluğu için)
logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)


class BackendThread(QThread):
    """
    FastAPI backend'i ayrı bir thread'de çalıştırır.
    
    Signals:
        started: Backend başlatıldığında emit edilir (port bilgisi ile)
        stopped: Backend durdurulduğunda emit edilir
        error: Hata oluştuğunda emit edilir (hata mesajı ile)
    """
    
    started = Signal(int)  # port numarası
    stopped = Signal()
    error = Signal(str)
    
    def __init__(self, port: Optional[int] = None):
        """
        Args:
            port: Backend'in çalışacağı port. None ise boş port bulunur.
        """
        super().__init__()
        self.port = port if port else self._find_free_port()
        self.server: Optional[uvicorn.Server] = None
        self._should_stop = False
        
    @staticmethod
    def _find_free_port() -> int:
        """Boş bir port bulur ve döndürür."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def run(self):
        """Thread'in ana fonksiyonu - Backend'i başlatır."""
        try:
            # sys.path'i düzenle - backend modüllerini import edebilmek için
            self._setup_paths()
            
            # Backend app'i import et
            from backend.main import app
            
            # Uvicorn config oluştur (minimal logging)
            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=self.port,
                log_level="critical",  # En az log
                access_log=False,
                log_config=None,  # PyInstaller uyumluluğu
            )
            
            # Server oluştur
            self.server = uvicorn.Server(config)
            
            # Backend başarıyla başlatıldı sinyali
            self.started.emit(self.port)
            
            # Server'ı çalıştır (blocking)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.server.serve())
            
        except Exception as e:
            error_msg = str(e)
            # Daha detaylı hata mesajı
            if "No module named" in error_msg:
                error_msg = f"Backend modülü bulunamadı: {error_msg}\n\nPath: {sys.path}"
            self.error.emit(error_msg)
        finally:
            self.stopped.emit()
    
    def _setup_paths(self):
        """sys.path'i backend import'ları için ayarlar."""
        # PyInstaller frozen mod kontrolü
        if getattr(sys, 'frozen', False):
            # Exe içindeyiz - _MEIPASS kullan
            base_path = sys._MEIPASS
        else:
            # Normal Python - üst dizine git
            current_dir = os.path.dirname(os.path.abspath(__file__))  # core/
            frontend_dir = os.path.dirname(current_dir)  # frontend-PySide6/
            base_path = os.path.dirname(frontend_dir)  # BlockChainAgSimulasyon/
        
        # Path'e ekle
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
    
    def stop(self):
        """Backend'i durdurur."""
        if self.server:
            self.server.should_exit = True
            # Thread'in bitmesini bekle (max 5 saniye)
            self.wait(5000)
    
    def get_base_url(self) -> str:
        """Backend'in base URL'ini döndürür."""
        return f"http://127.0.0.1:{self.port}"


# Test için
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Backend thread oluştur
    backend = BackendThread()
    
    # Signal bağlantıları
    backend.started.connect(lambda port: print(f"✅ Backend started on port {port}"))
    backend.stopped.connect(lambda: print("❌ Backend stopped"))
    backend.error.connect(lambda msg: print(f"⚠️  Error: {msg}"))
    
    # Backend'i başlat
    backend.start()
    
    print(f"Backend URL: {backend.get_base_url()}")
    print("Press Ctrl+C to stop...")
    
    # Uygulama çalışsın
    try:
        sys.exit(app.exec())
    finally:
        backend.stop()
