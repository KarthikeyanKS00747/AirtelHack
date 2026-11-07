from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Lead, User

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/")
def list_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    segment: Optional[str] = None,
    outcome: Optional[str] = None,
    stage: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    q = db.query(Lead)
    if segment:
        q = q.filter(Lead.segment == segment)
    if outcome:
        q = q.filter(Lead.outcome == outcome)
    if stage:
        q = q.filter(Lead.stage_reached == stage)
    if source:
        q = q.filter(Lead.lead_source == source)

    total = q.count()
    leads = q.order_by(Lead.created_date.desc()).offset(offset).limit(limit).all()

    return {"total": total, "leads": [_lead_summary(l) for l in leads]}


@router.get("/funnel")
def get_funnel(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total = db.query(func.count(Lead.id)).scalar()
    contacted = db.query(func.count(Lead.id)).filter(Lead.contacted_date.isnot(None)).scalar()
    needs_assessed = db.query(func.count(Lead.id)).filter(Lead.needs_assessed_date.isnot(None)).scalar()
    quote_accepted = db.query(func.count(Lead.id)).filter(Lead.quote_accepted_date.isnot(None)).scalar()
    kyc_complete = db.query(func.count(Lead.id)).filter(Lead.kyc_complete_date.isnot(None)).scalar()
    activated = db.query(func.count(Lead.id)).filter(Lead.outcome == "Activated").scalar()

    return {
        "funnel": [
            {"stage": "Lead", "count": total, "pct_of_previous": None},
            {"stage": "Contacted", "count": contacted, "pct_of_previous": round(contacted/total*100, 1) if total else 0},
            {"stage": "Needs Assessed", "count": needs_assessed, "pct_of_previous": round(needs_assessed/contacted*100, 1) if contacted else 0},
            {"stage": "Quote Accepted", "count": quote_accepted, "pct_of_previous": round(quote_accepted/needs_assessed*100, 1) if needs_assessed else 0},
            {"stage": "KYC Complete", "count": kyc_complete, "pct_of_previous": round(kyc_complete/quote_accepted*100, 1) if quote_accepted else 0},
            {"stage": "Activated", "count": activated, "pct_of_previous": round(activated/kyc_complete*100, 1) if kyc_complete else 0},
        ],
        "lead_to_activation_pct": round(activated/total*100, 2) if total else 0,
    }


@router.get("/analytics/segments")
def segment_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(
        Lead.segment,
        func.count(Lead.id).label("total"),
        func.sum(case((Lead.outcome == "Activated", 1), else_=0)).label("activated"),
        func.avg(Lead.days_lead_to_activation).label("avg_days"),
        func.avg(Lead.monthly_bundle_value_inr).label("avg_bundle_value"),
    ).group_by(Lead.segment).all()

    return [
        {
            "segment": r.segment,
            "total": r.total,
            "activated": r.activated or 0,
            "conversion_pct": round((r.activated or 0) / r.total * 100, 1) if r.total else 0,
            "avg_activation_days": round(float(r.avg_days), 1) if r.avg_days else None,
            "avg_bundle_value_inr": round(float(r.avg_bundle_value), 0) if r.avg_bundle_value else None,
        } for r in rows
    ]


@router.get("/analytics/sources")
def source_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(
        Lead.lead_source,
        func.count(Lead.id).label("total"),
        func.sum(case((Lead.outcome == "Activated", 1), else_=0)).label("activated"),
        func.avg(Lead.acquisition_cost_inr).label("avg_cac"),
    ).group_by(Lead.lead_source).all()

    return [
        {
            "source": r.lead_source,
            "total": r.total,
            "activated": r.activated or 0,
            "conversion_pct": round((r.activated or 0) / r.total * 100, 1) if r.total else 0,
            "avg_cac_inr": round(float(r.avg_cac), 0) if r.avg_cac else None,
        } for r in rows
    ]


@router.get("/analytics/drop-reasons")
def drop_reasons(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(
        Lead.drop_reason,
        func.count(Lead.id).label("count"),
    ).filter(Lead.outcome == "Dropped", Lead.drop_reason.isnot(None)).group_by(Lead.drop_reason).order_by(func.count(Lead.id).desc()).all()

    return [{"reason": r.drop_reason, "count": r.count} for r in rows]


@router.get("/analytics/gstin")
def gstin_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    with_gstin = db.query(
        func.count(Lead.id).label("total"),
        func.sum(case((Lead.outcome == "Activated", 1), else_=0)).label("activated"),
    ).filter(Lead.has_gstin == True).one()

    without_gstin = db.query(
        func.count(Lead.id).label("total"),
        func.sum(case((Lead.outcome == "Activated", 1), else_=0)).label("activated"),
    ).filter(Lead.has_gstin == False).one()

    return {
        "with_gstin": {
            "total": with_gstin.total,
            "activated": with_gstin.activated or 0,
            "conversion_pct": round((with_gstin.activated or 0) / with_gstin.total * 100, 1) if with_gstin.total else 0,
        },
        "without_gstin": {
            "total": without_gstin.total,
            "activated": without_gstin.activated or 0,
            "conversion_pct": round((without_gstin.activated or 0) / without_gstin.total * 100, 1) if without_gstin.total else 0,
        },
    }


@router.get("/high-intent")
def high_intent_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    limit: int = 20,
):
    # High-intent: reached quote or KYC but didn't activate
    leads = db.query(Lead).filter(
        Lead.outcome == "Dropped",
        Lead.stage_reached.in_(["Quote accepted", "KYC complete"]),
    ).order_by(Lead.monthly_telecom_spend_inr.desc().nullslast()).limit(limit).all()

    return [_lead_summary(l) for l in leads]


@router.get("/abandoned-quotes")
def abandoned_quotes(db: Session = Depends(get_db), current_user: User = Depends(require_admin), limit: int = 20):
    leads = db.query(Lead).filter(
        Lead.outcome == "Dropped",
        Lead.stage_reached == "Quote accepted",
    ).limit(limit).all()
    return [_lead_summary(l) for l in leads]


@router.get("/kyc-exceptions")
def kyc_exceptions(db: Session = Depends(get_db), current_user: User = Depends(require_admin), limit: int = 20):
    leads = db.query(Lead).filter(
        Lead.drop_reason.contains("KYC") if Lead.drop_reason else False,
    ).limit(limit).all()
    return [_lead_summary(l) for l in leads]


@router.get("/{lead_id}")
def get_lead(lead_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    return _lead_summary(lead, full=True)


def _lead_summary(lead: Lead, full: bool = False) -> dict:
    base = {
        "id": lead.id,
        "business_name": lead.business_name,
        "business_type": lead.business_type,
        "segment": lead.segment,
        "city": lead.city,
        "city_tier": lead.city_tier,
        "lead_source": lead.lead_source,
        "stage_reached": lead.stage_reached,
        "outcome": lead.outcome,
        "drop_reason": lead.drop_reason,
        "has_gstin": lead.has_gstin,
        "employee_count": lead.employee_count,
        "monthly_telecom_spend_inr": lead.monthly_telecom_spend_inr,
        "monthly_bundle_value_inr": lead.monthly_bundle_value_inr,
        "propensity_score": lead.propensity_score,
        "created_date": str(lead.created_date) if lead.created_date else None,
    }
    if full:
        base.update({
            "contact_name": lead.contact_name,
            "contact_role": lead.contact_role,
            "num_sites": lead.num_sites,
            "annual_turnover_band": lead.annual_turnover_band,
            "activation_days": lead.days_lead_to_activation,
            "nps_score": lead.nps_score,
            "churned": lead.churned_within_6_months,
            "acquisition_cost_inr": lead.acquisition_cost_inr,
            "bundle_products": lead.bundle_products,
        })
    return base
