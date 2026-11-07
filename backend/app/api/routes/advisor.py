from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import BusinessProfile, Conversation, User
from app.services.advisor_service import DeterministicAdvisor, PERSONAS
from app.services.recommendation_engine import (
    RecommendationEngine, BusinessProfile as EngineProfile
)

router = APIRouter(prefix="/api/advisor", tags=["advisor"])
_advisor = DeterministicAdvisor()
_engine = RecommendationEngine()


class StartRequest(BaseModel):
    persona: Optional[str] = None
    session_id: Optional[str] = None


class MessageRequest(BaseModel):
    conversation_id: str
    message: str


class StartResponse(BaseModel):
    conversation_id: str
    message: str
    state: dict


class MessageResponse(BaseModel):
    conversation_id: str
    message: str
    is_complete: bool
    profile: Optional[dict] = None


@router.get("/personas")
def list_personas():
    return [
        {
            "key": k,
            "name": v["name"],
            "description": v["description"],
            "opening": v["opening"],
        }
        for k, v in PERSONAS.items()
    ]


@router.post("/start", response_model=StartResponse)
def start_conversation(
    req: StartRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    state, greeting = _advisor.start_conversation(persona=req.persona)

    # Persist conversation
    conv = Conversation(
        user_id=current_user.id if current_user else None,
        session_id=req.session_id,
        persona=req.persona,
        messages=[{"role": "assistant", "content": greeting}],
        status="active",
        extracted_profile={},
    )

    if state.get("completed") and req.persona:
        conv.extracted_profile = state["profile"]
        conv.status = "completed"

        # Create business profile
        prof = _build_business_profile(state["profile"], current_user)
        db.add(prof)
        db.flush()
        conv.business_profile_id = prof.id

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return StartResponse(
        conversation_id=conv.id,
        message=greeting,
        state=state,
    )


@router.post("/message", response_model=MessageResponse)
def send_message(
    req: MessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")

    # Restore state and process
    messages = list(conv.messages or [])
    profile = dict(conv.extracted_profile or {})
    idx = len([m for m in messages if m["role"] == "user"])

    state = {
        "profile": profile,
        "current_question_index": idx,
        "completed": conv.status == "completed",
    }

    # Add user message
    messages.append({"role": "user", "content": req.message})

    state, response, completed = _advisor.process_message(state, req.message)
    messages.append({"role": "assistant", "content": response})

    conv.messages = messages
    conv.extracted_profile = state["profile"]

    result_profile = None
    if completed:
        conv.status = "completed"
        result_profile = state["profile"]

        # Create/update business profile
        if not conv.business_profile_id:
            prof = _build_business_profile(state["profile"], current_user)
            db.add(prof)
            db.flush()
            conv.business_profile_id = prof.id

    db.commit()

    return MessageResponse(
        conversation_id=conv.id,
        message=response,
        is_complete=completed,
        profile=result_profile,
    )


@router.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return {
        "id": conv.id,
        "messages": conv.messages,
        "profile": conv.extracted_profile,
        "status": conv.status,
        "business_profile_id": conv.business_profile_id,
    }


def _build_business_profile(profile_data: dict, user: Optional[User]) -> BusinessProfile:
    return BusinessProfile(
        user_id=user.id if user else None,
        business_name=profile_data.get("business_name", ""),
        business_type=profile_data.get("business_type", ""),
        segment=profile_data.get("segment", "micro"),
        city=profile_data.get("city", ""),
        city_tier=int(profile_data.get("city_tier", 1)),
        state=profile_data.get("state", ""),
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
        raw_profile=profile_data,
    )
