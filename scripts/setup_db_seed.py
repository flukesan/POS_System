"""
Seed database with initial data using passlib for password hashing.
This ensures the password hash format is compatible with FastAPI's passlib verification.
"""
import sys
import os

try:
    from passlib.context import CryptContext
except ImportError:
    print("Installing passlib...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "passlib[bcrypt]"])
    from passlib.context import CryptContext

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

# Generate password hash compatible with passlib
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pw = pwd_ctx.hash("admin1234")

print(f"  Generated bcrypt hash for admin1234")

# Connect to DB
try:
    conn = psycopg2.connect(
        dbname="posdb",
        user="posuser",
        password="pospassword",
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Enable extensions
    cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    cur.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";")

    # Admin user
    cur.execute("""
        INSERT INTO users (id, username, email, hashed_password, full_name, role)
        SELECT uuid_generate_v4(), 'admin', 'admin@agripos.local', %s, 'ผู้ดูแลระบบ', 'admin'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');
    """, (hashed_pw,))
    print("  ✓ Admin user created (username: admin, password: admin1234)")

    # Warehouse
    cur.execute("""
        INSERT INTO warehouses (id, code, name, address)
        SELECT uuid_generate_v4(), 'WH-001', 'คลังสินค้าหลัก', 'ร้านเกษตรภัณฑ์ - สาขาหลัก'
        WHERE NOT EXISTS (SELECT 1 FROM warehouses WHERE code = 'WH-001');
    """)

    # Categories
    categories = [
        ('ปุ๋ยเคมี', 'Chemical Fertilizer', 1),
        ('ปุ๋ยอินทรีย์', 'Organic Fertilizer', 2),
        ('ยาฆ่าแมลง', 'Insecticide', 3),
        ('ยาฆ่าหญ้า', 'Herbicide', 4),
        ('ยาฆ่าเชื้อรา', 'Fungicide', 5),
        ('เมล็ดพันธุ์', 'Seeds', 6),
        ('เครื่องมือเกษตร', 'Agricultural Tools', 7),
        ('อุปกรณ์ชลประทาน', 'Irrigation Equipment', 8),
        ('อุปกรณ์ป้องกัน', 'Protective Equipment', 9),
        ('อื่นๆ', 'Others', 10),
    ]
    for name, name_en, order in categories:
        cur.execute("""
            INSERT INTO categories (id, name, name_en, sort_order)
            SELECT uuid_generate_v4(), %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = %s);
        """, (name, name_en, order, name))
    print("  ✓ Categories created")

    # Bank account
    cur.execute("""
        INSERT INTO bank_accounts (bank_name, account_name, account_number, promptpay_id, is_default)
        SELECT 'ธนาคารกสิกรไทย', 'ร้านเกษตรภัณฑ์', '123-4-56789-0', '0812345678', TRUE
        WHERE NOT EXISTS (SELECT 1 FROM bank_accounts WHERE promptpay_id = '0812345678');
    """)

    # Settings
    settings_data = [
        ('shop_name', 'ร้านเกษตรภัณฑ์', 'ชื่อร้านค้า'),
        ('shop_phone', '053-123456', 'เบอร์โทรร้านค้า'),
        ('default_tax_rate', '7', 'ภาษีมูลค่าเพิ่มเริ่มต้น (%)'),
        ('currency', 'THB', 'สกุลเงิน'),
        ('receipt_footer', 'ขอบคุณที่ใช้บริการ', 'ข้อความท้ายใบเสร็จ'),
        ('low_stock_alert', '10', 'แจ้งเตือนสต๊อกต่ำ'),
        ('credit_default_days', '30', 'จำนวนวันเครดิตเริ่มต้น'),
    ]
    for key, value, desc in settings_data:
        cur.execute("""
            INSERT INTO settings (key, value, description)
            SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM settings WHERE key = %s);
        """, (key, value, desc, key))
    print("  ✓ Settings created")

    cur.close()
    conn.close()
    print("\nSeed data inserted successfully!")

except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure PostgreSQL is running and posdb/posuser exists.")
    sys.exit(1)
