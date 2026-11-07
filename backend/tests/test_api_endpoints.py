"""Integration tests for API route logic and service handlers."""
import pytest
from app.main import health, root
from app.core.database import SessionLocal
from app.models import User
from app.api.routes.products import list_products, get_product
from app.api.routes.advisor import list_personas, start_conversation, StartRequest
from app.api.routes.recommendations import generate_recommendation, RecommendRequest
from app.api.routes.analytics import overview, bundle_popularity, churn_analysis, nps_distribution
from app.api.routes.leads import get_funnel


def test_health_and_root_endpoints():
    h = health()
    assert h["status"] == "ok"
    assert "version" in h

    r = root()
    assert "Udyam Digital API" in r["message"]


def test_products_endpoint():
    db = SessionLocal()
    try:
        products = list_products(db=db)
        assert len(products) == 25
        categories = {p["category"] for p in products}
        assert "Connectivity" in categories
        assert "Security" in categories

        p01 = get_product(product_id="P01", db=db)
        assert p01["id"] == "P01"
        assert p01["product_name"] == "Biz Fibre 100"
    finally:
        db.close()


def test_advisor_personas_endpoint():
    personas = list_personas()
    assert len(personas) >= 3
    keys = {p["key"] for p in personas}
    assert "kirana" in keys
    assert "clinic" in keys
    assert "multi_retail" in keys


def test_advisor_start_endpoint():
    db = SessionLocal()
    try:
        req = StartRequest(persona="kirana", session_id="test-session-123")
        res = start_conversation(req=req, db=db, current_user=None)
        assert res.conversation_id is not None
        assert "Gupta General Store" in res.message or "Kirana" in res.message
        assert res.state["completed"] is True
    finally:
        db.close()


def test_recommendation_generate_endpoint():
    db = SessionLocal()
    try:
        req = RecommendRequest(
            profile={
                "segment": "micro",
                "city_tier": 2,
                "employee_count": 2,
                "num_sites": 1,
                "has_gstin": False,
                "needs_broadband": True,
                "needs_pos": True,
                "needs_mobile_sims": 1,
            }
        )
        res = generate_recommendation(req=req, db=db, current_user=None)
        assert len(res["primary_bundle"]) >= 2
        assert res["total_monthly_inr"] > 0
        pids = [item["product_id"] for item in res["primary_bundle"]]
        assert "P19" in pids  # Cloud POS
    finally:
        db.close()


def test_analytics_overview_endpoint():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.role == "admin").first()
        res = overview(db=db, current_user=admin_user)
        assert res["total_leads"] == 5000
        assert res["activated"] == 368
        assert 7.0 <= res["lead_to_activation_pct"] <= 8.0
        assert 17.0 <= res["avg_activation_days"] <= 18.0
        assert res["avg_cac_inr"] > 0
    finally:
        db.close()


def test_leads_funnel_endpoint():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.role == "admin").first()
        res = get_funnel(db=db, current_user=admin_user)
        assert len(res["funnel"]) == 6
        assert res["funnel"][0]["count"] == 5000
        assert res["funnel"][5]["count"] == 368
        assert 7.0 <= res["lead_to_activation_pct"] <= 8.0
    finally:
        db.close()


def test_bundle_popularity_and_churn():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.role == "admin").first()
        bundles = bundle_popularity(db=db, current_user=admin_user)
        assert len(bundles) > 0

        churn = churn_analysis(db=db, current_user=admin_user)
        assert len(churn) >= 4  # micro, prof, multi, mfg
    finally:
        db.close()
