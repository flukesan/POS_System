"""
Stock Management API
- View stock levels
- Receive goods (purchase order)
- Stock adjustment
- Low stock alerts
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.models import (
    Stock, StockTransaction, StockTransactionType,
    PurchaseOrder, PurchaseOrderItem, Product, Warehouse, Supplier
)

router = APIRouter(prefix="/stock", tags=["Stock"])


# ─── SCHEMAS ─────────────────────────────────────────────────
class POItemCreate(BaseModel):
    product_id: str
    ordered_quantity: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    lot_number: Optional[str] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None

class PurchaseOrderCreate(BaseModel):
    supplier_id: Optional[str] = None
    warehouse_id: str
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[POItemCreate]

class StockAdjustment(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: Decimal
    reason: str
    notes: Optional[str] = None

class GoodsReceiveItem(BaseModel):
    po_item_id: str
    received_quantity: Decimal = Field(gt=0)
    lot_number: Optional[str] = None
    expiry_date: Optional[date] = None


# ─── HELPERS ─────────────────────────────────────────────────
def _generate_ref(prefix: str) -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{today}{suffix}"


# ─── ENDPOINTS ───────────────────────────────────────────────
@router.get("")
async def list_stock(
    warehouse_id: Optional[str] = None,
    product_id: Optional[str] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get current stock levels."""
    query = (
        select(Stock, Product.name, Product.code, Product.unit, Product.min_stock_level, Product.reorder_point)
        .join(Product, Stock.product_id == Product.id)
    )
    if warehouse_id:
        query = query.where(Stock.warehouse_id == uuid.UUID(warehouse_id))
    if product_id:
        query = query.where(Stock.product_id == uuid.UUID(product_id))
    if low_stock_only:
        query = query.where(Stock.quantity <= Product.reorder_point)

    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "stock_id": str(r.Stock.id),
            "product_id": str(r.Stock.product_id),
            "product_name": r.name,
            "product_code": r.code,
            "unit": r.unit,
            "quantity": float(r.Stock.quantity),
            "reserved": float(r.Stock.reserved_quantity),
            "available": float(r.Stock.quantity - r.Stock.reserved_quantity),
            "min_stock_level": r.min_stock_level,
            "reorder_point": r.reorder_point,
            "is_low": r.Stock.quantity <= r.reorder_point,
        }
        for r in rows
    ]


