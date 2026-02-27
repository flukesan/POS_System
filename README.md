# AgriPOS - ระบบ POS สำหรับร้านค้าเกษตร

ระบบ Point of Sale (POS) สำหรับร้านจำหน่าย **ปุ๋ยเคมี สารเคมีเกษตร และเครื่องมือเกษตร** พัฒนาด้วย FastAPI + React + PostgreSQL

---

## คุณสมบัติหลัก

### 🛒 ระบบขายสินค้า (POS Terminal)
- หน้าจอขายที่ใช้งานง่าย รวดเร็ว
- **สแกน QR Code / Barcode** เพื่อค้นหาสินค้า
- คำนวณส่วนลด ภาษี และยอดรวมอัตโนมัติ
- รองรับหลายสินค้าในตะกร้าพร้อมกัน

### 💳 ระบบชำระเงิน
- **เงินสด** - คำนวณเงินทอนอัตโนมัติ
- **QR PromptPay** - สร้าง QR Code พร้อมระบุยอดเงิน (EMVCo standard)
- **เครดิต** - บันทึกและติดตามยอดค้าง
- ระบบยืนยันการรับเงิน + บันทึกหลักฐาน

### 📦 ระบบสต๊อก
- ติดตามจำนวนคงเหลือแบบ Real-time
- **รับสินค้าเข้า** ผ่าน Purchase Order
- บันทึก Lot Number, วันหมดอายุ
- แจ้งเตือนสินค้าใกล้หมด
- ปรับยอดสต๊อก (Stock Adjustment)

### 👥 ระบบลูกค้า & เครดิต
- ฐานข้อมูลลูกค้า + ข้อมูลแปลงเกษตร
- **กำหนดวงเงินเครดิต** รายลูกค้า
- ติดตามยอดค้างชำระ + วันครบกำหนด
- แจ้งเตือนลูกค้าที่เกินกำหนด
- ประวัติการซื้อ-ขาย

### 📊 ระบบรายงาน
- ยอดขายรายวัน / รายเดือน
- สินค้าขายดี (Top Products)
- รายงานเครดิตค้างชำระ
- มูลค่าสต๊อกสินค้า (ราคาทุน / ราคาขาย)
- Dashboard KPI แบบ Real-time

### 🗄️ ฐานข้อมูล PostgreSQL
- เก็บรูปภาพสินค้า (BYTEA + File Storage)
- ข้อมูลหลักฐานการโอนเงิน
- บันทึก Audit Log ทุก Transaction
- รองรับ UUID, JSONB, Timezone

---

## โครงสร้างโปรเจค

```
POS_System/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API Endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── products.py    # สินค้า + QR
│   │   │   ├── stock.py       # สต๊อก + รับของ
│   │   │   ├── sales.py       # ขายสินค้า + ชำระเงิน
│   │   │   ├── customers.py   # ลูกค้า + เครดิต
│   │   │   └── reports.py     # รายงาน
│   │   ├── models/            # SQLAlchemy Models
│   │   ├── services/
│   │   │   └── qr_service.py  # QR Code Generator
│   │   ├── core/
│   │   │   ├── config.py      # Settings
│   │   │   └── security.py    # JWT Auth
│   │   └── main.py            # App Entry Point
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── pos/           # POS Terminal Components
│   │   │   │   ├── POSTerminal.tsx
│   │   │   │   ├── ProductGrid.tsx
│   │   │   │   ├── CartPanel.tsx
│   │   │   │   ├── PaymentModal.tsx
│   │   │   │   └── QRScannerModal.tsx
│   │   │   ├── customer/      # Customer Components
│   │   │   └── layout/        # Sidebar, Header
│   │   ├── pages/             # Route Pages
│   │   ├── store/             # Zustand State
│   │   ├── services/          # API Calls
│   │   ├── types/             # TypeScript Types
│   │   └── utils/             # Helpers
│   ├── Dockerfile
│   └── nginx.conf
│
├── database/
│   ├── 01_schema.sql          # Tables, Indexes, Triggers
│   └── 02_seed.sql            # Initial Data
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## การติดตั้งและเริ่มใช้งาน

### เริ่มต้นด้วย Docker (แนะนำ)

```bash
cp .env.example .env
docker compose up -d
# Frontend:  http://localhost
# API Docs:  http://localhost:8000/api/docs
```

### รันแบบ Development

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

---

## Default Login

| Username | Password |
|----------|----------|
| `admin`  | `admin1234` |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (Async) |
| Cache | Redis |
| Frontend | React 18 + TypeScript |
| State | Zustand |
| Queries | TanStack Query v5 |
| Styling | Tailwind CSS |
| Charts | Recharts |
| QR Code | qrcode (Python) + html5-qrcode |
| Deploy | Docker + Nginx |
| Auth | JWT (python-jose) |
