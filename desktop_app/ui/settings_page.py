"""
Settings Page — Printer + Cash Drawer config
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QComboBox,
    QGroupBox, QFormLayout, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.printer import PrinterService
from ui.styles import INPUT_STYLE, BUTTON_PRIMARY, BUTTON_SECONDARY, CARD_STYLE
import os


class SettingsPage(QWidget):
    def __init__(self, printer: PrinterService, parent=None):
        super().__init__(parent)
        self.printer = printer
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

        title = QLabel('⚙️  ตั้งค่าระบบ')
        title.setFont(QFont('Sarabun', 22, QFont.Weight.Bold))
        title.setStyleSheet('color: #0f172a;')
        layout.addWidget(title)

        # ── Printer section ────────────────────────────────────
        printer_card = QFrame()
        printer_card.setObjectName('card')
        printer_card.setStyleSheet(CARD_STYLE)
        p_layout = QVBoxLayout(printer_card)
        p_layout.setContentsMargins(20, 16, 20, 20)
        p_layout.setSpacing(14)

        p_title = QLabel('🖨️  เครื่องพิมพ์ใบเสร็จ (Thermal Printer)')
        p_title.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        p_title.setStyleSheet('color: #0f172a;')
        p_layout.addWidget(p_title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet('color: #475569; font-size: 12px; font-weight: 600;')
            return l

        self.printer_type = QComboBox()
        self.printer_type.setFixedHeight(40)
        self.printer_type.setStyleSheet(INPUT_STYLE)
        self.printer_type.addItems(['USB', 'Serial (COM Port)', 'Network (LAN)'])
        current = os.getenv('PRINTER_TYPE', 'usb').lower()
        idx = {'usb': 0, 'serial': 1, 'network': 2}.get(current, 0)
        self.printer_type.setCurrentIndex(idx)
        form.addRow(lbl('ประเภทการเชื่อมต่อ'), self.printer_type)

        self.vendor_inp = QLineEdit(os.getenv('PRINTER_VENDOR_ID', '0x04b8'))
        self.vendor_inp.setFixedHeight(40)
        self.vendor_inp.setStyleSheet(INPUT_STYLE)
        form.addRow(lbl('Vendor ID (USB)'), self.vendor_inp)

        self.product_inp = QLineEdit(os.getenv('PRINTER_PRODUCT_ID', '0x0e15'))
        self.product_inp.setFixedHeight(40)
        self.product_inp.setStyleSheet(INPUT_STYLE)
        form.addRow(lbl('Product ID (USB)'), self.product_inp)

        self.port_inp = QLineEdit(os.getenv('PRINTER_PORT', 'COM3'))
        self.port_inp.setFixedHeight(40)
        self.port_inp.setStyleSheet(INPUT_STYLE)
        form.addRow(lbl('COM Port (Serial)'), self.port_inp)

        self.net_host_inp = QLineEdit(os.getenv('PRINTER_HOST', '192.168.1.100'))
        self.net_host_inp.setFixedHeight(40)
        self.net_host_inp.setStyleSheet(INPUT_STYLE)
        form.addRow(lbl('IP Address (Network)'), self.net_host_inp)

        p_layout.addLayout(form)

        btn_row = QHBoxLayout()
        connect_btn = QPushButton('🔌  เชื่อมต่อเครื่องพิมพ์')
        connect_btn.setFixedHeight(42)
        connect_btn.setStyleSheet(BUTTON_PRIMARY)
        connect_btn.clicked.connect(self._connect_printer)
        btn_row.addWidget(connect_btn)

        test_btn = QPushButton('🖨️  พิมพ์ทดสอบ')
        test_btn.setFixedHeight(42)
        test_btn.setStyleSheet(BUTTON_SECONDARY)
        test_btn.clicked.connect(self._test_print)
        btn_row.addWidget(test_btn)

        drawer_btn = QPushButton('💰  เปิดลิ้นชักเงิน')
        drawer_btn.setFixedHeight(42)
        drawer_btn.setStyleSheet(BUTTON_SECONDARY)
        drawer_btn.clicked.connect(self._open_drawer)
        btn_row.addWidget(drawer_btn)
        p_layout.addLayout(btn_row)

        self.printer_status = QLabel('สถานะ: ยังไม่ได้เชื่อมต่อ')
        self.printer_status.setStyleSheet('color: #94a3b8; font-size: 12px; padding: 8px 0;')
        p_layout.addWidget(self.printer_status)

        layout.addWidget(printer_card)

        # ── API Config section ─────────────────────────────────
        api_card = QFrame()
        api_card.setObjectName('card')
        api_card.setStyleSheet(CARD_STYLE)
        api_layout = QVBoxLayout(api_card)
        api_layout.setContentsMargins(20, 16, 20, 20)
        api_layout.setSpacing(14)

        api_title = QLabel('🌐  การเชื่อมต่อ Server')
        api_title.setFont(QFont('Sarabun', 14, QFont.Weight.Bold))
        api_title.setStyleSheet('color: #0f172a;')
        api_layout.addWidget(api_title)

        api_form = QFormLayout()
        api_form.setSpacing(10)
        api_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.api_url_inp = QLineEdit(os.getenv('API_URL', 'http://localhost:8000/api/v1'))
        self.api_url_inp.setFixedHeight(40)
        self.api_url_inp.setStyleSheet(INPUT_STYLE)
        api_form.addRow(lbl('API URL'), self.api_url_inp)
        api_layout.addLayout(api_form)

        save_api_btn = QPushButton('💾  บันทึกการตั้งค่า')
        save_api_btn.setFixedHeight(42)
        save_api_btn.setStyleSheet(BUTTON_PRIMARY)
        save_api_btn.clicked.connect(self._save_settings)
        api_layout.addWidget(save_api_btn)
        layout.addWidget(api_card)

        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _connect_printer(self):
        ptype = ['usb','serial','network'][self.printer_type.currentIndex()]
        os.environ['PRINTER_TYPE'] = ptype
        os.environ['PRINTER_VENDOR_ID'] = self.vendor_inp.text()
        os.environ['PRINTER_PRODUCT_ID'] = self.product_inp.text()
        os.environ['PRINTER_PORT'] = self.port_inp.text()
        os.environ['PRINTER_HOST'] = self.net_host_inp.text()

        # Reinit printer with new settings
        self.printer.printer_type = ptype
        ok = self.printer.connect()
        if ok:
            self.printer_status.setText('✅  เชื่อมต่อสำเร็จ')
            self.printer_status.setStyleSheet('color: #10b981; font-size: 12px;')
        else:
            self.printer_status.setText('❌  เชื่อมต่อไม่สำเร็จ — ตรวจสอบการเชื่อมต่อและ driver')
            self.printer_status.setStyleSheet('color: #ef4444; font-size: 12px;')

    def _test_print(self):
        if not self.printer.is_connected():
            QMessageBox.warning(self, 'ไม่ได้เชื่อมต่อ', 'กรุณาเชื่อมต่อเครื่องพิมพ์ก่อน')
            return
        ok = self.printer.print_test()
        if ok:
            QMessageBox.information(self, 'สำเร็จ', '✅ พิมพ์ทดสอบสำเร็จ')
        else:
            QMessageBox.critical(self, 'ข้อผิดพลาด', '❌ พิมพ์ไม่สำเร็จ — ตรวจสอบเครื่องพิมพ์')

    def _open_drawer(self):
        ok = self.printer.open_cash_drawer()
        if ok:
            QMessageBox.information(self, 'สำเร็จ', '✅ เปิดลิ้นชักเงินสำเร็จ')
        else:
            QMessageBox.warning(self, 'ไม่สำเร็จ', '❌ ไม่สามารถเปิดลิ้นชักได้\nตรวจสอบการเชื่อมต่อ')

    def _save_settings(self):
        # Write to .env file
        env_path = '.env'
        lines = []
        settings = {
            'API_URL': self.api_url_inp.text(),
            'PRINTER_TYPE': ['usb','serial','network'][self.printer_type.currentIndex()],
            'PRINTER_VENDOR_ID': self.vendor_inp.text(),
            'PRINTER_PRODUCT_ID': self.product_inp.text(),
            'PRINTER_PORT': self.port_inp.text(),
            'PRINTER_HOST': self.net_host_inp.text(),
        }
        try:
            with open(env_path, 'w') as f:
                for k, v in settings.items():
                    f.write(f'{k}={v}\n')
            QMessageBox.information(self, 'สำเร็จ', '✅ บันทึกการตั้งค่าแล้ว\n(จะมีผลเมื่อเปิดโปรแกรมใหม่)')
        except Exception as e:
            QMessageBox.warning(self, 'ข้อผิดพลาด', f'ไม่สามารถบันทึกได้: {e}')

    def on_show(self):
        if self.printer.is_connected():
            self.printer_status.setText('✅  เชื่อมต่ออยู่')
            self.printer_status.setStyleSheet('color: #10b981; font-size: 12px;')
