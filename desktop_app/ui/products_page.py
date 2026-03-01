"""
Products Management Page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox,
    QTextEdit, QMessageBox, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from services.api_client import APIClient, APIError
from ui.styles import (
    INPUT_STYLE, BUTTON_PRIMARY, BUTTON_SECONDARY, TABLE_STYLE,
    DIALOG_STYLE, CARD_STYLE
)

UNITS = ['piece', 'kg', 'g', 'l', 'ml', 'bag', 'box', 'set', 'bottle', 'pack']


class ProductsWorker(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api: APIClient, search=''):
        super().__init__()
        self.api = api
        self.search = search

    def run(self):
        try:
            data = self.api.get_products(self.search, 200)
            self.result.emit(data if isinstance(data, list) else [])
        except Exception as e:
            self.error.emit(str(e))


class ProductFormDialog(QDialog):
    saved = pyqtSignal()

    def __init__(self, api: APIClient, product: dict = None, categories: list = None, parent=None):
        super().__init__(parent)
        self.api = api
        self.product = product
        self.categories = categories or []
        self.setWindowTitle('แก้ไขสินค้า' if product else 'เพิ่มสินค้าใหม่')
        self.setFixedWidth(520)
        self.setStyleSheet('QDialog { background: #ffffff; }')
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel('แก้ไขสินค้า' if self.product else '➕  เพิ่มสินค้าใหม่')
        title.setFont(QFont('Sarabun', 15, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet('color: #475569; font-size: 12px; font-weight: 600;')
            return l

        def inp(placeholder='', value=''):
            w = QLineEdit(value)
            w.setPlaceholderText(placeholder)
            w.setFixedHeight(40)
            w.setStyleSheet(INPUT_STYLE)
            return w

        self.code_inp = inp('PRD-001', self.product.get('code','') if self.product else '')
        form.addRow(lbl('รหัสสินค้า *'), self.code_inp)

        self.name_inp = inp('ชื่อสินค้า', self.product.get('name','') if self.product else '')
        form.addRow(lbl('ชื่อสินค้า *'), self.name_inp)

        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(40)
        self.category_combo.setStyleSheet(INPUT_STYLE)
        self.category_combo.addItem('-- ไม่ระบุ --', None)
        for c in self.categories:
            self.category_combo.addItem(c.get('name',''), c.get('id'))
        if self.product and self.product.get('category_id'):
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == self.product['category_id']:
                    self.category_combo.setCurrentIndex(i)
                    break
        form.addRow(lbl('หมวดหมู่'), self.category_combo)

        self.unit_combo = QComboBox()
        self.unit_combo.setFixedHeight(40)
        self.unit_combo.setStyleSheet(INPUT_STYLE)
        for u in UNITS:
            self.unit_combo.addItem(u)
        if self.product:
            idx = self.unit_combo.findText(self.product.get('unit','piece'))
            self.unit_combo.setCurrentIndex(max(0, idx))
        form.addRow(lbl('หน่วย *'), self.unit_combo)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 999999)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setFixedHeight(40)
        self.cost_spin.setStyleSheet(INPUT_STYLE)
        self.cost_spin.setValue(float(self.product.get('cost_price', 0)) if self.product else 0)
        form.addRow(lbl('ราคาทุน (฿)'), self.cost_spin)

        self.sell_spin = QDoubleSpinBox()
        self.sell_spin.setRange(0, 999999)
        self.sell_spin.setDecimals(2)
        self.sell_spin.setFixedHeight(40)
        self.sell_spin.setStyleSheet(INPUT_STYLE)
        self.sell_spin.setValue(float(self.product.get('selling_price', 0)) if self.product else 0)
        form.addRow(lbl('ราคาขาย (฿) *'), self.sell_spin)

        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(0, 99999)
        self.min_stock_spin.setFixedHeight(40)
        self.min_stock_spin.setStyleSheet(INPUT_STYLE)
        self.min_stock_spin.setValue(int(self.product.get('min_stock_level', 5)) if self.product else 5)
        form.addRow(lbl('สต๊อกขั้นต่ำ'), self.min_stock_spin)

        self.chem_inp = inp('เลขทะเบียน', self.product.get('chemical_registration','') if self.product else '')
        form.addRow(lbl('ทะเบียนสารเคมี'), self.chem_inp)

        self.active_check = QCheckBox('เปิดใช้งาน')
        self.active_check.setChecked(self.product.get('is_active', True) if self.product else True)
        self.active_check.setStyleSheet('color: #475569; font-size: 13px;')
        form.addRow(lbl('สถานะ'), self.active_check)

        layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('ยกเลิก')
        cancel_btn.setFixedHeight(44)
        cancel_btn.setStyleSheet(BUTTON_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        self.save_btn = QPushButton('💾  บันทึก')
        self.save_btn.setFixedHeight(44)
        self.save_btn.setFont(QFont('Sarabun', 12, QFont.Weight.Bold))
        self.save_btn.setStyleSheet(BUTTON_PRIMARY)
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

    def _save(self):
        code = self.code_inp.text().strip()
        name = self.name_inp.text().strip()
        if not code or not name:
            QMessageBox.warning(self, 'ข้อมูลไม่ครบ', 'กรุณากรอกรหัสและชื่อสินค้า')
            return

        data = {
            'code': code, 'name': name,
            'category_id': self.category_combo.currentData(),
            'unit': self.unit_combo.currentText(),
            'cost_price': self.cost_spin.value(),
            'selling_price': self.sell_spin.value(),
            'min_stock_level': self.min_stock_spin.value(),
            'chemical_registration': self.chem_inp.text().strip() or None,
            'is_active': self.active_check.isChecked(),
        }
        self.save_btn.setEnabled(False)
        self.save_btn.setText('กำลังบันทึก...')
        try:
            if self.product:
                self.api.update_product(self.product['id'], data)
            else:
                self.api.create_product(data)
            self.saved.emit()
            self.accept()
        except APIError as e:
            QMessageBox.critical(self, 'ข้อผิดพลาด', str(e))
            self.save_btn.setEnabled(True)
            self.save_btn.setText('💾  บันทึก')


class ProductsPage(QWidget):
    def __init__(self, api: APIClient, parent=None):
        super().__init__(parent)
        self.api = api
        self.products = []
        self.categories = []
        self.worker = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel('จัดการสินค้า')
        title.setFont(QFont('Sarabun', 22, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        sub = QLabel('รายการสินค้าทั้งหมด')
        sub.setStyleSheet('color: #64748b; font-size: 12px;')
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        add_btn = QPushButton('➕  เพิ่มสินค้า')
        add_btn.setFixedHeight(42)
        add_btn.setFont(QFont('Sarabun', 12, QFont.Weight.Bold))
        add_btn.setStyleSheet(BUTTON_PRIMARY)
        add_btn.clicked.connect(self._open_add)
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Search
        search_row = QHBoxLayout()
        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText('🔍  ค้นหาชื่อ รหัส บาร์โค้ด...')
        self.search_inp.setFixedHeight(42)
        self.search_inp.setStyleSheet(INPUT_STYLE)
        self.search_inp.setMaximumWidth(400)
        self.search_inp.returnPressed.connect(self.on_show)
        search_row.addWidget(self.search_inp)

        search_btn = QPushButton('ค้นหา')
        search_btn.setFixedHeight(42)
        search_btn.setStyleSheet(BUTTON_SECONDARY)
        search_btn.clicked.connect(self.on_show)
        search_row.addWidget(search_btn)
        search_row.addStretch()
        layout.addLayout(search_row)

        # Table
        table_card = QFrame()
        table_card.setObjectName('card')
        table_card.setStyleSheet(CARD_STYLE)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ชื่อสินค้า', 'รหัส', 'หมวดหมู่', 'ราคาทุน', 'ราคาขาย', 'หน่วย', 'สถานะ'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, 7):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.doubleClicked.connect(self._open_edit)
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)

        self.status_lbl = QLabel('กำลังโหลด...')
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet('color: #94a3b8; font-size: 12px;')
        layout.addWidget(self.status_lbl)

    def on_show(self):
        search = self.search_inp.text()
        if self.worker and self.worker.isRunning():
            return
        self.status_lbl.setText('กำลังโหลด...')
        # Load categories first
        try:
            self.categories = self.api.get_categories()
            if not isinstance(self.categories, list):
                self.categories = []
        except Exception:
            self.categories = []

        self.worker = ProductsWorker(self.api, search)
        self.worker.result.connect(self._on_data)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_data(self, products: list):
        self.products = products
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setRowHeight(row, 48)
            items = [
                (p.get('name', ''), '#1e293b', QFont.Weight.DemiBold),
                (p.get('code', ''), '#64748b', QFont.Weight.Normal),
                (p.get('category', {}).get('name', '-') if p.get('category') else '-', '#64748b', QFont.Weight.Normal),
                (f'฿{float(p.get("cost_price",0)):,.2f}', '#475569', QFont.Weight.Normal),
                (f'฿{float(p.get("selling_price",0)):,.2f}', '#10b981', QFont.Weight.Bold),
                (p.get('unit', ''), '#475569', QFont.Weight.Normal),
                ('ใช้งาน' if p.get('is_active') else 'ปิด', '#10b981' if p.get('is_active') else '#94a3b8', QFont.Weight.DemiBold),
            ]
            for col, (text, color, weight) in enumerate(items):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setFont(QFont('Sarabun', 12, weight))
                if col in [3, 4]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif col in [5, 6]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)

        self.status_lbl.setText(f'ทั้งหมด {len(products)} รายการ  (ดับเบิลคลิกเพื่อแก้ไข)')

    def _on_error(self, msg: str):
        self.status_lbl.setText(f'ข้อผิดพลาด: {msg}')

    def _open_add(self):
        dlg = ProductFormDialog(self.api, categories=self.categories, parent=self)
        dlg.saved.connect(self.on_show)
        dlg.exec()

    def _open_edit(self, index):
        row = index.row()
        if 0 <= row < len(self.products):
            product = self.products[row]
            dlg = ProductFormDialog(self.api, product=product, categories=self.categories, parent=self)
            dlg.saved.connect(self.on_show)
            dlg.exec()
