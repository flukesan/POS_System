# AgriPOS Desktop App (PyQt6)

## โครงสร้าง
```
desktop_app/
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── run.bat                  # Windows launcher
├── .env.example             # ตัวอย่างการตั้งค่า
├── services/
│   ├── api_client.py        # HTTP client → FastAPI backend
│   └── printer.py           # ESC/POS + Cash Drawer
└── ui/
    ├── styles.py            # QSS stylesheet ทั้งหมด
    ├── login_window.py      # หน้า Login
    ├── main_window.py       # หน้าหลัก + sidebar
    ├── pos_terminal.py      # หน้าขายสินค้า
    ├── dashboard_page.py    # แดชบอร์ด
    ├── products_page.py     # จัดการสินค้า
    ├── customers_page.py    # จัดการลูกค้า
    └── settings_page.py     # ตั้งค่าเครื่องพิมพ์
```

## ข้อกำหนด
- Python 3.11+
- Windows 10/11 (หรือ Linux/macOS)
- FastAPI backend รันอยู่ (Docker)

## วิธีติดตั้ง

### 1. ติดตั้ง Python (ถ้ายังไม่มี)
ดาวน์โหลดที่ https://www.python.org/downloads/

### 2. ติดตั้งฟอนต์ภาษาไทย (แนะนำ)
ดาวน์โหลด Sarabun font จาก Google Fonts
ติดตั้งลงในระบบ Windows

### 3. เริ่ม Backend ก่อน
```bat
cd POS_System
docker compose up -d
```

### 4. เปิด Desktop App
```bat
cd desktop_app
run.bat
```
สคริปต์จะติดตั้ง dependencies อัตโนมัติ

## ตั้งค่าไฟล์ .env
```env
API_URL=http://localhost:8000/api/v1

# Thermal Printer (USB - Epson, Star, etc.)
PRINTER_TYPE=usb
PRINTER_VENDOR_ID=0x04b8   # Epson
PRINTER_PRODUCT_ID=0x0e15

# หรือ Serial
# PRINTER_TYPE=serial
# PRINTER_PORT=COM3
# PRINTER_BAUDRATE=9600

# Cash Drawer (ถ้าแยก port จากเครื่องพิมพ์)
# CASH_DRAWER_PORT=COM4
```

## Vendor ID ของเครื่องพิมพ์ยอดนิยม
| ยี่ห้อ | Vendor ID |
|--------|-----------|
| Epson  | 0x04b8    |
| Star   | 0x0519    |
| Bixolon| 0x1504    |
| Sewoo  | 0x0dd4    |

Product ID ดูได้จาก Device Manager > USB

## Login
- **Username:** admin
- **Password:** admin1234
