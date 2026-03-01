"""
AgriPOS Desktop App — Entry Point
PyQt6 + FastAPI backend
"""
import sys
import os
import logging
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont

from services.api_client import APIClient
from services.printer import PrinterService
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('AgriPOS')
    app.setOrganizationName('AgriPOS')

    # Font: try Sarabun, fallback to system
    font = QFont('Sarabun', 13)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Init services
    api_url = os.getenv('API_URL', 'http://localhost:8000/api/v1')
    api = APIClient(api_url)
    printer = PrinterService()

    # Try to connect printer at startup (non-blocking)
    printer.connect()

    # Login
    login_win = LoginWindow(api)
    user_data = {}

    def on_login(data: dict):
        nonlocal user_data
        user_data = data

    login_win.logged_in.connect(on_login)

    if login_win.exec() != LoginWindow.DialogCode.Accepted:
        sys.exit(0)

    # Main window
    main_win = MainWindow(api, user_data, printer)
    main_win.show()
    main_win.showMaximized()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
