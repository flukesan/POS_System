"""
Login Window
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
from services.api_client import APIClient, APIError
from ui.styles import INPUT_STYLE, BUTTON_PRIMARY


class LoginWorker(QThread):
    success = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api: APIClient, username: str, password: str):
        super().__init__()
        self.api = api
        self.username = username
        self.password = password

    def run(self):
        try:
            data = self.api.login(self.username, self.password)
            self.success.emit(data)
        except APIError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f'ไม่สามารถเชื่อมต่อกับ Server: {e}')


class LoginWindow(QDialog):
    logged_in = pyqtSignal(dict)

    def __init__(self, api: APIClient, parent=None):
        super().__init__(parent)
        self.api = api
        self.worker = None
        self.setWindowTitle('AgriPOS — เข้าสู่ระบบ')
        self.setFixedSize(420, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Card
        card = QFrame()
        card.setObjectName('login_card')
        card.setStyleSheet("""
            QFrame#login_card {
                background: #ffffff;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)

        # Logo area
        logo_area = QVBoxLayout()
        logo_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.setSpacing(8)

        logo_label = QLabel('🌱')
        logo_label.setFont(QFont('', 48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.addWidget(logo_label)

        title = QLabel('AgriPOS')
        title.setFont(QFont('Sarabun', 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('color: #0f172a;')
        logo_area.addWidget(title)

        sub = QLabel('ระบบจัดการร้านค้าเกษตร')
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet('color: #64748b; font-size: 12px;')
        logo_area.addWidget(sub)

        layout.addLayout(logo_area)
        layout.addSpacing(8)

        # Username
        user_label = QLabel('ชื่อผู้ใช้')
        user_label.setStyleSheet('color: #475569; font-size: 12px; font-weight: 600;')
        layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('admin')
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.username_input)

        # Password
        pw_label = QLabel('รหัสผ่าน')
        pw_label.setStyleSheet('color: #475569; font-size: 12px; font-weight: 600;')
        layout.addWidget(pw_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('••••••••')
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.password_input.returnPressed.connect(self._do_login)
        layout.addWidget(self.password_input)

        layout.addSpacing(4)

        # Login button
        self.login_btn = QPushButton('เข้าสู่ระบบ')
        self.login_btn.setFixedHeight(48)
        self.login_btn.setFont(QFont('Sarabun', 13, QFont.Weight.Bold))
        self.login_btn.setStyleSheet(BUTTON_PRIMARY)
        self.login_btn.clicked.connect(self._do_login)
        layout.addWidget(self.login_btn)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet('color: #ef4444; font-size: 12px;')
        layout.addWidget(self.status_label)

        # Version
        ver = QLabel('AgriPOS v1.0 Desktop')
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet('color: #94a3b8; font-size: 10px;')
        layout.addWidget(ver)

        outer.addWidget(card)
        self.username_input.setFocus()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText('กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText('กำลังเข้าสู่ระบบ...')
        self.status_label.setText('')

        self.worker = LoginWorker(self.api, username, password)
        self.worker.success.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_success(self, data: dict):
        self.login_btn.setEnabled(True)
        self.login_btn.setText('เข้าสู่ระบบ')
        self.logged_in.emit(data)
        self.accept()

    def _on_error(self, msg: str):
        self.login_btn.setEnabled(True)
        self.login_btn.setText('เข้าสู่ระบบ')
        self.status_label.setText(f'❌ {msg}')
        self.password_input.clear()
        self.password_input.setFocus()
