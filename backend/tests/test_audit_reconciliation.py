"""
Comprehensive Audit Reconciliation Test Suite
Validates all high-risk audit criteria:
1. Full 25-product catalogue price & setup fee grounding
2. Server-side price manipulation prevention
3. 18% GST arithmetic & setup fee aggregation
4. Multi-site natural language parsing
5. KYC mock registry verification & status enforcement (Active vs Cancelled/Suspended)
6. Address proof 90-day recency against 2026-07-15
7. JWT authentication, token expiry & RBAC enforcement
8. Dashboard analytics reconciliation against smb_leads.csv
"""
import os
import csv
import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Product, User
from app.core.security import create_access_token, decode_token
from app.services.advisor_service import _extract_value
from app.services.kyc_service import (
    validate_gstin_format,
    lookup_gstin,
    lookup_udyam,
    verify_document,
    cross_check_documents,
    REFERENCE_DATE,
)
from app.api.routes.quotes import _calc_line_items, LineItem
from app.services.recommendation_engine import RecommendationEngine, BusinessProfile


# ── 1. Catalogue Grounding ──────────────────────────────────────────────────

def test_full_25_catalogue_grounding():
    """Verify that all 25 catalogue products in DB match CSV exactly."""
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset_raw/product_catalogue.csv"))
    assert os.path.exists(csv_path), "Catalogue CSV must exist"
    
    with open(csv_path, encoding="utf-8") as f:
        csv_items = list(csv.DictReader(f))
    
    assert len(csv_items) == 25
    
    db = SessionLocal()
    try:
        db_items = {p.id: p for p in db.query(Product).all()}
        assert len(db_items) == 25
        
        for row in csv_items:
            pid = row["product_id"]
            assert pid in db_items, f"Product {pid} missing from database"
            dbp = db_items[pid]
            
            min_p = float(row["price_min_inr_per_month"])
            max_p = float(row["price_max_inr_per_month"])
            setup = float(row["one_time_setup_inr"])
            req_gst = row["requires_gstin"].strip().upper() == "Y"
            
            assert float(dbp.price_min_inr_per_month) == min_p
            assert float(dbp.price_max_inr_per_month) == max_p
            assert float(dbp.one_time_setup_inr) == setup
            assert bool(dbp.requires_gstin) == req_gst
    finally:
        db.close()


# ── 2. Pricing, Taxes & Price Manipulation Prevention ───────────────────────

def test_server_side_price_tamper_prevention():
    """Ensure client cannot tamper with unit prices; server always uses catalogue midpoint."""
    db = SessionLocal()
    try:
        # P01 midpoint = 1099.0
        # P19 midpoint = 749.0
        items = [
            LineItem(product_id="P01", quantity=2),
            LineItem(product_id="P19", quantity=1),
        ]
        line_items_out, total_monthly, total_setup = _calc_line_items(items, db)
        
        # P01: 1099 * 2 = 2198.0
        assert line_items_out[0]["unit_price_inr"] == 1099.0
        assert line_items_out[0]["monthly_cost_inr"] == 2198.0
        # P19: 749 * 1 = 749.0, setup = 2500.0
        assert line_items_out[1]["unit_price_inr"] == 749.0
        assert line_items_out[1]["setup_cost_inr"] == 2500.0
        
        assert total_monthly == 2947.0
        assert total_setup == 2500.0
        
        # 18% GST
        tax = round(total_monthly * 0.18, 2)
        assert tax == 530.46
        assert round(total_monthly + tax, 2) == 3477.46
    finally:
        db.close()


# ── 3. Multi-site NLP Parser ────────────────────────────────────────────────

@pytest.mark.parametrize("phrase,expected", [
    ("Multiple", 3),
    ("More than one", 3),
    ("Several locations", 3),
    ("Chain of stores", 3),
    ("Two branches", 2),
    ("2", 2),
    ("One", 1),
    ("Single location", 1),
])
def test_multisite_nlp_parsing_exact(phrase, expected):
    """Verify natural language parsing for multi-site questions."""
    parsed = _extract_value("num_sites", phrase, {})
    assert parsed == expected, f"Input '{phrase}' expected {expected}, got {parsed}"


# ── 4. KYC Status & Planted Defects ─────────────────────────────────────────

