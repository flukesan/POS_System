"""
Sales Order API Endpoints
- Create/Update Order
- Add/Remove Items
- Process Payment (Cash, QR PromptPay)
- Confirm Payment
- Print Receipt
"""
import uuid
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.models import (
    SalesOrder, SalesOrderItem, PaymentTransaction, Product, Stock,
    Customer, CreditTransaction, OrderStatus, PaymentMethod, PaymentStatus
)
from app.services.qr_service import generate_promptpay_qr
from app.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/sales", tags=["Sales"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ─── SCHEMAS ─────────────────────────────────────────────────
class OrderItemCreate(BaseModel):
    product_id: str
    quantity: Decimal = Field(gt=0)
    unit_price: Optional[Decimal] = None
    discount_percent: Decimal = Field(default=0, ge=0, le=100)

class OrderCreate(BaseModel):
    customer_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    items: List[OrderItemCreate] = []
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    notes: Optional[str] = None
    is_credit_sale: bool = False

class PaymentRequest(BaseModel):
    order_id: str
    payment_method: PaymentMethod
    paid_amount: Optional[Decimal] = None  # for cash payment

class ConfirmPaymentRequest(BaseModel):
    transaction_ref: str
    bank_reference: Optional[str] = None
    payer_name: Optional[str] = None
    slip_image_base64: Optional[str] = None


# ─── HELPERS ─────────────────────────────────────────────────
def _generate_order_number() -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"SO{today}{suffix}"

def _generate_tx_ref() -> str:
    return f"TX{uuid.uuid4().hex[:12].upper()}"

async def _calculate_order_totals(items: list) -> dict:
    subtotal = sum(i["total_amount"] for i in items)
    tax_amount = sum(i["tax_amount"] for i in items)
    return {"subtotal": subtotal, "tax_amount": tax_amount}


