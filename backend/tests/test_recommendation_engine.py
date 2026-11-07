"""Unit tests for the Deterministic Recommendation Engine."""
import pytest
from app.services.recommendation_engine import (
    RecommendationEngine, BusinessProfile, get_catalogue
)


def test_catalogue_loads_all_25_products():
    catalogue = get_catalogue()
    assert len(catalogue) == 25
    assert "P01" in catalogue
    assert "P25" in catalogue
    for pid, p in catalogue.items():
        assert p["price_min"] <= p["price_max"]
        assert p["install_days"] >= 0


def test_micro_kirana_recommendation(engine_instance):
    # Kirana store: micro, 2 employees, 1 site, Tier 2, no GSTIN, needs broadband + POS + 1 SIM
    profile = BusinessProfile(
        segment="micro",
        city_tier=2,
        employee_count=2,
        num_sites=1,
        has_gstin=False,
        needs_broadband=True,
        needs_mobile_sims=1,
        needs_pos=True,
        budget_monthly_inr=2000,
    )
    result = engine_instance.recommend(profile)
    pids = [item.product_id for item in result.primary_bundle]

    # In tier 2 without GSTIN, P04 (5G AirFiber) or P01 (Biz Fibre 100)
    assert any(pid in pids for pid in ["P01", "P04"])
    assert "P07" in pids  # Postpaid 299 for 1 SIM
    assert "P19" in pids  # POS machine
    # Products requiring GSTIN must NOT be in bundle
    assert "P03" not in pids
    assert "P05" not in pids
    assert "P10" not in pids
    assert result.total_monthly_inr > 0


def test_professional_clinic_recommendation(engine_instance):
    # Clinic: prof, 8 employees, 1 site, Tier 1, GSTIN, needs broadband + email + CCTV + backup
    profile = BusinessProfile(
        segment="prof",
        city_tier=1,
        employee_count=8,
        num_sites=1,
        has_gstin=True,
        needs_broadband=True,
        needs_cloud_email=True,
        needs_cctv=2,
        needs_backup=True,
        budget_monthly_inr=8000,
    )
    result = engine_instance.recommend(profile)
    pids = [item.product_id for item in result.primary_bundle]

    assert "P03" in pids or "P02" in pids  # High-speed fibre
    assert "P16" in pids  # Cloud email
    assert "P23" in pids  # CCTV
    assert "P17" in pids  # Cloud backup

    # Verify CCTV quantity matches profile
    cctv_item = next(it for it in result.primary_bundle if it.product_id == "P23")
    assert cctv_item.quantity == 2


def test_multi_site_retail_sdwan_dependency(engine_instance):
    # Multi-site: 4 sites, 25 employees, Tier 1, GSTIN
    profile = BusinessProfile(
        segment="multi",
        city_tier=1,
        employee_count=25,
        num_sites=4,
        has_gstin=True,
        needs_broadband=True,
        needs_firewall=True,
    )
    result = engine_instance.recommend(profile)
    pids = [item.product_id for item in result.primary_bundle]

    # Must include multi-site connectivity
    assert "P02" in pids or "P05" in pids
    # Multi-site with >= 2 sites gets backup failover P09
    assert "P09" in pids


def test_gstin_eligibility_enforcement(engine_instance):
    # Non-GSTIN user trying to request GST-restricted services
    profile = BusinessProfile(
        segment="micro",
        city_tier=1,
        employee_count=2,
        num_sites=1,
        has_gstin=False,
        needs_whatsapp=True,
        needs_toll_free=True,
    )
    result = engine_instance.recommend(profile)
    pids = [item.product_id for item in result.primary_bundle]

    # WhatsApp (P15) and Toll-Free (P13) require GSTIN
    assert "P15" not in pids
    assert "P13" not in pids
    # Ineligibility reasons should be reported in ineligible dictionary
    ineligible = result.eligibility_checks.get("ineligible", {})
    assert "P15" in ineligible
    assert "P13" in ineligible


def test_city_tier_restriction(engine_instance):
    # P03 (Biz Fibre 1G) is Tier 1 only. In Tier 2 it must not be recommended.
    profile = BusinessProfile(
        segment="prof",
        city_tier=2,
        employee_count=6,
        num_sites=1,
        has_gstin=True,
        needs_broadband=True,
    )
    result = engine_instance.recommend(profile)
    pids = [item.product_id for item in result.primary_bundle]
    assert "P03" not in pids
