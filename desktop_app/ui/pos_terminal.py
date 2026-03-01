"""
POS Terminal — Main selling screen
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QDialog, QSizePolicy, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QButtonGroup, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, pyqtSlot, QByteArray
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
from typing import List, Dict, Optional
from services.api_client import APIClient, APIError
from services.printer import PrinterService
from ui.styles import (
    INPUT_STYLE, BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_DANGER,
    TABLE_STYLE, NUMPAD_STYLE, CHECKOUT_BTN_STYLE, PRODUCT_CARD_STYLE
)
import logging

logger = logging.getLogger(__name__)


# ── Cart Item ─────────────────────────────────────────────────
class CartItem:
    def __init__(self, product: dict):
        self.product = product
        self.quantity: float = 1.0
        self.unit_price: float = float(product.get('selling_price', 0))
        self.discount_percent: float = 0.0

    @property
    def discount_amount(self) -> float:
        return self.unit_price * self.quantity * self.discount_percent / 100

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity - self.discount_amount

    @property
    def tax_amount(self) -> float:
        rate = float(self.product.get('tax_rate', 7))
        return self.subtotal * rate / (100 + rate)

    @property
    def total(self) -> float:
        return self.subtotal


# ── Product Search Worker ─────────────────────────────────────
class ProductSearchWorker(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api: APIClient, search: str):
        super().__init__()
        self.api = api
        self.search = search

    def run(self):
        try:
            data = self.api.get_products(self.search, limit=60)
            self.result.emit(data if isinstance(data, list) else [])
        except Exception as e:
            self.error.emit(str(e))


# ── Image Loader Thread ────────────────────────────────────────
class ImageLoader(QThread):
    loaded = pyqtSignal(QPixmap)

    def __init__(self, url: str, w: int = 60, h: int = 60):
        super().__init__()
        self.url = url
        self.w = w
        self.h = h

    def run(self):
        try:
            import requests as _req
            resp = _req.get(self.url, timeout=5)
            resp.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(resp.content))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    self.w, self.h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.loaded.emit(pixmap)
        except Exception:
            pass


# ── Product Card Widget ───────────────────────────────────────
class ProductCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, product: dict, base_url: str = '', parent=None):
        super().__init__(parent)
        self.product = product
        self.base_url = base_url
        self._img_loader: Optional[ImageLoader] = None
        self.setObjectName('product_card')
        self.setFixedSize(160, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(PRODUCT_CARD_STYLE + """
            QFrame#product_card { cursor: pointer; }
        """)
        self._build()

    def _resolve_url(self, url: str) -> str:
        if not url:
            return ''
        if url.startswith('http://') or url.startswith('https://'):
            return url
        return self.base_url.rstrip('/') + '/' + url.lstrip('/')

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Image area
        self.img_lbl = QLabel('📦')
        self.img_lbl.setFont(QFont('', 28))
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setFixedSize(140, 60)
        self.img_lbl.setStyleSheet('background: #f1f5f9; border-radius: 6px;')
        layout.addWidget(self.img_lbl)

        img_url = self._resolve_url(self.product.get('main_image_url') or '')
        if img_url:
            self._img_loader = ImageLoader(img_url, 140, 60)
            self._img_loader.loaded.connect(self._on_image_loaded)
            self._img_loader.start()

        # Name
        name = QLabel(self.product.get('name', ''))
        name.setFont(QFont('Sarabun', 11, QFont.Weight.Bold))
        name.setStyleSheet('color: #1e293b;')
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setMaximumHeight(42)
        layout.addWidget(name)

        # Price
        price = self.product.get('selling_price', 0)
        unit = self.product.get('unit', '')
        price_label = QLabel(f'฿{float(price):,.2f}/{unit}')
        price_label.setFont(QFont('Sarabun', 11, QFont.Weight.Bold))
        price_label.setStyleSheet('color: #10b981;')
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_label)

    def _on_image_loaded(self, pixmap: QPixmap):
        self.img_lbl.setPixmap(pixmap)
        self.img_lbl.setText('')

    def mousePressEvent(self, event):
        self.clicked.emit(self.product)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(PRODUCT_CARD_STYLE + """
            QFrame#product_card {
                background: #f0fdf4;
                border-color: #10b981;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(PRODUCT_CARD_STYLE)
        super().leaveEvent(event)