@router.post("/purchase-orders", status_code=201)
async def create_purchase_order(payload: PurchaseOrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new purchase order for receiving goods."""
    subtotal = Decimal("0")
    items_data = []

    for item in payload.items:
        product = await db.get(Product, uuid.UUID(item.product_id))
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")
        discount_amt = item.unit_cost * item.ordered_quantity * (item.discount_percent / 100)
        total_cost = item.unit_cost * item.ordered_quantity - discount_amt
        subtotal += total_cost
        items_data.append((product, item, total_cost))

    tax_amount = subtotal * Decimal("0.07")
    total_amount = subtotal + tax_amount

    po = PurchaseOrder(
        po_number=_generate_ref("PO"),
        supplier_id=uuid.UUID(payload.supplier_id) if payload.supplier_id else None,
        warehouse_id=uuid.UUID(payload.warehouse_id),
        expected_date=payload.expected_date,
        notes=payload.notes,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status="pending",
    )
    db.add(po)
    await db.flush()

    for product, item, total_cost in items_data:
        po_item = PurchaseOrderItem(
            po_id=po.id,
            product_id=product.id,
            ordered_quantity=item.ordered_quantity,
            received_quantity=0,
            unit_cost=item.unit_cost,
            discount_percent=item.discount_percent,
            total_cost=total_cost,
            lot_number=item.lot_number,
            expiry_date=item.expiry_date,
            notes=item.notes,
        )
        db.add(po_item)

    await db.commit()
    await db.refresh(po)
    return {"po_id": str(po.id), "po_number": po.po_number, "total_amount": float(po.total_amount)}


@router.post("/purchase-orders/{po_id}/receive")
async def receive_goods(
    po_id: str,
    items: List[GoodsReceiveItem],
    db: AsyncSession = Depends(get_db)
):
    """Mark goods as received, update stock levels."""
    po = await db.get(PurchaseOrder, uuid.UUID(po_id))
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status == "received":
        raise HTTPException(400, "Already fully received")

    for receive_item in items:
        po_item = await db.get(PurchaseOrderItem, uuid.UUID(receive_item.po_item_id))
        if not po_item or po_item.po_id != po.id:
            raise HTTPException(404, f"PO item {receive_item.po_item_id} not found")

        remaining = po_item.ordered_quantity - po_item.received_quantity
        qty = min(receive_item.received_quantity, remaining)
        po_item.received_quantity += qty
        if receive_item.lot_number:
            po_item.lot_number = receive_item.lot_number
        if receive_item.expiry_date:
            po_item.expiry_date = receive_item.expiry_date

        # Update stock
        stock_result = await db.execute(
            select(Stock).where(
                Stock.product_id == po_item.product_id,
                Stock.warehouse_id == po.warehouse_id,
            )
        )
        stock = stock_result.scalar_one_or_none()
        if not stock:
            stock = Stock(product_id=po_item.product_id, warehouse_id=po.warehouse_id, quantity=0)
            db.add(stock)
            await db.flush()

        before_qty = stock.quantity
        stock.quantity += qty

        # Record transaction
        tx = StockTransaction(
            transaction_type=StockTransactionType.receive,
            reference_no=_generate_ref("RCV"),
            product_id=po_item.product_id,
            warehouse_id=po.warehouse_id,
            quantity=qty,
            unit_cost=po_item.unit_cost,
            total_cost=po_item.unit_cost * qty,
            before_quantity=before_qty,
            after_quantity=stock.quantity,
            lot_number=receive_item.lot_number,
            expiry_date=receive_item.expiry_date,
            reference_id=po.id,
        )
        db.add(tx)

    # Update PO status
    all_received = all(i.received_quantity >= i.ordered_quantity for i in po.items if hasattr(po, 'items'))
    po.status = "received" if all_received else "partial"
    po.received_date = date.today()

    await db.commit()
    return {"status": po.status, "message": "Goods received successfully"}


@router.post("/adjust")
async def adjust_stock(payload: StockAdjustment, db: AsyncSession = Depends(get_db)):
    """Manually adjust stock (count/damage/correction)."""
    stock_result = await db.execute(
        select(Stock).where(
            Stock.product_id == uuid.UUID(payload.product_id),
            Stock.warehouse_id == uuid.UUID(payload.warehouse_id),
        )
    )
    stock = stock_result.scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock record not found")

    before_qty = stock.quantity
    stock.quantity += payload.quantity

    tx = StockTransaction(
        transaction_type=StockTransactionType.adjustment,
        reference_no=_generate_ref("ADJ"),
        product_id=uuid.UUID(payload.product_id),
        warehouse_id=uuid.UUID(payload.warehouse_id),
        quantity=payload.quantity,
        before_quantity=before_qty,
        after_quantity=stock.quantity,
        notes=f"{payload.reason}: {payload.notes or ''}",
    )
    db.add(tx)
    await db.commit()
    return {"message": "Stock adjusted", "new_quantity": float(stock.quantity)}


@router.get("/alerts/low-stock")
async def low_stock_alerts(db: AsyncSession = Depends(get_db)):
    """Get products that are below reorder point."""
    query = (
        select(Stock, Product)
        .join(Product, Stock.product_id == Product.id)
        .where(Stock.quantity <= Product.reorder_point)
        .where(Product.is_active == True)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "product_id": str(r.Product.id),
            "product_code": r.Product.code,
            "product_name": r.Product.name,
            "current_stock": float(r.Stock.quantity),
            "reorder_point": r.Product.reorder_point,
            "min_stock_level": r.Product.min_stock_level,
        }
        for r in rows
    ]


@router.get("/transactions")
async def stock_transactions(
    product_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get stock transaction history."""
    query = select(StockTransaction).order_by(StockTransaction.created_at.desc()).limit(limit).offset(offset)
    if product_id:
        query = query.where(StockTransaction.product_id == uuid.UUID(product_id))
    if transaction_type:
        query = query.where(StockTransaction.transaction_type == transaction_type)
    result = await db.execute(query)
    return result.scalars().all()
