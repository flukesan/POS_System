"""
Customers Management Page
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox,
    QMessageBox, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from services.api_client import APIClient, APIError
from ui.styles import INPUT_STYLE, BUTTON_PRIMARY, BUTTON_SECONDARY, TABLE_STYLE, CARD_STYLE


class CustomersWorker(QThread):
    result = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api: APIClient, search=''):
        super().__init__()
        self.api = api
        self.search = search

    def run(self):
        try:
            data = self.api.get_customers(self.search)
            self.result.emit(data if isinstance(data, list) else [])
        except Exception as e:
            self.error.emit(str(e))


class CustomerFormDialog(QDialog):
    saved = pyqtSignal()

    def __init__(self, api: APIClient, customer: dict = None, parent=None):
        super().__init__(parent)
        self.api = api
        self.customer = customer
        self.setWindowTitle('แก้ไขลูกค้า' if customer else 'เพิ่มลูกค้าใหม่')
        self.setFixedWidth(480)
        self.setStyleSheet('QDialog { background: #ffffff; }')
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel('แก้ไขลูกค้า' if self.customer else '👤  เพิ่มลูกค้าใหม่')
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

        self.name_inp = inp('ชื่อ-นามสกุล / ชื่อบริษัท', self.customer.get('name','') if self.customer else '')
        form.addRow(lbl('ชื่อลูกค้า *'), self.name_inp)

        self.phone_inp = inp('08x-xxxxxxx', self.customer.get('phone','') if self.customer else '')
        form.addRow(lbl('เบอร์โทรศัพท์'), self.phone_inp)

        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(40)
        self.type_combo.setStyleSheet(INPUT_STYLE)
        types = [('individual','บุคคลทั่วไป'),('farmer','เกษตรกร'),('corporate','นิติบุคคล')]
        for val, text in types:
            self.type_combo.addItem(text, val)
        if self.customer:
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == self.customer.get('customer_type','individual'):
                    self.type_combo.setCurrentIndex(i); break
        form.addRow(lbl('ประเภทลูกค้า'), self.type_combo)

        self.address_inp = inp('ที่อยู่', self.customer.get('address','') if self.customer else '')
        form.addRow(lbl('ที่อยู่'), self.address_inp)

        self.credit_spin = QDoubleSpinBox()
        self.credit_spin.setRange(0, 9999999)
        self.credit_spin.setDecimals(2)
        self.credit_spin.setFixedHeight(40)
        self.credit_spin.setStyleSheet(INPUT_STYLE)
        self.credit_spin.setValue(float(self.customer.get('credit_limit',0)) if self.customer else 0)
        form.addRow(lbl('วงเงินเครดิต (฿)'), self.credit_spin)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(0, 365)
        self.days_spin.setFixedHeight(40)
        self.days_spin.setStyleSheet(INPUT_STYLE)
        self.days_spin.setValue(int(self.customer.get('credit_days',30)) if self.customer else 30)
        form.addRow(lbl('จำนวนวันเครดิต'), self.days_spin)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('ยกเลิก')
        cancel_btn.setFixedHeight(44)
        cancel_btn.setStyleSheet(BUTTON_SECONDARY)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        self.save_btn = QPushButton('💾  บันทึก')
        self.save_btn.setFixedHeight(44)
        self.save_btn.setFont(QFont('Sarabun', 12, QFont.Weight.Bold))
        self.save_btn.setStyleSheet(BUTTON_PRIMARY.replace('#10b981','#6366f1').replace('#0d9488','#8b5cf6').replace('#059669','#4f46e5').replace('#0f766e','#7c3aed').replace('#047857','#4338ca').replace('#0d6b6b','#6d28d9'))
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

    def _save(self):
        name = self.name_inp.text().strip()
        if not name:
            QMessageBox.warning(self, 'ข้อมูลไม่ครบ', 'กรุณากรอกชื่อลูกค้า')
            return
        data = {
            'name': name,
            'phone': self.phone_inp.text().strip() or None,
            'address': self.address_inp.text().strip() or None,
            'customer_type': self.type_combo.currentData(),
            'credit_limit': self.credit_spin.value(),
            'credit_days': self.days_spin.value(),
        }
        self.save_btn.setEnabled(False)
        self.save_btn.setText('กำลังบันทึก...')
        try:
            if self.customer:
                self.api.update_customer(self.customer['id'], data)
            else:
                self.api.create_customer(data)
            self.saved.emit()
            self.accept()
        except APIError as e:
            QMessageBox.critical(self, 'ข้อผิดพลาด', str(e))
            self.save_btn.setEnabled(True)
            self.save_btn.setText('💾  บันทึก')


class CustomersPage(QWidget):
    def __init__(self, api: APIClient, parent=None):
        super().__init__(parent)
        self.api = api
        self.customers = []
        self.worker = None
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel('ลูกค้า / เครดิต')
        title.setFont(QFont('Sarabun', 22, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        sub = QLabel('จัดการข้อมูลลูกค้าและวงเงินเครดิต')
        sub.setStyleSheet('color: #64748b; font-size: 12px;')
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()

        add_btn = QPushButton('➕  เพิ่มลูกค้า')
        add_btn.setFixedHeight(42)
        add_btn.setFont(QFont('Sarabun', 12, QFont.Weight.Bold))
        add_btn.setStyleSheet(BUTTON_PRIMARY.replace('#10b981','#6366f1').replace('#0d9488','#8b5cf6').replace('#059669','#4f46e5').replace('#0f766e','#7c3aed').replace('#047857','#4338ca').replace('#0d6b6b','#6d28d9'))
        add_btn.clicked.connect(self._open_add)
        header.addWidget(add_btn)
        layout.addLayout(header)

        search_row = QHBoxLayout()
        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText('🔍  ค้นหาชื่อ / เบอร์โทร...')
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

        table_card = QFrame()
        table_card.setObjectName('card')
        table_card.setStyleSheet(CARD_STYLE)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ชื่อลูกค้า', 'รหัส', 'เบอร์โทร', 'วงเงินเครดิต', 'สถานะ'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, 5):
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
        self.worker = CustomersWorker(self.api, search)
        self.worker.result.connect(self._on_data)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    STATUS_COLOR = {'active':'#10b981','overdue':'#ef4444','suspended':'#94a3b8','paid':'#3b82f6'}
    STATUS_LABEL = {'active':'ปกติ','overdue':'เกินกำหนด','suspended':'ระงับ','paid':'ชำระแล้ว'}

    def _on_data(self, customers: list):
        self.customers = customers
        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table.setRowHeight(row, 48)
            status = c.get('credit_status','active')
            items_data = [
                (c.get('name',''), '#1e293b', QFont.Weight.DemiBold),
                (c.get('code',''), '#64748b', QFont.Weight.Normal),
                (c.get('phone','-') or '-', '#64748b', QFont.Weight.Normal),
                (f'฿{float(c.get("credit_limit",0)):,.0f}', '#475569', QFont.Weight.Normal),
                (self.STATUS_LABEL.get(status,''), self.STATUS_COLOR.get(status,'#94a3b8'), QFont.Weight.DemiBold),
            ]
            for col, (text, color, weight) in enumerate(items_data):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setFont(QFont('Sarabun', 12, weight))
                if col in [3,4]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
        self.status_lbl.setText(f'ทั้งหมด {len(customers)} ราย  (ดับเบิลคลิกเพื่อแก้ไข)')

    def _on_error(self, msg: str):
        self.status_lbl.setText(f'ข้อผิดพลาด: {msg}')

    def _open_add(self):
        dlg = CustomerFormDialog(self.api, parent=self)
        dlg.saved.connect(self.on_show)
        dlg.exec()

    def _open_edit(self, index):
        row = index.row()
        if 0 <= row < len(self.customers):
            dlg = CustomerFormDialog(self.api, customer=self.customers[row], parent=self)
            dlg.saved.connect(self.on_show)
            dlg.exec()
