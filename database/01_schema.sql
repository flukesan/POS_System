-- ============================================================
-- POS System Database Schema
-- Agricultural Chemicals, Fertilizers & Farming Tools
-- PostgreSQL Database Schema
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'cashier', 'warehouse');
CREATE TYPE payment_method AS ENUM ('cash', 'qr_promptpay', 'bank_transfer', 'credit');
CREATE TYPE payment_status AS ENUM ('pending', 'confirmed', 'failed', 'refunded');
CREATE TYPE order_status AS ENUM ('draft', 'pending', 'completed', 'cancelled', 'refunded');
CREATE TYPE stock_transaction_type AS ENUM ('receive', 'sale', 'adjustment', 'return', 'damage');
CREATE TYPE credit_status AS ENUM ('active', 'overdue', 'paid', 'suspended');
CREATE TYPE unit_type AS ENUM ('kg', 'g', 'l', 'ml', 'bag', 'box', 'piece', 'set', 'bottle', 'pack');

-- ============================================================
-- USERS & AUTHENTICATION
-- ============================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role user_role NOT NULL DEFAULT 'cashier',
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCT CATEGORIES
-- ============================================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    image_url TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SUPPLIERS
-- ============================================================
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    tax_id VARCHAR(20),
    bank_name VARCHAR(100),
    bank_account VARCHAR(30),
    credit_days INTEGER DEFAULT 30,
    logo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCTS
-- ============================================================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    qr_code TEXT UNIQUE,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    unit unit_type NOT NULL DEFAULT 'piece',
    unit_per_pack DECIMAL(10,3) DEFAULT 1,
    cost_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    selling_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    min_selling_price DECIMAL(12,2),
    tax_rate DECIMAL(5,2) DEFAULT 7.00,
    description TEXT,
    specifications JSONB,
    main_image_url TEXT,
    image_urls JSONB DEFAULT '[]',
    min_stock_level INTEGER DEFAULT 5,
    max_stock_level INTEGER DEFAULT 1000,
    reorder_point INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    is_serialized BOOLEAN DEFAULT FALSE,
    chemical_registration VARCHAR(50),
    expiry_tracking BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PRODUCT IMAGES (separate table for multiple images)
-- ============================================================
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    image_data BYTEA,
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- WAREHOUSES / LOCATIONS
-- ============================================================
CREATE TABLE warehouses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    manager_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- STOCK / INVENTORY
-- ============================================================
CREATE TABLE stock (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    warehouse_id UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    quantity DECIMAL(12,3) NOT NULL DEFAULT 0,
    reserved_quantity DECIMAL(12,3) DEFAULT 0,
    available_quantity DECIMAL(12,3) GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    last_counted_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, warehouse_id)
);

-- ============================================================
-- STOCK TRANSACTIONS (Receive/Sale/Adjustment)
-- ============================================================
CREATE TABLE stock_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_type stock_transaction_type NOT NULL,
    reference_no VARCHAR(50) UNIQUE NOT NULL,
    product_id UUID NOT NULL REFERENCES products(id),
    warehouse_id UUID NOT NULL REFERENCES warehouses(id),
    quantity DECIMAL(12,3) NOT NULL,
    unit_cost DECIMAL(12,2),
    total_cost DECIMAL(12,2),
    before_quantity DECIMAL(12,3),
    after_quantity DECIMAL(12,3),
    lot_number VARCHAR(50),
    expiry_date DATE,
    notes TEXT,
    reference_id UUID,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PURCHASE ORDERS (Receive Goods)
-- ============================================================
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_number VARCHAR(30) UNIQUE NOT NULL,
    supplier_id UUID REFERENCES suppliers(id),
    warehouse_id UUID REFERENCES warehouses(id),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_date DATE,
    received_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    subtotal DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    document_url TEXT,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    ordered_quantity DECIMAL(12,3) NOT NULL,
    received_quantity DECIMAL(12,3) DEFAULT 0,
    unit_cost DECIMAL(12,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    total_cost DECIMAL(12,2) NOT NULL,
    lot_number VARCHAR(50),
    expiry_date DATE,
    notes TEXT
);

