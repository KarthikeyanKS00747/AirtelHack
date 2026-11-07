from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.core.database import get_db
from app.core.security import require_admin
from app.models import Lead, User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total = db.query(func.count(Lead.id)).scalar()
    activated = db.query(func.count(Lead.id)).filter(Lead.outcome == "Activated").scalar()
    avg_days = db.query(func.avg(Lead.days_lead_to_activation)).filter(Lead.outcome == "Activated").scalar()
    avg_cac = db.query(func.avg(Lead.acquisition_cost_inr)).filter(Lead.outcome == "Activated").scalar()
    avg_bundle = db.query(func.avg(Lead.monthly_bundle_value_inr)).filter(Lead.outcome == "Activated").scalar()
    churned = db.query(func.count(Lead.id)).filter(Lead.churned_within_6_months == True).scalar()
    avg_nps = db.query(func.avg(Lead.nps_score)).filter(Lead.outcome == "Activated").scalar()

    return {
        "total_leads": total,
        "activated": activated,
        "lead_to_activation_pct": round(activated / total * 100, 2) if total else 0,
        "avg_activation_days": round(float(avg_days), 1) if avg_days else None,
        "avg_cac_inr": round(float(avg_cac), 0) if avg_cac else None,
        "avg_monthly_bundle_inr": round(float(avg_bundle), 0) if avg_bundle else None,
        "churn_count": churned,
        "churn_rate_pct": round(churned / activated * 100, 1) if activated else 0,
        "avg_nps": round(float(avg_nps), 1) if avg_nps else None,
        "note": "All figures derived from April–June 2026 hackathon dataset (reference date: 2026-07-15)",
    }


@router.get("/bundle-popularity")
def bundle_popularity(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(Lead.bundle_products).filter(Lead.outcome == "Activated", Lead.bundle_products.isnot(None)).all()
    from collections import Counter
    product_counts: Counter = Counter()
    for (bp,) in rows:
        if bp:
            for item in bp.split(";"):
                pid = item.split("x")[0] if "x" in item else item
                if pid:
                    product_counts[pid.strip()] += 1

    return [{"product_id": pid, "count": cnt} for pid, cnt in product_counts.most_common(15)]


@router.get("/churn-analysis")
def churn_analysis(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(
        Lead.segment,
        func.sum(case((Lead.churned_within_6_months == True, 1), else_=0)).label("churned"),
        func.sum(case((Lead.outcome == "Activated", 1), else_=0)).label("activated"),
    ).group_by(Lead.segment).all()

    return [
        {
            "segment": r.segment,
            "activated": r.activated or 0,
            "churned": r.churned or 0,
            "churn_rate_pct": round((r.churned or 0) / (r.activated or 1) * 100, 1),
        } for r in rows
    ]


@router.get("/nps-distribution")
def nps_distribution(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(
        Lead.nps_score,
        func.count(Lead.id).label("count"),
    ).filter(Lead.nps_score.isnot(None)).group_by(Lead.nps_score).order_by(Lead.nps_score).all()

    promoters = sum(r.count for r in rows if r.nps_score and r.nps_score >= 9)
    passives = sum(r.count for r in rows if r.nps_score and 7 <= r.nps_score <= 8)
    detractors = sum(r.count for r in rows if r.nps_score and r.nps_score <= 6)
    total_resp = promoters + passives + detractors
    nps = round((promoters - detractors) / total_resp * 100, 1) if total_resp else 0

    return {
        "distribution": [{"score": r.nps_score, "count": r.count} for r in rows],
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "nps_score": nps,
    }
