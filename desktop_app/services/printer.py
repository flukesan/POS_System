"""
ESC/POS Thermal Printer + Cash Drawer Service
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PrinterService:
    """Handles ESC/POS thermal printer and cash drawer."""

    def __init__(self):
        self.printer = None
        self.printer_type = os.getenv('PRINTER_TYPE', 'usb')  # usb | serial | network
        self.vendor_id = int(os.getenv('PRINTER_VENDOR_ID', '0x04b8'), 16)
        self.product_id = int(os.getenv('PRINTER_PRODUCT_ID', '0x0e15'), 16)
        self.serial_port = os.getenv('PRINTER_PORT', 'COM3')
        self.baudrate = int(os.getenv('PRINTER_BAUDRATE', '9600'))
        self.cash_drawer_port = os.getenv('CASH_DRAWER_PORT', '')

    def connect(self) -> bool:
        """Connect to printer. Returns True if successful."""
        try:
            from escpos.printer import Usb, Serial, Network
            if self.printer_type == 'usb':
                self.printer = Usb(self.vendor_id, self.product_id)
            elif self.printer_type == 'serial':
                self.printer = Serial(self.serial_port, baudrate=self.baudrate)
            elif self.printer_type == 'network':
                host = os.getenv('PRINTER_HOST', '192.168.1.100')
                self.printer = Network(host)
            logger.info(f'Printer connected: {self.printer_type}')
            return True
        except ImportError:
            logger.warning('python-escpos not installed')
            return False
        except Exception as e:
            logger.error(f'Printer connection failed: {e}')
            return False

    def is_connected(self) -> bool:
        return self.printer is not None

    def print_receipt(self, order: Dict, shop_info: Dict) -> bool:
        """Print a sales receipt."""
        if not self.printer:
            logger.warning('Printer not connected, skipping print')
            return False
        try:
            p = self.printer
            shop_name = shop_info.get('shop_name', 'ร้านเกษตรภัณฑ์')
            shop_address = shop_info.get('shop_address', '')
            shop_phone = shop_info.get('shop_phone', '')
            footer = shop_info.get('receipt_footer', 'ขอบคุณที่ใช้บริการ')

            # Header
            p.set(align='center', bold=True, width=2, height=2)
            p.text(f'{shop_name}\n')
            p.set(align='center', bold=False, width=1, height=1)
            if shop_address:
                p.text(f'{shop_address}\n')
            if shop_phone:
                p.text(f'โทร: {shop_phone}\n')
            p.text('-' * 32 + '\n')

            # Order info
            p.set(align='left')
            now = datetime.now().strftime('%d/%m/%Y %H:%M')
            p.text(f'เลขที่: {order.get("order_number", "")}\n')
            p.text(f'วันที่: {now}\n')
            if order.get('customer'):
                p.text(f'ลูกค้า: {order["customer"]["name"]}\n')
            p.text('-' * 32 + '\n')

            # Items
            for item in order.get('items', []):
                name = item.get('product_name', item.get('name', ''))
                qty = item.get('quantity', 0)
                price = item.get('unit_price', 0)
                total = item.get('total_amount', 0)
                p.text(f'{name[:20]}\n')
                p.text(f'  {qty} x {price:,.2f}'.ljust(24) + f'{total:>8,.2f}\n')

            p.text('-' * 32 + '\n')

            # Totals
            subtotal = order.get('subtotal', 0)
            discount = order.get('discount_amount', 0)
            tax = order.get('tax_amount', 0)
            total = order.get('total_amount', 0)
            paid = order.get('paid_amount', 0)
            change = order.get('change_amount', 0)

            p.text(f'{"ยอดรวม":16}{subtotal:>16,.2f}\n')
            if discount > 0:
                p.text(f'{"ส่วนลด":16}{-discount:>16,.2f}\n')
            p.text(f'{"ภาษี 7%":16}{tax:>16,.2f}\n')
            p.set(bold=True)
            p.text(f'{"ยอดชำระ":16}{total:>16,.2f}\n')
            p.set(bold=False)
            p.text(f'{"รับเงิน":16}{paid:>16,.2f}\n')
            p.text(f'{"เงินทอน":16}{change:>16,.2f}\n')
            p.text('-' * 32 + '\n')

            # Payment method
            method_map = {
                'cash': 'เงินสด', 'qr_promptpay': 'QR PromptPay',
                'bank_transfer': 'โอนเงิน', 'credit': 'เครดิต'
            }
            method = method_map.get(order.get('payment_method', 'cash'), '')
            if method:
                p.text(f'วิธีชำระ: {method}\n')

            # Footer
            p.set(align='center')
            p.text(f'\n{footer}\n\n')
            p.cut()
            return True

        except Exception as e:
            logger.error(f'Print error: {e}')
            return False

    def open_cash_drawer(self) -> bool:
        """Open cash drawer via printer or serial port."""
        # Method 1: Via ESC/POS printer (most common)
        if self.printer:
            try:
                self.printer.cashdraw(2)  # Pin 2
                return True
            except Exception as e:
                logger.error(f'Cash drawer via printer failed: {e}')

        # Method 2: Via separate serial port
        if self.cash_drawer_port:
            try:
                import serial
                with serial.Serial(self.cash_drawer_port, 9600, timeout=1) as ser:
                    ser.write(b'\x1B\x70\x00\x19\xFA')  # ESC p 0
                return True
            except Exception as e:
                logger.error(f'Cash drawer via serial failed: {e}')

        return False

    def print_test(self) -> bool:
        """Print a test page."""
        if not self.printer:
            return False
        try:
            p = self.printer
            p.set(align='center', bold=True)
            p.text('AgriPOS\n')
            p.set(bold=False)
            p.text('Test Print OK\n')
            p.text(datetime.now().strftime('%d/%m/%Y %H:%M:%S') + '\n')
            p.cut()
            return True
        except Exception as e:
            logger.error(f'Test print error: {e}')
            return False
