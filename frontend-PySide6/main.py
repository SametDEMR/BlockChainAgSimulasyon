"""Main application entry point."""
import sys
from PySide6.QtWidgets import QApplication

from core.api_client import APIClient
from core.data_manager import DataManager
from core.updater import DataUpdater
from ui.main_window import MainWindow


def main():
    """Main application function."""
    app = QApplication(sys.argv)
    
    # Create core components
    api_client = APIClient("http://localhost:8000")
    data_manager = DataManager(api_client)
    # DÜZELTME: Refresh interval'ı 1 saniyeye düşür (blok üretiminden hızlı olmalı)
    # Bu sayede her blok üretildiğinde hemen görüntülenir
    updater = DataUpdater(api_client, data_manager, interval_ms=1000)
    
    # Create and show main window
    window = MainWindow(api_client, data_manager, updater)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
