from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import BusinessProfile, Recommendation, Bundle, BundleItem, Product, User, Conversation
from app.services.recommendation_engine import (
    RecommendationEngine, BusinessProfile as EngineProfile, get_catalogue
)
import uuid

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])
_engine = RecommendationEngine()


class RecommendRequest(BaseModel):
    business_profile_id: Optional[str] = None
    conversation_id: Optional[str] = None
    # Or pass profile directly
    profile: Optional[dict] = None


@router.post("/generate")
def generate_recommendation(
    req: RecommendRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    # Get profile data
    if req.business_profile_id:
        bp = db.query(BusinessProfile).filter(BusinessProfile.id == req.business_profile_id).first()
        if not bp:
            raise HTTPException(404, "Business profile not found")
        profile_data = {
            "segment": bp.segment or "micro",
            "city_tier": bp.city_tier or 1,
            "employee_count": bp.employee_count or 1,
            "num_sites": bp.num_sites or 1,
            "has_gstin": bp.has_gstin or False,
            "needs_broadband": bp.needs_broadband,
            "needs_mobile_sims": bp.needs_mobile_sims,
            "needs_cloud_email": bp.needs_cloud_email,
            "needs_pos": bp.needs_pos,
            "needs_cctv": bp.needs_cctv,
            "needs_backup": bp.needs_backup,
            "needs_website": bp.needs_website,
            "needs_whatsapp": bp.needs_whatsapp,
            "needs_toll_free": bp.needs_toll_free,
            "needs_sms": bp.needs_sms,
            "needs_firewall": bp.needs_firewall,
            "needs_fleet_tracking": bp.needs_fleet_tracking,
            "budget_monthly_inr": bp.budget_monthly_inr,
        }
    elif req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
        if not conv:
            raise HTTPException(404, "Conversation not found")
        profile_data = conv.extracted_profile or {}
        # Also get/create business profile
        if conv.business_profile_id:
            bp_id = conv.business_profile_id
        else:
            bp_id = None
    elif req.profile:
        profile_data = req.profile
        bp_id = None
    else:
        raise HTTPException(400, "Provide business_profile_id, conversation_id, or profile")

    # Build engine profile
    ep = EngineProfile(
        segment=profile_data.get("segment", "micro"),
        city_tier=int(profile_data.get("city_tier", 1)),
        employee_count=int(profile_data.get("employee_count", 1)),
        num_sites=int(profile_data.get("num_sites", 1)),
        has_gstin=bool(profile_data.get("has_gstin", False)),
        needs_broadband=bool(profile_data.get("needs_broadband", True)),
        needs_mobile_sims=int(profile_data.get("needs_mobile_sims", 0)),
        needs_cloud_email=bool(profile_data.get("needs_cloud_email", False)),
        needs_pos=bool(profile_data.get("needs_pos", False)),
        needs_cctv=int(profile_data.get("needs_cctv", 0)),
        needs_backup=bool(profile_data.get("needs_backup", False)),
        needs_website=bool(profile_data.get("needs_website", False)),
        needs_whatsapp=bool(profile_data.get("needs_whatsapp", False)),
        needs_toll_free=bool(profile_data.get("needs_toll_free", False)),
        needs_sms=bool(profile_data.get("needs_sms", False)),
        needs_firewall=bool(profile_data.get("needs_firewall", False)),
        needs_fleet_tracking=int(profile_data.get("needs_fleet_tracking", 0)),
        budget_monthly_inr=profile_data.get("budget_monthly_inr"),
    )

    result = _engine.recommend(ep)

    # Persist recommendation
    bp_id_to_use = req.business_profile_id or (conv.business_profile_id if req.conversation_id else None)
    
    if bp_id_to_use:
        rec = Recommendation(
            business_profile_id=bp_id_to_use,
            primary_bundle=[{
                "product_id": i.product_id,
                "product_name": i.product_name,
                "category": i.category,
                "description": i.description,
                "unit": i.unit,
                "quantity": i.quantity,
                "unit_price_inr": i.unit_price_inr,
                "monthly_cost_inr": i.monthly_cost_inr,
                "setup_cost_inr": i.setup_cost_inr,
                "is_mandatory": i.is_mandatory,
                "reason": i.reason,
                "install_days": i.install_days,
            } for i in result.primary_bundle],
            alternative_bundles=result.alternative_bundles,
            total_monthly_inr=result.total_monthly_inr,
            total_setup_inr=result.total_setup_inr,
            explanation=result.explanation,
            eligibility_checks=result.eligibility_checks,
            score=result.score,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        rec_id = rec.id
    else:
        rec_id = None

    return {
        "recommendation_id": rec_id,
        "primary_bundle": [
            {
                "product_id": i.product_id,
                "product_name": i.product_name,
                "category": i.category,
                "description": i.description,
                "unit": i.unit,
                "quantity": i.quantity,
                "unit_price_inr": i.unit_price_inr,
                "monthly_cost_inr": i.monthly_cost_inr,
                "setup_cost_inr": i.setup_cost_inr,
                "is_mandatory": i.is_mandatory,
                "reason": i.reason,
                "install_days": i.install_days,
            } for i in result.primary_bundle
        ],
        "alternative_bundles": result.alternative_bundles,
        "total_monthly_inr": result.total_monthly_inr,
        "total_setup_inr": result.total_setup_inr,
        "estimated_installation_days": result.estimated_installation_days,
        "explanation": result.explanation,
        "eligibility_checks": result.eligibility_checks,
        "score": result.score,
    }


@router.get("/{recommendation_id}")
def get_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    return rec
