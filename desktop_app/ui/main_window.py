"""
Main Window — Shell with sidebar navigation
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QSizePolicy, QButtonGroup, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from services.api_client import APIClient
from services.printer import PrinterService
from ui.pos_terminal import POSTerminal
from ui.products_page import ProductsPage
from ui.customers_page import CustomersPage
from ui.dashboard_page import DashboardPage
from ui.settings_page import SettingsPage
from ui.styles import SIDEBAR_STYLE, MAIN_STYLE


ROLE_LABEL = {
    'admin': 'ผู้ดูแลระบบ',
    'manager': 'ผู้จัดการ',
    'cashier': 'แคชเชียร์',
    'warehouse': 'คลังสินค้า',
}

NAV_ITEMS = [
    ('dashboard',  '📊', 'แดชบอร์ด'),
    ('pos',        '🛒', 'ขายสินค้า (POS)'),
    ('products',   '📦', 'สินค้า'),
    ('customers',  '👥', 'ลูกค้า / เครดิต'),
    ('settings',   '⚙️', 'ตั้งค่า'),
]


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName('nav_btn')
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setText(f'  {icon}  {label}')
        self.setFont(QFont('Sarabun', 12))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MainWindow(QMainWindow):
    def __init__(self, api: APIClient, user: dict, printer: PrinterService):
        super().__init__()
        self.api = api
        self.user = user
        self.printer = printer
        self.setWindowTitle('AgriPOS — ระบบจัดการร้านค้าเกษตร')
        self.setMinimumSize(1280, 780)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setObjectName('page_container')
        self.stack.setStyleSheet('background: #f8fafc;')
        root.addWidget(self.stack, stretch=1)

        self.setStyleSheet(MAIN_STYLE)
        self._build_pages()

        # Default to POS
        self._switch_to('pos')
        self.nav_buttons['pos'].setChecked(True)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(SIDEBAR_STYLE)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        # Logo
        logo_frame = QFrame()
        logo_frame.setStyleSheet('background: rgba(255,255,255,0.05); border-radius: 12px;')
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(12, 10, 12, 10)
        logo_layout.setSpacing(10)

        icon_lbl = QLabel('🌱')
        icon_lbl.setFont(QFont('', 22))
        logo_layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        title_lbl = QLabel('AgriPOS')
        title_lbl.setObjectName('logo_title')
        title_lbl.setFont(QFont('Sarabun', 13, QFont.Weight.Bold))
        sub_lbl = QLabel('ร้านค้าเกษตร')
        sub_lbl.setObjectName('logo_sub')
        sub_lbl.setFont(QFont('Sarabun', 10))
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(sub_lbl)
        logo_layout.addLayout(text_layout)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)
        layout.addSpacing(12)

        # Nav buttons
        self.nav_buttons: dict[str, NavButton] = {}
        self.btn_group = QButtonGroup()
        self.btn_group.setExclusive(True)

        for key, icon, label in NAV_ITEMS:
            btn = NavButton(icon, label)
            self.btn_group.addButton(btn)
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
            btn.clicked.connect(lambda _, k=key: self._switch_to(k))

        layout.addStretch()

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet('color: rgba(255,255,255,0.10);')
        layout.addWidget(sep)
        layout.addSpacing(8)

        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet('background: rgba(255,255,255,0.05); border-radius: 12px;')
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(12, 10, 12, 10)
        user_layout.setSpacing(10)

        avatar_lbl = QLabel(self.user.get('full_name', 'U')[0])
        avatar_lbl.setFixedSize(36, 36)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        avatar_lbl.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #8b5cf6);
            color: white; border-radius: 18px;
        """)
        user_layout.addWidget(avatar_lbl)

        user_text = QVBoxLayout()
        user_text.setSpacing(1)
        name_lbl = QLabel(self.user.get('full_name', ''))
        name_lbl.setObjectName('user_name')
        name_lbl.setFont(QFont('Sarabun', 11, QFont.Weight.DemiBold))
        role_lbl = QLabel(ROLE_LABEL.get(self.user.get('role', ''), ''))
        role_lbl.setObjectName('user_role')
        role_lbl.setFont(QFont('Sarabun', 10))
        user_text.addWidget(name_lbl)
        user_text.addWidget(role_lbl)
        user_layout.addLayout(user_text)
        layout.addWidget(user_frame)

        # Logout
        logout_btn = QPushButton('  🚪  ออกจากระบบ')
        logout_btn.setObjectName('logout_btn')
        logout_btn.setFixedHeight(38)
        logout_btn.setFont(QFont('Sarabun', 11))
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)

        return sidebar

    def _build_pages(self):
        self.pages: dict[str, QWidget] = {}

        self.pages['dashboard'] = DashboardPage(self.api)
        self.pages['pos'] = POSTerminal(self.api, self.printer, self.user)
        self.pages['products'] = ProductsPage(self.api)
        self.pages['customers'] = CustomersPage(self.api)
        self.pages['settings'] = SettingsPage(self.printer)

        for page in self.pages.values():
            self.stack.addWidget(page)

    def _switch_to(self, key: str):
        page = self.pages.get(key)
        if page:
            self.stack.setCurrentWidget(page)
            if hasattr(page, 'on_show'):
                page.on_show()

    def _logout(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'ออกจากระบบ', 'ต้องการออกจากระบบ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
