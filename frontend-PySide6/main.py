"""Main application entry point."""
import sys
from PySide6.QtWidgets import QApplication

from core.api_client import APIClient
from core.data_manager import DataManager
from core.updater import DataUpdater
from core.backend_runner import BackendThread
from ui.main_window import MainWindow


def main():
    """Main application function."""
    app = QApplication(sys.argv)
    app.setApplicationName("Blockchain Attack Simulator")
    app.setOrganizationName("BlockchainSim")
    
    # Backend thread oluştur (embedded backend)
    backend_thread = BackendThread()  # Otomatik boş port bulur
    
    # API client oluştur (başlangıç URL placeholder, backend başlayınca güncellenir)
    api_client = APIClient("http://localhost:8000")
    
    # Data manager ve updater oluştur
    data_manager = DataManager(api_client)
    updater = DataUpdater(api_client, data_manager, interval_ms=1000)
    
    # Main window oluştur ve backend thread'ini ver
    window = MainWindow(
        api_client, 
        data_manager, 
        updater, 
        backend_thread=backend_thread  # Embedded backend
    )
    window.show()
    
    # Uygulama çalışsın
    exit_code = app.exec()
    
    # Cleanup
    backend_thread.stop()
    backend_thread.wait(5000)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
