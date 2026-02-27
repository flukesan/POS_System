"""
Reports & Analytics API
- Daily/Monthly Sales Summary
- Stock Report
- Customer Credit Report
- Best-selling Products
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, cast, Date

from app.db.database import get_db
from app.models.models import (
    SalesOrder, SalesOrderItem, Product, Customer,
    Stock, CreditTransaction, PaymentTransaction, OrderStatus
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get today's dashboard KPIs."""
    today = date.today()
    month_start = today.replace(day=1)

    # Today's sales
    today_result = await db.execute(
        select(
            func.count(SalesOrder.id).label("order_count"),
            func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_sales"),
        ).where(
            and_(
                func.date(SalesOrder.order_date) == today,
                SalesOrder.status == OrderStatus.completed,
            )
        )
    )
    today_row = today_result.one()

    # Monthly sales
    month_result = await db.execute(
        select(
            func.count(SalesOrder.id).label("order_count"),
            func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_sales"),
        ).where(
            and_(
                func.date(SalesOrder.order_date) >= month_start,
                SalesOrder.status == OrderStatus.completed,
            )
        )
    )
    month_row = month_result.one()

    # Low stock count
    low_stock_result = await db.execute(
        select(func.count()).select_from(Stock).join(Product).where(
            Stock.quantity <= Product.reorder_point
        )
    )
    low_stock_count = low_stock_result.scalar()

    # Outstanding credit
    credit_result = await db.execute(
        select(func.coalesce(func.sum(Customer.credit_balance), 0))
    )
    total_credit = credit_result.scalar()

    # Overdue credit customers
    overdue_result = await db.execute(
        select(func.count()).select_from(Customer).where(
            Customer.credit_status == "overdue"
        )
    )
    overdue_count = overdue_result.scalar()

    return {
        "today": {
            "order_count": today_row.order_count,
            "total_sales": float(today_row.total_sales),
        },
        "this_month": {
            "order_count": month_row.order_count,
            "total_sales": float(month_row.total_sales),
        },
        "low_stock_products": low_stock_count,
        "total_outstanding_credit": float(total_credit),
        "overdue_customers": overdue_count,
    }


@router.get("/sales/daily")
async def daily_sales_report(
    date_from: date = Query(default=None),
    date_to: date = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """Daily sales breakdown."""
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    result = await db.execute(
        select(
            func.date(SalesOrder.order_date).label("sale_date"),
            func.count(SalesOrder.id).label("order_count"),
            func.sum(SalesOrder.subtotal).label("subtotal"),
            func.sum(SalesOrder.discount_amount).label("total_discount"),
            func.sum(SalesOrder.tax_amount).label("total_tax"),
            func.sum(SalesOrder.total_amount).label("total_sales"),
        )
        .where(
            and_(
                func.date(SalesOrder.order_date) >= date_from,
                func.date(SalesOrder.order_date) <= date_to,
                SalesOrder.status == OrderStatus.completed,
            )
        )
        .group_by(func.date(SalesOrder.order_date))
        .order_by(func.date(SalesOrder.order_date))
    )
    rows = result.all()
    return [
        {
            "date": str(r.sale_date),
            "order_count": r.order_count,
            "subtotal": float(r.subtotal or 0),
            "total_discount": float(r.total_discount or 0),
            "total_tax": float(r.total_tax or 0),
            "total_sales": float(r.total_sales or 0),
        }
        for r in rows
    ]


@router.get("/sales/top-products")
async def top_products_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Top selling products by quantity and revenue."""
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    result = await db.execute(
        select(
            Product.id,
            Product.code,
            Product.name,
            Product.unit,
            func.sum(SalesOrderItem.quantity).label("total_qty"),
            func.sum(SalesOrderItem.total_amount).label("total_revenue"),
        )
        .join(SalesOrderItem, Product.id == SalesOrderItem.product_id)
        .join(SalesOrder, SalesOrderItem.order_id == SalesOrder.id)
        .where(
            and_(
                func.date(SalesOrder.order_date) >= date_from,
                func.date(SalesOrder.order_date) <= date_to,
                SalesOrder.status == OrderStatus.completed,
            )
        )
        .group_by(Product.id, Product.code, Product.name, Product.unit)
        .order_by(func.sum(SalesOrderItem.total_amount).desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "product_id": str(r.id),
            "product_code": r.code,
            "product_name": r.name,
            "unit": r.unit,
            "total_qty": float(r.total_qty),
            "total_revenue": float(r.total_revenue),
        }
        for r in rows
    ]


@router.get("/credit/outstanding")
async def outstanding_credit_report(db: AsyncSession = Depends(get_db)):
    """All customers with outstanding credit."""
    result = await db.execute(
        select(Customer)
        .where(Customer.credit_balance > 0)
        .order_by(Customer.credit_balance.desc())
    )
    customers = result.scalars().all()

    total_outstanding = sum(c.credit_balance for c in customers)
    overdue_customers = [c for c in customers if c.credit_status == "overdue"]

    return {
        "total_outstanding": float(total_outstanding),
        "total_customers": len(customers),
        "overdue_customers": len(overdue_customers),
        "customers": [
            {
                "id": str(c.id),
                "code": c.code,
                "name": c.name,
                "phone": c.phone,
                "credit_limit": float(c.credit_limit),
                "credit_balance": float(c.credit_balance),
                "credit_status": c.credit_status,
                "available_credit": float(c.credit_limit - c.credit_balance),
            }
            for c in customers
        ],
    }


@router.get("/stock/valuation")
async def stock_valuation_report(db: AsyncSession = Depends(get_db)):
    """Total stock value at cost price."""
    result = await db.execute(
        select(
            Product.id,
            Product.code,
            Product.name,
            Product.unit,
            Product.cost_price,
            Product.selling_price,
            func.sum(Stock.quantity).label("total_qty"),
            func.sum(Stock.quantity * Product.cost_price).label("cost_value"),
            func.sum(Stock.quantity * Product.selling_price).label("selling_value"),
        )
        .join(Stock, Product.id == Stock.product_id)
        .where(Product.is_active == True)
        .group_by(Product.id, Product.code, Product.name, Product.unit, Product.cost_price, Product.selling_price)
        .order_by(func.sum(Stock.quantity * Product.cost_price).desc())
    )
    rows = result.all()
    total_cost = sum(float(r.cost_value or 0) for r in rows)
    total_selling = sum(float(r.selling_value or 0) for r in rows)

    return {
        "total_cost_value": total_cost,
        "total_selling_value": total_selling,
        "potential_profit": total_selling - total_cost,
        "items": [
            {
                "product_id": str(r.id),
                "product_code": r.code,
                "product_name": r.name,
                "unit": r.unit,
                "cost_price": float(r.cost_price),
                "selling_price": float(r.selling_price),
                "total_qty": float(r.total_qty or 0),
                "cost_value": float(r.cost_value or 0),
                "selling_value": float(r.selling_value or 0),
            }
            for r in rows
        ],
    }