# ─── ENDPOINTS ───────────────────────────────────────────────
@router.post("/orders", status_code=201)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new sales order with items."""
    order_items = []
    subtotal = Decimal("0")
    tax_total = Decimal("0")

    for item in payload.items:
        product = await db.get(Product, uuid.UUID(item.product_id))
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")

        unit_price = item.unit_price or product.selling_price
        discount_amt = unit_price * item.quantity * (item.discount_percent / 100)
        taxable = unit_price * item.quantity - discount_amt
        tax_amt = taxable * (product.tax_rate / 100)
        total = taxable + tax_amt

        order_items.append(SalesOrderItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
            discount_percent=item.discount_percent,
            discount_amount=discount_amt,
            tax_rate=product.tax_rate,
            tax_amount=tax_amt,
            total_amount=total,
        ))
        subtotal += taxable
        tax_total += tax_amt

    discount_amount = subtotal * (payload.discount_percent / 100)
    total_amount = subtotal - discount_amount + tax_total

    credit_due_date = None
    if payload.is_credit_sale and payload.customer_id:
        customer = await db.get(Customer, uuid.UUID(payload.customer_id))
        if customer:
            credit_due_date = date.today() + timedelta(days=customer.credit_days)

    order = SalesOrder(
        order_number=_generate_order_number(),
        customer_id=uuid.UUID(payload.customer_id) if payload.customer_id else None,
        warehouse_id=uuid.UUID(payload.warehouse_id) if payload.warehouse_id else None,
        subtotal=subtotal,
        discount_percent=payload.discount_percent,
        discount_amount=discount_amount,
        tax_amount=tax_total,
        total_amount=total_amount,
        notes=payload.notes,
        is_credit_sale=payload.is_credit_sale,
        credit_due_date=credit_due_date,
        status=OrderStatus.pending,
    )
    db.add(order)
    await db.flush()

    for item in order_items:
        item.order_id = order.id
        db.add(item)

    await db.commit()
    await db.refresh(order)
    return {"order_id": str(order.id), "order_number": order.order_number, "total_amount": float(order.total_amount)}


@router.post("/payment/initiate")
async def initiate_payment(payload: PaymentRequest, db: AsyncSession = Depends(get_db)):
    """
    Initiate payment for an order.
    - Cash: returns change calculation
    - QR PromptPay: generates QR code with amount
    - Credit: records credit transaction
    """
    order = await db.get(SalesOrder, uuid.UUID(payload.order_id))
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status == OrderStatus.completed:
        raise HTTPException(400, "Order already completed")

    tx_ref = _generate_tx_ref()

    if payload.payment_method == PaymentMethod.cash:
        paid = payload.paid_amount or order.total_amount
        change = paid - order.total_amount
        if change < 0:
            raise HTTPException(400, f"Insufficient payment. Required: {order.total_amount}")

        tx = PaymentTransaction(
            order_id=order.id,
            transaction_ref=tx_ref,
            payment_method=PaymentMethod.cash,
            amount=order.total_amount,
            status=PaymentStatus.confirmed,
            confirmed_at=datetime.utcnow(),
        )
        db.add(tx)
        order.paid_amount = paid
        order.change_amount = change
        order.payment_method = PaymentMethod.cash
        order.payment_status = PaymentStatus.confirmed
        order.status = OrderStatus.completed
        await db.commit()
        return {"status": "confirmed", "change_amount": float(change), "transaction_ref": tx_ref}

    elif payload.payment_method == PaymentMethod.qr_promptpay:
        from app.models.models import BankAccount
        result = await db.execute(select(BankAccount).where(BankAccount.is_default == True))
        bank = result.scalar_one_or_none()
        if not bank or not bank.promptpay_id:
            raise HTTPException(400, "No PromptPay account configured")

        qr_data = generate_promptpay_qr(
            promptpay_id=bank.promptpay_id,
            amount=order.total_amount,
            order_ref=order.order_number,
        )
        tx = PaymentTransaction(
            order_id=order.id,
            transaction_ref=tx_ref,
            payment_method=PaymentMethod.qr_promptpay,
            amount=order.total_amount,
            status=PaymentStatus.pending,
            qr_code_data=qr_data["qr_data"],
        )
        db.add(tx)
        order.payment_method = PaymentMethod.qr_promptpay
        order.qr_reference = tx_ref
        await db.commit()
        return {
            "status": "pending",
            "transaction_ref": tx_ref,
            "amount": float(order.total_amount),
            "qr_data": qr_data["qr_data"],
            "qr_image": qr_data["qr_image_base64"],
        }

    elif payload.payment_method == PaymentMethod.credit:
        if not order.customer_id:
            raise HTTPException(400, "Credit sale requires a customer")
        customer = await db.get(Customer, order.customer_id)
        available_credit = customer.credit_limit - customer.credit_balance
        if order.total_amount > available_credit:
            raise HTTPException(400, f"Insufficient credit. Available: {available_credit}")

        credit_tx = CreditTransaction(
            customer_id=customer.id,
            order_id=order.id,
            transaction_type="charge",
            amount=order.total_amount,
            balance_before=customer.credit_balance,
            balance_after=customer.credit_balance + order.total_amount,
            due_date=order.credit_due_date,
        )
        customer.credit_balance += order.total_amount
        db.add(credit_tx)

        tx = PaymentTransaction(
            order_id=order.id,
            transaction_ref=tx_ref,
            payment_method=PaymentMethod.credit,
            amount=order.total_amount,
            status=PaymentStatus.confirmed,
            confirmed_at=datetime.utcnow(),
        )
        db.add(tx)
        order.payment_method = PaymentMethod.credit
        order.payment_status = PaymentStatus.confirmed
        order.status = OrderStatus.completed
        await db.commit()
        return {"status": "confirmed", "transaction_ref": tx_ref, "credit_balance": float(customer.credit_balance)}

    raise HTTPException(400, "Unsupported payment method")


@router.post("/payment/confirm")
async def confirm_qr_payment(payload: ConfirmPaymentRequest, db: AsyncSession = Depends(get_db)):
    """Manually confirm QR/transfer payment after verifying bank slip."""
    result = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.transaction_ref == payload.transaction_ref)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.status == PaymentStatus.confirmed:
        raise HTTPException(400, "Already confirmed")

    tx.status = PaymentStatus.confirmed
    tx.confirmed_at = datetime.utcnow()
    tx.bank_reference = payload.bank_reference
    tx.payer_name = payload.payer_name

    order = await db.get(SalesOrder, tx.order_id)
    order.payment_status = PaymentStatus.confirmed
    order.status = OrderStatus.completed
    order.paid_amount = tx.amount

    await db.commit()
    return {"status": "confirmed", "order_number": order.order_number, "amount": float(tx.amount)}


@router.get("/orders/{order_id}")
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get order details with items and payment."""
    order = await db.get(SalesOrder, uuid.UUID(order_id))
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("/orders")
async def list_orders(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List sales orders with filters."""
    query = select(SalesOrder).order_by(SalesOrder.order_date.desc()).limit(limit).offset(offset)
    if customer_id:
        query = query.where(SalesOrder.customer_id == uuid.UUID(customer_id))
    if status:
        query = query.where(SalesOrder.status == status)
    result = await db.execute(query)
    return result.scalars().all()
