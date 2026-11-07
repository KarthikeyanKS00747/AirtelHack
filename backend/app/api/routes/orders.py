from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Order, OrderMilestone, Quote, BusinessProfile, User, AuditEvent
from app.core.config import settings

router = APIRouter(prefix="/api/orders", tags=["orders"])


# Lifecycle stages in order
LIFECYCLE = [
    ("placed", "Order Placed", "Your order has been received and confirmed."),
    ("kyc_pending", "KYC Pending", "Please upload your KYC documents to proceed."),
    ("kyc_review", "KYC Under Review", "Your documents are being verified."),
    ("kyc_complete", "KYC Verified", "Your KYC documents have been verified."),
    ("serviceability_check", "Serviceability Check", "Checking service availability at your location."),
    ("scheduled", "Installation Scheduled", "Your installation has been scheduled."),
    ("in_progress", "Installation In Progress", "Technicians are at your premises."),
    ("activated", "Service Activated", "Your Accel Business services are now active!"),
]

VALID_TRANSITIONS = {
    "placed": ["kyc_pending", "cancelled"],
    "kyc_pending": ["kyc_review", "cancelled"],
    "kyc_review": ["kyc_complete", "kyc_pending", "cancelled"],
    "kyc_complete": ["serviceability_check", "cancelled"],
    "serviceability_check": ["scheduled", "cancelled"],
    "scheduled": ["in_progress", "cancelled"],
    "in_progress": ["activated", "cancelled"],
    "activated": [],
    "cancelled": [],
}


class OrderCreate(BaseModel):
    quote_id: str
    payment_ref: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


@router.post("/", status_code=201)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = db.query(Quote).filter(Quote.id == data.quote_id, Quote.user_id == current_user.id).first()
    if not quote:
        raise HTTPException(404, "Quote not found")
    if quote.status not in ("draft", "accepted"):
        raise HTTPException(400, f"Cannot create order from {quote.status} quote")

    # Calculate expected activation date from max install days
    install_days = 7  # default; ideally from bundle items
    expected_activation = date.fromisoformat(settings.DATASET_REFERENCE_DATE) + timedelta(days=install_days)

    order_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order = Order(
        order_number=order_num,
        user_id=current_user.id,
        quote_id=quote.id,
        business_profile_id=quote.business_profile_id,
        status="placed",
        total_monthly_inr=quote.total_monthly_inr,
        total_setup_inr=quote.total_setup_inr,
        contract_months=quote.contract_months,
        payment_ref=data.payment_ref or f"SIM-PAY-{uuid.uuid4().hex[:10].upper()}",
        payment_status="completed",  # simulated
        expected_activation_date=expected_activation,
    )
    db.add(order)
    db.flush()

    # Accept the quote
    quote.status = "accepted"

    # Initial milestone
    m = OrderMilestone(
        order_id=order.id,
        stage="placed",
        label="Order Placed",
        description="Your order has been received. Please proceed with KYC verification.",
        agent="system",
    )
    db.add(m)

    # Audit
    audit = AuditEvent(
        user_id=current_user.id,
        event_type="order_created",
        resource_type="order",
        resource_id=order.id,
        details={"order_number": order_num, "quote_id": quote.id},
    )
    db.add(audit)

    db.commit()
    db.refresh(order)
    return order


@router.get("/")
def list_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.user_id != current_user.id and current_user.role not in ("admin", "sales"):
        raise HTTPException(403, "Access denied")

    milestones = db.query(OrderMilestone).filter(OrderMilestone.order_id == order_id).order_by(OrderMilestone.occurred_at).all()
    quote = db.query(Quote).filter(Quote.id == order.quote_id).first()

    # Build lifecycle with completion status
    completed_stages = {m.stage for m in milestones}
    lifecycle_display = []
    for stage, label, desc in LIFECYCLE:
        lifecycle_display.append({
            "stage": stage,
            "label": label,
            "description": desc,
            "completed": stage in completed_stages,
            "is_current": stage == order.status,
        })

    return {
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "total_monthly_inr": order.total_monthly_inr,
            "total_setup_inr": order.total_setup_inr,
            "contract_months": order.contract_months,
            "payment_status": order.payment_status,
            "payment_ref": order.payment_ref,
            "expected_activation_date": str(order.expected_activation_date) if order.expected_activation_date else None,
            "activated_at": str(order.activated_at) if order.activated_at else None,
            "created_at": str(order.created_at),
        },
        "quote": {
            "quote_number": quote.quote_number if quote else "",
            "customer_name": quote.customer_name if quote else "",
            "line_items": quote.line_items if quote else [],
        },
        "milestones": [
            {"stage": m.stage, "label": m.label, "description": m.description, "occurred_at": str(m.occurred_at)}
            for m in milestones
        ],
        "lifecycle": lifecycle_display,
        "next_action": _get_next_action(order.status),
    }


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: str,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "sales"):
        raise HTTPException(403, "Only staff can update order status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if data.status not in allowed:
        raise HTTPException(400, f"Invalid transition: {order.status} → {data.status}. Allowed: {allowed}")

    order.status = data.status
    stage_info = {s: (l, d) for s, l, d in LIFECYCLE}
    label, desc = stage_info.get(data.status, (data.status, ""))

    m = OrderMilestone(
        order_id=order.id,
        stage=data.status,
        label=label,
        description=data.note or desc,
        agent=current_user.full_name,
    )
    db.add(m)
    db.commit()
    return {"message": f"Order status updated to {data.status}"}


# Customer self-service: advance KYC pending → KYC review
@router.post("/{order_id}/advance-kyc")
def advance_to_kyc_review(order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "kyc_pending":
        raise HTTPException(400, f"Order is {order.status}, not kyc_pending")

    order.status = "kyc_review"
    m = OrderMilestone(
        order_id=order.id,
        stage="kyc_review",
        label="KYC Submitted",
        description="Documents submitted. Accel team is reviewing your KYC.",
        agent="system",
    )
    db.add(m)
    db.commit()
    return {"message": "KYC submitted for review"}


def _get_next_action(status: str) -> dict:
    actions = {
        "placed": {"label": "Upload KYC Documents", "action": "kyc"},
        "kyc_pending": {"label": "Upload KYC Documents", "action": "kyc"},
        "kyc_review": {"label": "KYC Under Review — No action needed", "action": None},
        "kyc_complete": {"label": "Awaiting Service Check", "action": None},
        "serviceability_check": {"label": "Awaiting Scheduling", "action": None},
        "scheduled": {"label": "Prepare for Installation", "action": None},
        "in_progress": {"label": "Installation in Progress", "action": None},
        "activated": {"label": "Service Active — Contact Support if needed", "action": "support"},
        "cancelled": {"label": "Order Cancelled", "action": None},
    }
    return actions.get(status, {"label": "Contact Support", "action": "support"})
