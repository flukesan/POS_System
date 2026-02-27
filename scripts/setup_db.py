"""
Local Database Setup Script
Run: python scripts/setup_db.py

This script:
1. Creates posuser + posdb in PostgreSQL
2. Runs schema SQL
3. Seeds initial data (admin user with correct password hash)
"""
import subprocess
import sys
import os
import getpass

def run_psql(command, dbname="postgres", user="postgres", password=None, host="localhost", port="5432"):
    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password
    result = subprocess.run(
        ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname, "-c", command],
        capture_output=True, text=True, env=env
    )
    return result

def run_psql_file(filepath, dbname="posdb", user="posuser", password="pospassword", host="localhost", port="5432"):
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    result = subprocess.run(
        ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname, "-f", filepath],
        capture_output=True, text=True, env=env
    )
    return result

def main():
    print("=" * 50)
    print("  AgriPOS - Database Setup")
    print("=" * 50)

    pg_password = getpass.getpass("Enter PostgreSQL superuser (postgres) password: ")

    host = input("PostgreSQL host [localhost]: ").strip() or "localhost"
    port = input("PostgreSQL port [5432]: ").strip() or "5432"

    print("\n[1/4] Creating posuser role...")
    r = run_psql(
        "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='posuser') THEN "
        "CREATE ROLE posuser WITH LOGIN PASSWORD 'pospassword'; END IF; END $$;",
        user="postgres", password=pg_password, host=host, port=port
    )
    if r.returncode != 0 and "already exists" not in r.stderr:
        print(f"    Error: {r.stderr}")
    else:
        print("    OK")

    print("[2/4] Creating posdb database...")
    r = run_psql(
        "SELECT 'CREATE DATABASE posdb OWNER posuser' WHERE NOT EXISTS "
        "(SELECT FROM pg_database WHERE datname='posdb')\\gexec",
        user="postgres", password=pg_password, host=host, port=port
    )
    # Try direct create as fallback
    r2 = run_psql("GRANT ALL PRIVILEGES ON DATABASE posdb TO posuser;",
                  user="postgres", password=pg_password, host=host, port=port)
    print("    OK")

    # Enable extensions
    print("[3/4] Running schema...")
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "01_schema.sql")
    r = run_psql_file(schema_path, dbname="posdb", user="posuser", password="pospassword", host=host, port=port)
    if r.returncode != 0:
        print(f"    Warning: {r.stderr[:200]}")
    else:
        print("    OK")

    print("[4/4] Seeding initial data...")
    # Use passlib to generate correct bcrypt hash instead of pgcrypto
    try:
        from passlib.context import CryptContext
        pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pw = pwd_ctx.hash("admin1234")

        import uuid
        seed_sql = f"""
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Admin user
INSERT INTO users (id, username, email, hashed_password, full_name, role)
SELECT uuid_generate_v4(), 'admin', 'admin@agripos.local', '{hashed_pw}', 'ผู้ดูแลระบบ', 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- Warehouse
INSERT INTO warehouses (id, code, name, address)
SELECT uuid_generate_v4(), 'WH-001', 'คลังสินค้าหลัก', 'ร้านเกษตรภัณฑ์ - สาขาหลัก'
WHERE NOT EXISTS (SELECT 1 FROM warehouses WHERE code = 'WH-001');

-- Categories
INSERT INTO categories (id, name, name_en, sort_order)
SELECT uuid_generate_v4(), v.name, v.name_en, v.sort_order
FROM (VALUES
    ('ปุ๋ยเคมี','Chemical Fertilizer',1),
    ('ปุ๋ยอินทรีย์','Organic Fertilizer',2),
    ('ยาฆ่าแมลง','Insecticide',3),
    ('ยาฆ่าหญ้า','Herbicide',4),
    ('ยาฆ่าเชื้อรา','Fungicide',5),
    ('เมล็ดพันธุ์','Seeds',6),
    ('เครื่องมือเกษตร','Agricultural Tools',7),
    ('อุปกรณ์ชลประทาน','Irrigation Equipment',8),
    ('อุปกรณ์ป้องกัน','Protective Equipment',9),
    ('อื่นๆ','Others',10)
) AS v(name, name_en, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE categories.name = v.name);

-- Bank account
INSERT INTO bank_accounts (bank_name, account_name, account_number, promptpay_id, is_default)
SELECT 'ธนาคารกสิกรไทย', 'ร้านเกษตรภัณฑ์', '123-4-56789-0', '0812345678', TRUE
WHERE NOT EXISTS (SELECT 1 FROM bank_accounts WHERE promptpay_id = '0812345678');

-- Settings
INSERT INTO settings (key, value, description)
SELECT v.key, v.value, v.description
FROM (VALUES
    ('shop_name','ร้านเกษตรภัณฑ์','ชื่อร้านค้า'),
    ('shop_phone','053-123456','เบอร์โทรร้านค้า'),
    ('default_tax_rate','7','ภาษีมูลค่าเพิ่มเริ่มต้น (%)'),
    ('currency','THB','สกุลเงิน'),
    ('receipt_footer','ขอบคุณที่ใช้บริการ','ข้อความท้ายใบเสร็จ'),
    ('low_stock_alert','10','แจ้งเตือนสต๊อกต่ำ')
) AS v(key, value, description)
WHERE NOT EXISTS (SELECT 1 FROM settings WHERE settings.key = v.key);
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
            f.write(seed_sql)
            tmp_path = f.name

        r = run_psql_file(tmp_path, dbname="posdb", user="posuser", password="pospassword", host=host, port=port)
        os.unlink(tmp_path)

        if r.returncode != 0:
            print(f"    Warning: {r.stderr[:300]}")
        else:
            print("    OK")
    except ImportError:
        print("    passlib not installed. Run: pip install passlib[bcrypt]")
        print("    Then re-run this script.")
        sys.exit(1)

    print()
    print("=" * 50)
    print("  Database setup complete!")
    print()
    print("  Login: admin / admin1234")
    print("=" * 50)

    print()
    print("Now create backend/.env:")
    print(f"""
DATABASE_URL=postgresql+asyncpg://posuser:pospassword@{host}:{port}/posdb
SECRET_KEY=local-dev-secret-key-12345
DEBUG=true
UPLOAD_DIR=./uploads
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
""")

if __name__ == "__main__":
    main()