-- ============================================================
-- CUSTOMERS
-- ============================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    customer_type VARCHAR(20) DEFAULT 'individual',
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    district VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(10),
    tax_id VARCHAR(20),
    farm_area_rai DECIMAL(10,2),
    crop_types JSONB DEFAULT '[]',
    avatar_url TEXT,
    credit_limit DECIMAL(12,2) DEFAULT 0,
    credit_balance DECIMAL(12,2) DEFAULT 0,
    credit_days INTEGER DEFAULT 30,
    credit_status credit_status DEFAULT 'active',
    loyalty_points INTEGER DEFAULT 0,
    total_purchases DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SALES ORDERS
-- ============================================================
CREATE TABLE sales_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(30) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    cashier_id UUID REFERENCES users(id),
    warehouse_id UUID REFERENCES warehouses(id),
    order_date TIMESTAMPTZ DEFAULT NOW(),
    status order_status DEFAULT 'draft',
    subtotal DECIMAL(12,2) DEFAULT 0,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    paid_amount DECIMAL(12,2) DEFAULT 0,
    change_amount DECIMAL(12,2) DEFAULT 0,
    payment_method payment_method,
    payment_status payment_status DEFAULT 'pending',
    qr_reference VARCHAR(100),
    notes TEXT,
    is_credit_sale BOOLEAN DEFAULT FALSE,
    credit_due_date DATE,
    receipt_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sales_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 7,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    lot_number VARCHAR(50),
    notes TEXT
);

-- ============================================================
-- PAYMENT TRANSACTIONS
-- ============================================================
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES sales_orders(id),
    transaction_ref VARCHAR(100) UNIQUE NOT NULL,
    payment_method payment_method NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status payment_status DEFAULT 'pending',
    qr_code_data TEXT,
    qr_image_url TEXT,
    bank_reference VARCHAR(100),
    payer_name VARCHAR(100),
    payer_account VARCHAR(50),
    confirmed_at TIMESTAMPTZ,
    confirmed_by UUID REFERENCES users(id),
    webhook_data JSONB,
    slip_image_url TEXT,
    slip_image_data BYTEA,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CREDIT TRANSACTIONS (Customer Credit System)
-- ============================================================
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    order_id UUID REFERENCES sales_orders(id),
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    balance_before DECIMAL(12,2),
    balance_after DECIMAL(12,2),
    due_date DATE,
    paid_date DATE,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BANK ACCOUNTS (for QR payment receiving)
-- ============================================================
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_name VARCHAR(100) NOT NULL,
    account_name VARCHAR(150) NOT NULL,
    account_number VARCHAR(30) NOT NULL,
    promptpay_id VARCHAR(20),
    qr_code_image_url TEXT,
    qr_code_data TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SETTINGS
-- ============================================================
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    value_json JSONB,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOGS
-- ============================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_products_code ON products(code);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_stock_product ON stock(product_id);
CREATE INDEX idx_stock_warehouse ON stock(warehouse_id);
CREATE INDEX idx_stock_transactions_product ON stock_transactions(product_id);
CREATE INDEX idx_stock_transactions_created ON stock_transactions(created_at);
CREATE INDEX idx_sales_orders_customer ON sales_orders(customer_id);
CREATE INDEX idx_sales_orders_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_status ON sales_orders(status);
CREATE INDEX idx_payment_transactions_order ON payment_transactions(order_id);
CREATE INDEX idx_credit_transactions_customer ON credit_transactions(customer_id);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_code ON customers(code);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table ON audit_logs(table_name, record_id);

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_products_updated BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customers_updated BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_sales_orders_updated BEFORE UPDATE ON sales_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_purchase_orders_updated BEFORE UPDATE ON purchase_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Generate Order Number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TEXT AS $$
DECLARE
    today TEXT := TO_CHAR(NOW(), 'YYYYMMDD');
    seq INTEGER;
    result TEXT;
BEGIN
    SELECT COUNT(*) + 1 INTO seq
    FROM sales_orders
    WHERE DATE(order_date) = CURRENT_DATE;
    result := 'SO' || today || LPAD(seq::TEXT, 4, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Update stock on sale
CREATE OR REPLACE FUNCTION update_stock_on_sale()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE stock
    SET quantity = quantity - NEW.quantity,
        updated_at = NOW()
    WHERE product_id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
