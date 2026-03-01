"""
Product Management API
- CRUD Products
- Upload Images
- Generate QR/Barcode
- Search by QR/Barcode scan
"""
import uuid
import io
import base64
import aiofiles
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from pydantic import BaseModel, Field
from decimal import Decimal

from app.db.database import get_db
from app.models.models import Product, ProductImage, Stock, Warehouse, Category, Supplier
from app.services.qr_service import generate_product_qr
from app.core.config import settings

router = APIRouter(prefix="/products", tags=["Products"])


def _product_dict(p: Product) -> dict:
    """Serialize a Product SQLAlchemy model to a safe dict (no lazy-load)."""
    return {
        "id": str(p.id),
        "code": p.code,
        "barcode": p.barcode,
        "name": p.name,
        "name_en": p.name_en,
        "category_id": str(p.category_id) if p.category_id else None,
        "supplier_id": str(p.supplier_id) if p.supplier_id else None,
        "unit": p.unit,
        "unit_per_pack": float(p.unit_per_pack) if p.unit_per_pack is not None else 1,
        "cost_price": float(p.cost_price) if p.cost_price is not None else 0,
        "selling_price": float(p.selling_price) if p.selling_price is not None else 0,
        "min_selling_price": float(p.min_selling_price) if p.min_selling_price is not None else None,
        "tax_rate": float(p.tax_rate) if p.tax_rate is not None else 7.0,
        "description": p.description,
        "min_stock_level": p.min_stock_level,
        "reorder_point": p.reorder_point,
        "is_active": p.is_active,
        "chemical_registration": p.chemical_registration,
        "expiry_tracking": p.expiry_tracking,
        "main_image_url": p.main_image_url,
        "qr_code": p.qr_code,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


# ─── SCHEMAS ─────────────────────────────────────────────────
class ProductCreate(BaseModel):
    code: str
    name: str
    name_en: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    unit: str = "piece"
    unit_per_pack: Decimal = Field(default=1, gt=0)
    cost_price: Decimal = Field(default=0, ge=0)
    selling_price: Decimal = Field(default=0, ge=0)
    min_selling_price: Optional[Decimal] = None
    tax_rate: Decimal = Field(default=7.00)
    description: Optional[str] = None
    min_stock_level: int = 5
    reorder_point: int = 10
    chemical_registration: Optional[str] = None
    expiry_tracking: bool = False
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    min_selling_price: Optional[Decimal] = None
    description: Optional[str] = None
    min_stock_level: Optional[int] = None
    reorder_point: Optional[int] = None
    is_active: Optional[bool] = None


# ─── ENDPOINTS ───────────────────────────────────────────────
@router.get("")
async def list_products(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    low_stock: bool = False,
    is_active: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List products with filters and pagination."""
    query = select(Product).where(Product.is_active == is_active)
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.code.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%"),
            )
        )
    if category_id:
        query = query.where(Product.category_id == uuid.UUID(category_id))
    if supplier_id:
        query = query.where(Product.supplier_id == uuid.UUID(supplier_id))

    result = await db.execute(query.order_by(Product.name).limit(limit).offset(offset))
    return result.scalars().all()


@router.post("", status_code=201)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Create a new product."""
    existing = await db.execute(select(Product).where(Product.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Product code '{payload.code}' already exists")

    product = Product(
        code=payload.code,
        name=payload.name,
        name_en=payload.name_en,
        category_id=uuid.UUID(payload.category_id) if payload.category_id else None,
        supplier_id=uuid.UUID(payload.supplier_id) if payload.supplier_id else None,
        unit=payload.unit,
        unit_per_pack=payload.unit_per_pack,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        min_selling_price=payload.min_selling_price,
        tax_rate=payload.tax_rate,
        description=payload.description,
        min_stock_level=payload.min_stock_level,
        reorder_point=payload.reorder_point,
        chemical_registration=payload.chemical_registration,
        expiry_tracking=payload.expiry_tracking,
        is_active=payload.is_active,
    )
    db.add(product)
    await db.flush()

    # Generate product QR
    qr_result = generate_product_qr(str(product.id), product.code)
    product.qr_code = qr_result["qr_data"]

    # Initialize stock for all warehouses
    warehouses = await db.execute(select(Warehouse).where(Warehouse.is_active == True))
    for wh in warehouses.scalars().all():
        stock = Stock(product_id=product.id, warehouse_id=wh.id, quantity=0)
        db.add(stock)

    await db.commit()
    await db.refresh(product)
    return _product_dict(product)


@router.get("/scan")
async def scan_product(
    code: str,  # barcode or QR code value
    db: AsyncSession = Depends(get_db)
):
    """Look up a product by scanning barcode or QR code."""
    result = await db.execute(
        select(Product).where(
            or_(
                Product.barcode == code,
                Product.qr_code == code,
                Product.code == code,
            )
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found for this code")

    # Include current stock
    stock_result = await db.execute(
        select(Stock).where(Stock.product_id == product.id)
    )
    stocks = stock_result.scalars().all()
    total_qty = sum(s.quantity for s in stocks)

    return {
        "product": _product_dict(product),
        "total_stock": float(total_qty),
    }


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all active product categories."""
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order, Category.name)
    )
    return [
        {"id": str(c.id), "name": c.name, "name_en": c.name_en, "sort_order": c.sort_order}
        for c in result.scalars().all()
    ]


@router.get("/{product_id}")
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, uuid.UUID(product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    return _product_dict(product)


@router.put("/{product_id}")
async def update_product(product_id: str, payload: ProductUpdate, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, uuid.UUID(product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        if field in ("category_id", "supplier_id") and value:
            value = uuid.UUID(value)
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return _product_dict(product)


@router.post("/{product_id}/images")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """Upload an image for a product. Stored in DB as bytea and as file."""
    product = await db.get(Product, uuid.UUID(product_id))
    if not product:
        raise HTTPException(404, "Product not found")

    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Invalid image type")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    # Save to disk
    upload_path = Path(settings.UPLOAD_DIR) / "products" / product_id
    upload_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = upload_path / filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    image_url = f"/uploads/products/{product_id}/{filename}"

    img = ProductImage(
        product_id=product.id,
        image_url=image_url,
        image_data=content,
        is_primary=is_primary,
    )
    db.add(img)

    if is_primary:
        product.main_image_url = image_url

    await db.commit()
    return {"image_url": image_url, "is_primary": is_primary}


@router.get("/{product_id}/qr")
async def get_product_qr(product_id: str, db: AsyncSession = Depends(get_db)):
    """Get QR code image for a product."""
    product = await db.get(Product, uuid.UUID(product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    qr_result = generate_product_qr(product_id, product.code)
    return qr_result
