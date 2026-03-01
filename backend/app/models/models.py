import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Boolean, DateTime, Numeric, Integer,
    Text, ForeignKey, Enum, Date, LargeBinary, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ENUM as PGENUM
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

# PostgreSQL ENUM type that already exists in the DB (created by 01_schema.sql)
_unit_type = PGENUM(
    'kg', 'g', 'l', 'ml', 'bag', 'box', 'piece', 'set', 'bottle', 'pack',
    name='unit_type',
    create_type=False,  # don't try to CREATE TYPE — it already exists
)

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    cashier = "cashier"
    warehouse = "warehouse"

class PaymentMethod(str, enum.Enum):
    cash = "cash"
    qr_promptpay = "qr_promptpay"
    bank_transfer = "bank_transfer"
    credit = "credit"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"
    refunded = "refunded"

class OrderStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    refunded = "refunded"

class StockTransactionType(str, enum.Enum):
    receive = "receive"
    sale = "sale"
    adjustment = "adjustment"
    return_ = "return"
    damage = "damage"

class CreditStatus(str, enum.Enum):
    active = "active"
    overdue = "overdue"
    paid = "paid"
    suspended = "suspended"

# ─── USER ────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.cashier)
    avatar_url = Column(Text)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

# ─── CATEGORY ────────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    description = Column(Text)
    image_url = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    products = relationship("Product", back_populates="category")

# ─── SUPPLIER ────────────────────────────────────────────────
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    tax_id = Column(String(20))
    bank_name = Column(String(100))
    bank_account = Column(String(30))
    credit_days = Column(Integer, default=30)
    logo_url = Column(Text)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    products = relationship("Product", back_populates="supplier")

# ─── PRODUCT ─────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    barcode = Column(String(50), unique=True)
    qr_code = Column(Text, unique=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    unit = Column(_unit_type, nullable=False, default="piece")
    unit_per_pack = Column(Numeric(10, 3), default=1)
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    selling_price = Column(Numeric(12, 2), nullable=False, default=0)
    min_selling_price = Column(Numeric(12, 2))
    tax_rate = Column(Numeric(5, 2), default=7.00)
    description = Column(Text)
    specifications = Column(JSONB)
    main_image_url = Column(Text)
    image_urls = Column(JSONB, default=list)
    min_stock_level = Column(Integer, default=5)
    max_stock_level = Column(Integer, default=1000)
    reorder_point = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    chemical_registration = Column(String(50))
    expiry_tracking = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    stock_items = relationship("Stock", back_populates="product")

# ─── PRODUCT IMAGE ───────────────────────────────────────────
class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    image_data = Column(LargeBinary)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    product = relationship("Product", back_populates="images")

# ─── WAREHOUSE ───────────────────────────────────────────────
class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# ─── STOCK ───────────────────────────────────────────────────
class Stock(Base):
    __tablename__ = "stock"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False, default=0)
    reserved_quantity = Column(Numeric(12, 3), default=0)
    last_counted_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    product = relationship("Product", back_populates="stock_items")
    warehouse = relationship("Warehouse")

# ─── STOCK TRANSACTION ───────────────────────────────────────
class StockTransaction(Base):
    __tablename__ = "stock_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(Enum(StockTransactionType), nullable=False)
    reference_no = Column(String(50), unique=True, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_cost = Column(Numeric(12, 2))
    total_cost = Column(Numeric(12, 2))
    before_quantity = Column(Numeric(12, 3))
    after_quantity = Column(Numeric(12, 3))
    lot_number = Column(String(50))
    expiry_date = Column(Date)
    notes = Column(Text)
    reference_id = Column(UUID(as_uuid=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# ─── CUSTOMER ────────────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    customer_type = Column(String(20), default="individual")
    name = Column(String(150), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    district = Column(String(100))
    province = Column(String(100))
    postal_code = Column(String(10))
    tax_id = Column(String(20))
    farm_area_rai = Column(Numeric(10, 2))
    crop_types = Column(JSONB, default=list)
    avatar_url = Column(Text)
    credit_limit = Column(Numeric(12, 2), default=0)
    credit_balance = Column(Numeric(12, 2), default=0)
    credit_days = Column(Integer, default=30)
    credit_status = Column(Enum(CreditStatus), default=CreditStatus.active)
    loyalty_points = Column(Integer, default=0)
    total_purchases = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    orders = relationship("SalesOrder", back_populates="customer")
    credit_transactions = relationship("CreditTransaction", back_populates="customer")

# ─── SALES ORDER ─────────────────────────────────────────────
class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(30), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"))
    order_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(OrderStatus), default=OrderStatus.draft)
    subtotal = Column(Numeric(12, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    paid_amount = Column(Numeric(12, 2), default=0)
    change_amount = Column(Numeric(12, 2), default=0)
    payment_method = Column(Enum(PaymentMethod))
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    qr_reference = Column(String(100))
    notes = Column(Text)
    is_credit_sale = Column(Boolean, default=False)
    credit_due_date = Column(Date)
    receipt_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = relationship("Customer", back_populates="orders")
    cashier = relationship("User", foreign_keys=[cashier_id])
    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("PaymentTransaction", back_populates="order")

# ─── SALES ORDER ITEM ────────────────────────────────────────
class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=7)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    lot_number = Column(String(50))
    notes = Column(Text)
    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")

# ─── PAYMENT TRANSACTION ─────────────────────────────────────
class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=False)
    transaction_ref = Column(String(100), unique=True, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    qr_code_data = Column(Text)
    qr_image_url = Column(Text)
    bank_reference = Column(String(100))
    payer_name = Column(String(100))
    payer_account = Column(String(50))
    confirmed_at = Column(DateTime(timezone=True))
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    webhook_data = Column(JSONB)
    slip_image_url = Column(Text)
    slip_image_data = Column(LargeBinary)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    order = relationship("SalesOrder", back_populates="payments")

# ─── CREDIT TRANSACTION ──────────────────────────────────────
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id"))
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    balance_before = Column(Numeric(12, 2))
    balance_after = Column(Numeric(12, 2))
    due_date = Column(Date)
    paid_date = Column(Date)
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    customer = relationship("Customer", back_populates="credit_transactions")

# ─── PURCHASE ORDER ──────────────────────────────────────────
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = Column(String(30), unique=True, nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"))
    order_date = Column(Date, nullable=False, default=datetime.utcnow)
    expected_date = Column(Date)
    received_date = Column(Date)
    status = Column(String(20), default="pending")
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    notes = Column(Text)
    document_url = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    supplier = relationship("Supplier")
    items = relationship("PurchaseOrderItem", back_populates="po", cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    ordered_quantity = Column(Numeric(12, 3), nullable=False)
    received_quantity = Column(Numeric(12, 3), default=0)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    total_cost = Column(Numeric(12, 2), nullable=False)
    lot_number = Column(String(50))
    expiry_date = Column(Date)
    notes = Column(Text)
    po = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")

# ─── BANK ACCOUNT ────────────────────────────────────────────
class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = Column(String(100), nullable=False)
    account_name = Column(String(150), nullable=False)
    account_number = Column(String(30), nullable=False)
    promptpay_id = Column(String(20))
    qr_code_image_url = Column(Text)
    qr_code_data = Column(Text)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
