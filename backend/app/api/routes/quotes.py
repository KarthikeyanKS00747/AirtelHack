from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Quote, Bundle, BundleItem, BusinessProfile, Product, Recommendation, User

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


class LineItem(BaseModel):
    product_id: str
    quantity: int = 1


class QuoteCreate(BaseModel):
    recommendation_id: Optional[str] = None
    business_profile_id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    billing_address: str
    gstin_for_invoice: Optional[str] = None
    line_items: list[LineItem]
    contract_months: int = 12
    notes: Optional[str] = None


def _calc_line_items(items: list[LineItem], db: Session) -> tuple[list[dict], float, float]:
    """Server-side price calculation — never trust client prices."""
    line_items_out = []
    total_monthly = 0.0
    total_setup = 0.0

    for li in items:
        product = db.query(Product).filter(Product.id == li.product_id).first()
        if not product:
            raise HTTPException(404, f"Product {li.product_id} not found")
        unit_price = round((product.price_min_inr_per_month + product.price_max_inr_per_month) / 2, 2)
        monthly = round(unit_price * li.quantity, 2)
        setup = round(product.one_time_setup_inr * li.quantity, 2)
        total_monthly += monthly
        total_setup += setup
        line_items_out.append({
            "product_id": product.id,
            "product_name": product.product_name,
            "unit": product.unit,
            "quantity": li.quantity,
            "unit_price_inr": unit_price,
            "monthly_cost_inr": monthly,
            "setup_cost_inr": setup,
        })

    return line_items_out, round(total_monthly, 2), round(total_setup, 2)


@router.post("/", status_code=201)
def create_quote(
    data: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Server-side price calculation
    line_items, total_monthly, total_setup = _calc_line_items(data.line_items, db)
    tax = round(total_monthly * 0.18, 2)
    total_with_tax = round(total_monthly + tax, 2)

    quote_num = f"QT-{uuid.uuid4().hex[:8].upper()}"
    valid_until = date.today() + timedelta(days=30)

    quote = Quote(
        quote_number=quote_num,
        business_profile_id=data.business_profile_id,
        recommendation_id=data.recommendation_id,
        user_id=current_user.id,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        billing_address=data.billing_address,
        gstin_for_invoice=data.gstin_for_invoice,
        line_items=line_items,
        total_monthly_inr=total_monthly,
        total_setup_inr=total_setup,
        contract_months=data.contract_months,
        tax_pct=18,
        total_with_tax_inr=total_with_tax,
        status="draft",
        valid_until=valid_until,
        notes=data.notes,
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@router.get("/{quote_id}")
def get_quote(quote_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    if quote.user_id != current_user.id and current_user.role not in ("admin", "sales"):
        raise HTTPException(403, "Access denied")
    return quote


@router.patch("/{quote_id}/accept")
def accept_quote(quote_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    quote.status = "accepted"
    db.commit()
    return {"message": "Quote accepted", "quote_id": quote_id}


@router.get("/")
def list_my_quotes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Quote).filter(Quote.user_id == current_user.id).order_by(Quote.created_at.desc()).all()
