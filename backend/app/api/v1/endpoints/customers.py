"""
Customer Management API
- CRUD Customers
- Credit Management
- Purchase History
- Credit Payment Recording
"""
import uuid
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.models import Customer, CreditTransaction, SalesOrder, CreditStatus

router = APIRouter(prefix="/customers", tags=["Customers"])


# ─── SCHEMAS ─────────────────────────────────────────────────
class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    customer_type: str = "individual"
    tax_id: Optional[str] = None
    farm_area_rai: Optional[Decimal] = None
    crop_types: list = []
    credit_limit: Decimal = Field(default=0, ge=0)
    credit_days: int = Field(default=30, ge=0, le=365)
    notes: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    credit_days: Optional[int] = None
    credit_status: Optional[CreditStatus] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class CreditPayment(BaseModel):
    customer_id: str
    amount: Decimal = Field(gt=0)
    payment_method: str = "cash"
    notes: Optional[str] = None
    order_id: Optional[str] = None


# ─── HELPERS ─────────────────────────────────────────────────
def _generate_customer_code() -> str:
    suffix = uuid.uuid4().hex[:6].upper()
    return f"CUS{suffix}"


# ─── ENDPOINTS ───────────────────────────────────────────────
@router.get("")
async def list_customers(
    search: Optional[str] = None,
    credit_status: Optional[str] = None,
    has_overdue: bool = False,
    is_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List customers with filters."""
    query = select(Customer).where(Customer.is_active == is_active)
    if search:
        from sqlalchemy import or_
        query = query.where(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.code.ilike(f"%{search}%"),
            )
        )
    if credit_status:
        query = query.where(Customer.credit_status == credit_status)
    if has_overdue:
        query = query.where(Customer.credit_status == CreditStatus.overdue)

    result = await db.execute(query.order_by(Customer.name).limit(limit).offset(offset))
    return result.scalars().all()


@router.post("", status_code=201)
async def create_customer(payload: CustomerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new customer."""
    customer = Customer(
        code=_generate_customer_code(),
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        district=payload.district,
        province=payload.province,
        customer_type=payload.customer_type,
        tax_id=payload.tax_id,
        farm_area_rai=payload.farm_area_rai,
        crop_types=payload.crop_types,
        credit_limit=payload.credit_limit,
        credit_days=payload.credit_days,
        notes=payload.notes,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}")
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    customer = await db.get(Customer, uuid.UUID(customer_id))
    if not customer:
        raise HTTPException(404, "Customer not found")
    return customer


@router.put("/{customer_id}")
async def update_customer(customer_id: str, payload: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    customer = await db.get(Customer, uuid.UUID(customer_id))
    if not customer:
        raise HTTPException(404, "Customer not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(customer, field, value)
    await db.commit()
    return customer


@router.get("/{customer_id}/credit-summary")
async def get_credit_summary(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Get customer credit summary - balance, history, overdue."""
    customer = await db.get(Customer, uuid.UUID(customer_id))
    if not customer:
        raise HTTPException(404, "Customer not found")

    # Get outstanding credit orders
    result = await db.execute(
        select(SalesOrder)
        .where(
            SalesOrder.customer_id == customer.id,
            SalesOrder.is_credit_sale == True,
            SalesOrder.payment_status != "confirmed",
        )
        .order_by(SalesOrder.credit_due_date)
    )
    outstanding_orders = result.scalars().all()

    overdue_orders = [o for o in outstanding_orders if o.credit_due_date and o.credit_due_date < date.today()]
    overdue_amount = sum(o.total_amount for o in overdue_orders)

    return {
        "customer_id": str(customer.id),
        "customer_name": customer.name,
        "credit_limit": float(customer.credit_limit),
        "credit_balance": float(customer.credit_balance),
        "available_credit": float(customer.credit_limit - customer.credit_balance),
        "credit_status": customer.credit_status,
        "overdue_amount": float(overdue_amount),
        "outstanding_orders": len(outstanding_orders),
        "overdue_orders": len(overdue_orders),
    }


@router.post("/credit/payment")
async def record_credit_payment(payload: CreditPayment, db: AsyncSession = Depends(get_db)):
    """Record a credit payment from customer."""
    customer = await db.get(Customer, uuid.UUID(payload.customer_id))
    if not customer:
        raise HTTPException(404, "Customer not found")

    if payload.amount > customer.credit_balance:
        raise HTTPException(400, f"Payment exceeds credit balance: {customer.credit_balance}")

    before_balance = customer.credit_balance
    customer.credit_balance -= payload.amount

    if customer.credit_balance <= 0:
        customer.credit_balance = Decimal("0")
        customer.credit_status = CreditStatus.active

    tx = CreditTransaction(
        customer_id=customer.id,
        order_id=uuid.UUID(payload.order_id) if payload.order_id else None,
        transaction_type="payment",
        amount=payload.amount,
        balance_before=before_balance,
        balance_after=customer.credit_balance,
        paid_date=date.today(),
        notes=payload.notes,
    )
    db.add(tx)
    await db.commit()

    return {
        "message": "Payment recorded",
        "amount_paid": float(payload.amount),
        "remaining_balance": float(customer.credit_balance),
    }


@router.get("/{customer_id}/history")
async def customer_purchase_history(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get customer purchase history."""
    result = await db.execute(
        select(SalesOrder)
        .where(SalesOrder.customer_id == uuid.UUID(customer_id))
        .order_by(SalesOrder.order_date.desc())
        .limit(limit)
        .offset(offset)
    )
    orders = result.scalars().all()

    # Totals
    totals = await db.execute(
        select(
            func.count(SalesOrder.id).label("total_orders"),
            func.sum(SalesOrder.total_amount).label("total_spent"),
        ).where(SalesOrder.customer_id == uuid.UUID(customer_id))
    )
    row = totals.one()
    return {
        "total_orders": row.total_orders or 0,
        "total_spent": float(row.total_spent or 0),
        "orders": orders,
    }


@router.get("/{customer_id}/credit-transactions")
async def customer_credit_transactions(
    customer_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get credit transaction history for a customer."""
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.customer_id == uuid.UUID(customer_id))
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
