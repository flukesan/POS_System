"""
Dashboard Page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from services.api_client import APIClient
from ui.styles import BUTTON_SECONDARY, CARD_STYLE


class DashboardWorker(QThread):
    result = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api: APIClient):
        super().__init__()
        self.api = api

    def run(self):
        try:
            data = self.api.get_dashboard()
            self.result.emit(data)
        except Exception as e:
            self.error.emit(str(e))


def make_kpi_card(icon: str, label: str, value: str, sub: str, gradient: tuple) -> QFrame:
    card = QFrame()
    card.setObjectName('card')
    card.setStyleSheet(f"""
        QFrame#card {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {gradient[0]}, stop:1 {gradient[1]});
            border-radius: 16px;
            border: none;
        }}
    """)
    card.setFixedHeight(120)
    layout = QHBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(16)

    # Icon
    icon_lbl = QLabel(icon)
    icon_lbl.setFont(QFont('', 32))
    icon_lbl.setFixedSize(56, 56)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_lbl.setStyleSheet('background: rgba(255,255,255,0.2); border-radius: 14px;')
    layout.addWidget(icon_lbl)

    # Text
    text_layout = QVBoxLayout()
    text_layout.setSpacing(2)

    label_lbl = QLabel(label)
    label_lbl.setStyleSheet('color: rgba(255,255,255,0.8); font-size: 12px; font-weight: 500;')
    text_layout.addWidget(label_lbl)

    value_lbl = QLabel(value)
    value_lbl.setFont(QFont('Sarabun', 22, QFont.Weight.Bold))
    value_lbl.setStyleSheet('color: #ffffff;')
    value_lbl.setObjectName(f'kpi_{label}')
    text_layout.addWidget(value_lbl)

    sub_lbl = QLabel(sub)
    sub_lbl.setStyleSheet('color: rgba(255,255,255,0.6); font-size: 11px;')
    text_layout.addWidget(sub_lbl)
    layout.addLayout(text_layout)
    layout.addStretch()

    return card


class DashboardPage(QWidget):
    def __init__(self, api: APIClient, parent=None):
        super().__init__(parent)
        self.api = api
        self.worker = None
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #f8fafc; }')

        content = QWidget()
        content.setStyleSheet('background: #f8fafc;')
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel('แดชบอร์ด')
        title.setFont(QFont('Sarabun', 22, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton('🔄  รีเฟรช')
        refresh_btn.setFixedHeight(36)
        refresh_btn.setStyleSheet(BUTTON_SECONDARY)
        refresh_btn.clicked.connect(self.on_show)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # KPI Grid
        self.kpi_grid = QGridLayout()
        self.kpi_grid.setSpacing(14)

        kpis = [
            ('💰', 'ยอดขายวันนี้', '฿0', '0 รายการ', ('#10b981', '#059669')),
            ('📈', 'ยอดขายเดือนนี้', '฿0', '0 รายการ', ('#3b82f6', '#1d4ed8')),
            ('⚠️', 'สินค้าใกล้หมด', '0', 'รายการ', ('#f59e0b', '#d97706')),
            ('💳', 'เครดิตค้างชำระ', '฿0', 'เกินกำหนด 0 ราย', ('#ef4444', '#dc2626')),
        ]

        self.kpi_cards = []
        for i, (icon, label, value, sub, gradient) in enumerate(kpis):
            card = make_kpi_card(icon, label, value, sub, gradient)
            self.kpi_grid.addWidget(card, 0, i)
            self.kpi_cards.append((label, card))

        layout.addLayout(self.kpi_grid)

        # Placeholder for recent orders
        orders_card = QFrame()
        orders_card.setObjectName('card')
        orders_card.setStyleSheet(CARD_STYLE)
        orders_layout = QVBoxLayout(orders_card)
        orders_layout.setContentsMargins(20, 16, 20, 16)

        orders_title = QLabel('ยอดขายล่าสุด')
        orders_title.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        orders_title.setStyleSheet('color: #0f172a;')
        orders_layout.addWidget(orders_title)

        self.orders_placeholder = QLabel('กำลังโหลดข้อมูล...')
        self.orders_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orders_placeholder.setStyleSheet('color: #94a3b8; padding: 40px; font-size: 13px;')
        orders_layout.addWidget(self.orders_placeholder)
        layout.addWidget(orders_card)
        layout.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def on_show(self):
        if self.worker and self.worker.isRunning():
            return
        self.worker = DashboardWorker(self.api)
        self.worker.result.connect(self._on_data)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_data(self, data: dict):
        today = data.get('today', {})
        month = data.get('this_month', {})
        low = data.get('low_stock_products', 0)
        credit = data.get('total_outstanding_credit', 0)
        overdue = data.get('overdue_customers', 0)

        values = [
            (f'฿{float(today.get("total_sales",0)):,.0f}', f'{today.get("order_count",0)} รายการ'),
            (f'฿{float(month.get("total_sales",0)):,.0f}', f'{month.get("order_count",0)} รายการ'),
            (str(low), 'รายการที่ต้องสั่งซื้อ'),
            (f'฿{float(credit):,.0f}', f'เกินกำหนด {overdue} ราย'),
        ]
        for (label, card), (val, sub) in zip(self.kpi_cards, values):
            val_lbl = card.findChild(QLabel, f'kpi_{label}')
            if val_lbl:
                val_lbl.setText(val)

        self.orders_placeholder.setText(f'ยอดขายวันนี้: {today.get("order_count",0)} รายการ | เดือนนี้: {month.get("order_count",0)} รายการ')

    def _on_error(self, msg: str):
        self.orders_placeholder.setText(f'ไม่สามารถโหลดข้อมูลได้: {msg}')