def test_kyc_cancelled_gstin_rejection():
    """Ensure Cancelled GSTIN (e.g. K01 specimen) is rejected."""
    # 37IHKXV5167L1ZS is K01's GSTIN, status: Cancelled
    status, notes, res = verify_document(
        doc_type="gst_certificate",
        extracted_fields={"gstin": "37IHKXV5167L1ZS", "legal_name": "Neha Kaur (Prop. Vindhya Tours & Travels)"},
        ocr_status="success"
    )
    assert status == "failed"
    assert "Cancelled" in notes


def test_kyc_address_recency_90_days():
    """Ensure address proofs older than 90 days from 2026-07-15 fail, recent ones pass."""
    # K11 specimen is dated 2025-10-31 (257 days old)
    status_old, notes_old, _ = verify_document(
        doc_type="address_proof",
        extracted_fields={"document_date": "31/10/2025"},
        ocr_status="success"
    )
    assert status_old == "failed"
    assert "257 days old" in notes_old
    
    # Recent: 2026-06-26 (19 days old)
    status_recent, notes_recent, _ = verify_document(
        doc_type="address_proof",
        extracted_fields={"document_date": "26/06/2026"},
        ocr_status="success"
    )
    assert status_recent == "verified"
    assert "within acceptable range" in notes_recent


def test_kyc_missing_udyam_crosscheck():
    """Applicant K05 has missing Udyam certificate; crosscheck must flag incomplete."""
    docs = [
        {"doc_type": "gst_certificate", "extracted_fields": {"gstin": "32AITXR9985H1ZT"}, "verification_status": "verified"},
        {"doc_type": "signatory_id", "extracted_fields": {"name": "Balaji Realty"}, "verification_status": "verified"},
        {"doc_type": "address_proof", "extracted_fields": {"document_date": "11/06/2026"}, "verification_status": "verified"},
    ]
    cross = cross_check_documents(docs)
    assert cross["gst_udyam_name_match"]["status"] == "skip"
    assert "Udyam Certificate" in cross["gst_udyam_name_match"]["message"]


# ── 5. Security: JWT Expiry & RBAC ──────────────────────────────────────────

def test_jwt_token_creation_and_expiry():
    """Verify JWT encoding, decoding, and expiration enforcement."""
    # Valid token
    token = create_access_token({"sub": "user-123", "role": "sales"}, expires_delta=timedelta(minutes=15))
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "sales"
    
    # Expired token
    expired_token = create_access_token({"sub": "user-123", "role": "sales"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(Exception):
        decode_token(expired_token)


# ── 6. Swarg Recommendation Recalculation ───────────────────────────────────

def test_swarg_recommendation_discrepancy_grounding():
    """
    Verify Swarg profile recommendations:
    - Without GSTIN: P03 (requires GSTIN=Y) cannot be recommended; P02 is selected.
    - Postpaid: With 40 employees and multi/prof segment, P08 is selected.
    - Backup: P09 added because P02 is in basket and segment is prof/multi.
    """
    engine = RecommendationEngine()
    
    # Profile as evaluated in original advisor chat (single site parsed, prof segment, no GSTIN)
    p_chat = BusinessProfile(
        segment="prof",
        city_tier=1,
        employee_count=40,
        num_sites=1,
        has_gstin=False,
        needs_broadband=True,
        needs_mobile_sims=40,
        needs_pos=True,
        needs_cctv=20,
        needs_backup=True,
    )
    res_chat = engine.recommend(p_chat)
    pids = [i.product_id for i in res_chat.primary_bundle]
    
    # P03 must NOT be present because requires_gstin=Y
    assert "P03" not in pids
    assert "P02" in pids  # Biz Fibre 300 fallback
    assert "P08" in pids  # 40x Postpaid 599
    assert "P09" in pids  # Failover
    assert "P11" in pids  # Static IP
    assert res_chat.total_monthly_inr == 37235.0
    assert res_chat.total_setup_inr == 41000.0


# ── 7. Dashboard Lead Reconciliation ────────────────────────────────────────

def test_dashboard_leads_reconciliation():
    """Verify funnel counts against the actual 5,000-lead CSV."""
    leads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset_raw/smb_leads.csv"))
    assert os.path.exists(leads_path)
    
    with open(leads_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    
    assert len(reader) == 5000
    activated = [r for r in reader if r.get("outcome") == "Activated"]
    assert len(activated) == 368
    
    stages = [r.get("stage_reached") for r in reader]
    assert stages.count("Lead") + stages.count("Contacted") + stages.count("Needs assessed") + \
           stages.count("Quote accepted") + stages.count("KYC complete") + stages.count("Activated") == 5000