# ── Cart Table ────────────────────────────────────────────────
class CartTable(QTableWidget):
    qty_changed = pyqtSignal(int, float)
    item_removed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['สินค้า', 'ราคา', 'จำนวน', 'ส่วนลด%', 'รวม'])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(TABLE_STYLE + """
            QTableWidget { alternate-background-color: #f8fafc; }
        """)

    def load_items(self, items: List[CartItem], base_url: str = ''):
        self._img_loaders: list = getattr(self, '_img_loaders', [])
        self._img_loaders.clear()
        self.setRowCount(len(items))
        for row, item in enumerate(items):
            self.setRowHeight(row, 56)

            # Name + code (with thumbnail)
            name_widget = QWidget()
            name_h = QHBoxLayout(name_widget)
            name_h.setContentsMargins(4, 4, 4, 4)
            name_h.setSpacing(6)

            # Thumbnail
            img_lbl = QLabel('📦')
            img_lbl.setFixedSize(44, 44)
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_lbl.setStyleSheet('background: #f1f5f9; border-radius: 6px; font-size: 20px;')
            name_h.addWidget(img_lbl)

            raw_url = item.product.get('main_image_url') or ''
            if raw_url and base_url:
                img_url = raw_url if raw_url.startswith('http') else base_url.rstrip('/') + '/' + raw_url.lstrip('/')
                loader = ImageLoader(img_url, 44, 44)
                loader.loaded.connect(lambda px, lbl=img_lbl: (lbl.setPixmap(px), lbl.setText('')))
                loader.start()
                self._img_loaders.append(loader)

            text_col = QWidget()
            text_layout = QVBoxLayout(text_col)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(1)
            name_lbl = QLabel(item.product.get('name', ''))
            name_lbl.setFont(QFont('Sarabun', 12, QFont.Weight.DemiBold))
            name_lbl.setStyleSheet('color: #1e293b;')
            code_lbl = QLabel(item.product.get('code', ''))
            code_lbl.setStyleSheet('color: #94a3b8; font-size: 10px; font-family: monospace;')
            text_layout.addWidget(name_lbl)
            text_layout.addWidget(code_lbl)
            name_h.addWidget(text_col)
            self.setCellWidget(row, 0, name_widget)

            # Price
            price_item = QTableWidgetItem(f'฿{item.unit_price:,.2f}')
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setForeground(QColor('#475569'))
            self.setItem(row, 1, price_item)

            # Qty spinner
            qty_spin = QDoubleSpinBox()
            qty_spin.setMinimum(0.001)
            qty_spin.setMaximum(9999)
            qty_spin.setDecimals(2)
            qty_spin.setSingleStep(1)
            qty_spin.setValue(item.quantity)
            qty_spin.setFixedWidth(80)
            qty_spin.setStyleSheet("""
                QDoubleSpinBox {
                    background: #f1f5f9; border: 1px solid #e2e8f0;
                    border-radius: 8px; padding: 4px 8px; font-size: 13px;
                }
                QDoubleSpinBox:focus { border-color: #10b981; background: #f0fdf4; }
            """)
            captured_row = row
            qty_spin.valueChanged.connect(lambda v, r=captured_row: self.qty_changed.emit(r, v))
            self.setCellWidget(row, 2, qty_spin)

            # Discount %
            disc_item = QTableWidgetItem(f'{item.discount_percent:.0f}%')
            disc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            if item.discount_percent > 0:
                disc_item.setForeground(QColor('#ef4444'))
            self.setItem(row, 3, disc_item)

            # Total
            total_item = QTableWidgetItem(f'฿{item.total:,.2f}')
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setForeground(QColor('#10b981'))
            total_item.setFont(QFont('Sarabun', 12, QFont.Weight.Bold))
            self.setItem(row, 4, total_item)


# ── Payment Dialog ────────────────────────────────────────────
class PaymentDialog(QDialog):
    payment_done = pyqtSignal(dict)

    def __init__(self, total: float, api: APIClient, order_data: dict, printer: PrinterService, parent=None):
        super().__init__(parent)
        self.total = total
        self.api = api
        self.order_data = order_data
        self.printer = printer
        self.setWindowTitle('ชำระเงิน')
        self.setFixedSize(440, 520)
        self.setStyleSheet('QDialog { background: #ffffff; border-radius: 16px; }')
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 28)

        title = QLabel('💳 ชำระเงิน')
        title.setFont(QFont('Sarabun', 16, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        layout.addWidget(title)

        # Total display
        total_frame = QFrame()
        total_frame.setStyleSheet('background: #f0fdf4; border-radius: 12px; border: 1.5px solid #bbf7d0;')
        total_layout = QVBoxLayout(total_frame)
        total_layout.setContentsMargins(16, 12, 16, 12)

        total_lbl = QLabel('ยอดชำระ')
        total_lbl.setStyleSheet('color: #065f46; font-size: 12px; font-weight: 600;')
        total_layout.addWidget(total_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        amount_lbl = QLabel(f'฿{self.total:,.2f}')
        amount_lbl.setFont(QFont('Sarabun', 32, QFont.Weight.Bold))
        amount_lbl.setStyleSheet('color: #059669;')
        amount_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(amount_lbl)
        layout.addWidget(total_frame)

        # Cash received input
        recv_label = QLabel('รับเงิน (บาท)')
        recv_label.setStyleSheet('color: #475569; font-size: 12px; font-weight: 600;')
        layout.addWidget(recv_label)

        self.received_input = QDoubleSpinBox()
        self.received_input.setMinimum(0)
        self.received_input.setMaximum(999999)
        self.received_input.setDecimals(2)
        self.received_input.setValue(self._round_up(self.total))
        self.received_input.setFixedHeight(52)
        self.received_input.setFont(QFont('Sarabun', 18, QFont.Weight.Bold))
        self.received_input.setStyleSheet(INPUT_STYLE)
        self.received_input.valueChanged.connect(self._update_change)
        layout.addWidget(self.received_input)

        # Quick cash buttons
        quick_row = QHBoxLayout()
        for amt in [20, 50, 100, 500, 1000]:
            btn = QPushButton(f'฿{amt}')
            btn.setFixedHeight(36)
            btn.setStyleSheet(BUTTON_SECONDARY)
            btn.clicked.connect(lambda _, a=amt: self.received_input.setValue(a))
            quick_row.addWidget(btn)
        layout.addLayout(quick_row)

        # Change
        self.change_label = QLabel('เงินทอน: ฿0.00')
        self.change_label.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        self.change_label.setStyleSheet('color: #0ea5e9; padding: 8px 12px; background: #f0f9ff; border-radius: 10px;')
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.change_label)

        # Confirm button
        self.confirm_btn = QPushButton('✓  ยืนยันชำระเงิน + เปิดลิ้นชัก')
        self.confirm_btn.setFixedHeight(56)
        self.confirm_btn.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        self.confirm_btn.setStyleSheet(CHECKOUT_BTN_STYLE)
        self.confirm_btn.clicked.connect(self._confirm)
        layout.addWidget(self.confirm_btn)

        self._update_change()

        cancel_btn = QPushButton('ยกเลิก')
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(BUTTON_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

    def _round_up(self, amount: float) -> float:
        """Round up to nearest 1 baht."""
        import math
        return math.ceil(amount)

    def _update_change(self):
        received = self.received_input.value()
        change = max(0, received - self.total)
        self.change_label.setText(f'เงินทอน: ฿{change:,.2f}')
        self.confirm_btn.setEnabled(received >= self.total)

    def _confirm(self):
        received = self.received_input.value()
        change = max(0, received - self.total)
        self.order_data['paid_amount'] = received
        self.order_data['change_amount'] = change
        self.order_data['payment_method'] = 'cash'

        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setText('กำลังบันทึก...')

        try:
            order = self.api.create_order(self.order_data)
            # Open cash drawer
            self.printer.open_cash_drawer()
            # Print receipt
            self.printer.print_receipt(order, {})
            self.payment_done.emit(order)
            self.accept()
        except APIError as e:
            QMessageBox.critical(self, 'ข้อผิดพลาด', str(e))
            self.confirm_btn.setEnabled(True)
            self.confirm_btn.setText('✓  ยืนยันชำระเงิน + เปิดลิ้นชัก')


# ── POS Terminal Main Widget ──────────────────────────────────
class POSTerminal(QWidget):
    def __init__(self, api: APIClient, printer: PrinterService, user: dict, parent=None):
        super().__init__(parent)
        self.api = api
        self.printer = printer
        self.user = user
        self.cart: List[CartItem] = []
        self.products: List[dict] = []
        self.search_worker: Optional[ProductSearchWorker] = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)
        self._build()
        self._load_products()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Left: Products ─────────────────────────────────────
        left = QWidget()
        left.setStyleSheet('background: #f8fafc;')
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(12)

        # Top bar
        top_bar = QHBoxLayout()
        search_label = QLabel('🔍')
        search_label.setFont(QFont('', 16))
        top_bar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('ค้นหาสินค้า ชื่อ / รหัส / บาร์โค้ด...')
        self.search_input.setFixedHeight(44)
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self._search_changed)
        top_bar.addWidget(self.search_input)

        scan_btn = QPushButton('📷  สแกน')
        scan_btn.setFixedHeight(44)
        scan_btn.setFixedWidth(90)
        scan_btn.setStyleSheet(BUTTON_SECONDARY)
        top_bar.addWidget(scan_btn)
        left_layout.addLayout(top_bar)

        # Product grid scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet('background: transparent;')
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_widget)
        left_layout.addWidget(scroll)

        self.status_label = QLabel('กำลังโหลดสินค้า...')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet('color: #94a3b8; font-size: 13px; padding: 20px;')
        left_layout.addWidget(self.status_label)
        self.status_label.hide()

        layout.addWidget(left, stretch=3)

        # ── Right: Cart ────────────────────────────────────────
        right = QWidget()
        right.setFixedWidth(420)
        right.setStyleSheet('background: #ffffff; border-left: 1px solid #e2e8f0;')
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Cart header
        cart_header = QWidget()
        cart_header.setFixedHeight(52)
        cart_header.setStyleSheet('background: #f8fafc; border-bottom: 1px solid #e2e8f0;')
        cart_h = QHBoxLayout(cart_header)
        cart_h.setContentsMargins(16, 0, 16, 0)

        cart_title = QLabel('🛒  ตะกร้าสินค้า')
        cart_title.setFont(QFont('Sarabun', 15, QFont.Weight.Bold))
        cart_title.setStyleSheet('color: #1e293b;')
        cart_h.addWidget(cart_title)
        cart_h.addStretch()

        self.clear_btn = QPushButton('🗑 ล้าง')
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.setStyleSheet("""
            QPushButton { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; border-radius: 8px; padding: 0 12px; font-size: 12px; font-weight: 600; }
            QPushButton:hover { background: #ffe4e6; }
        """)
        self.clear_btn.clicked.connect(self._clear_cart)
        cart_h.addWidget(self.clear_btn)
        right_layout.addWidget(cart_header)

        # Cart table
        self.cart_table = CartTable()
        self.cart_table.qty_changed.connect(self._on_qty_changed)
        right_layout.addWidget(self.cart_table, stretch=1)

        # Totals panel
        totals_widget = QWidget()
        totals_widget.setStyleSheet('background: #f8fafc; border-top: 1px solid #e2e8f0;')
        totals_layout = QVBoxLayout(totals_widget)
        totals_layout.setContentsMargins(16, 12, 16, 16)
        totals_layout.setSpacing(6)

        def total_row(label, value_attr, big=False, color='#475569'):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont('Sarabun', 18 if big else 14, QFont.Weight.Bold if big else QFont.Weight.DemiBold))
            lbl.setStyleSheet(f'color: {color};')
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel('฿0.00')
            val.setFont(QFont('Sarabun', 20 if big else 14, QFont.Weight.Bold))
            val.setStyleSheet(f'color: {color};')
            setattr(self, value_attr, val)
            row.addWidget(val)
            return row

        totals_layout.addLayout(total_row('ยอดรวม', 'subtotal_lbl', color='#475569'))
        totals_layout.addLayout(total_row('ภาษี 7%', 'tax_lbl', color='#64748b'))

        # Divider before total
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet('color: #e2e8f0; margin: 4px 0;')
        totals_layout.addWidget(div)

        self.total_row = total_row('ยอดชำระ', 'total_lbl', big=True, color='#059669')
        totals_layout.addLayout(self.total_row)
        totals_layout.addSpacing(8)

        # Checkout button
        self.checkout_btn = QPushButton('💰  ชำระเงิน')
        self.checkout_btn.setFixedHeight(60)
        self.checkout_btn.setFont(QFont('Sarabun', 16, QFont.Weight.Bold))
        self.checkout_btn.setStyleSheet(CHECKOUT_BTN_STYLE)
        self.checkout_btn.setEnabled(False)
        self.checkout_btn.clicked.connect(self._checkout)
        totals_layout.addWidget(self.checkout_btn)

        right_layout.addWidget(totals_widget)
        layout.addWidget(right)

    # ── Product Loading ───────────────────────────────────────
    def _load_products(self, search=''):
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
        self.search_worker = ProductSearchWorker(self.api, search)
        self.search_worker.result.connect(self._on_products_loaded)
        self.search_worker.error.connect(self._on_search_error)
        self.search_worker.start()

    @pyqtSlot(list)
    def _on_products_loaded(self, products: list):
        self.products = products
        self._render_products(products)

    def _render_products(self, products: list):
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not products:
            self.status_label.setText('ไม่พบสินค้า')
            self.status_label.show()
            return

        self.status_label.hide()
        cols = 4
        for i, product in enumerate(products):
            card = ProductCard(product, base_url=self.api.base_url)
            card.clicked.connect(self._add_to_cart)
            self.grid_layout.addWidget(card, i // cols, i % cols)

    @pyqtSlot(str)
    def _on_search_error(self, msg: str):
        self.status_label.setText(f'ข้อผิดพลาด: {msg}')
        self.status_label.show()

    def _search_changed(self, text: str):
        self.search_timer.start(300)

    def _do_search(self):
        self._load_products(self.search_input.text())

    # ── Cart Operations ───────────────────────────────────────
    def _add_to_cart(self, product: dict):
        pid = product.get('id')
        for item in self.cart:
            if item.product.get('id') == pid:
                item.quantity += 1
                self._refresh_cart()
                return
        self.cart.append(CartItem(product))
        self._refresh_cart()

    def _on_qty_changed(self, row: int, value: float):
        if 0 <= row < len(self.cart):
            if value <= 0:
                self.cart.pop(row)
            else:
                self.cart[row].quantity = value
            self._refresh_cart()

    def _clear_cart(self):
        if not self.cart:
            return
        reply = QMessageBox.question(self, 'ล้างตะกร้า', 'ต้องการล้างสินค้าทั้งหมดในตะกร้า?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cart.clear()
            self._refresh_cart()

    def _refresh_cart(self):
        self.cart_table.load_items(self.cart, base_url=self.api.base_url)
        subtotal = sum(i.subtotal for i in self.cart)
        tax = sum(i.tax_amount for i in self.cart)
        total = sum(i.total for i in self.cart)

        self.subtotal_lbl.setText(f'฿{subtotal:,.2f}')
        self.tax_lbl.setText(f'฿{tax:,.2f}')
        self.total_lbl.setText(f'฿{total:,.2f}')
        self.checkout_btn.setEnabled(len(self.cart) > 0)

    # ── Checkout ──────────────────────────────────────────────
    def _checkout(self):
        if not self.cart:
            return
        total = sum(i.total for i in self.cart)

        order_data = {
            'cashier_id': self.user.get('user_id'),
            'items': [
                {
                    'product_id': item.product['id'],
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'discount_percent': item.discount_percent,
                    'tax_rate': float(item.product.get('tax_rate', 7)),
                }
                for item in self.cart
            ],
        }

        dlg = PaymentDialog(total, self.api, order_data, self.printer, self)
        dlg.payment_done.connect(self._on_payment_done)
        dlg.exec()

    def _on_payment_done(self, order: dict):
        self.cart.clear()
        self._refresh_cart()
        QMessageBox.information(self, 'สำเร็จ', f'✅ ชำระเงินสำเร็จ\nเลขที่: {order.get("order_number", "")}')
