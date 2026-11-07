"""Unit tests for Smart KYC, Document Verification and Registry Lookups."""
import pytest
from datetime import date
from app.services.kyc_service import (
    validate_gstin_format,
    lookup_gstin,
    lookup_udyam,
    verify_document,
    cross_check_documents,
    extract_gstin_fields,
    extract_udyam_fields,
    extract_address_proof_fields,
    REFERENCE_DATE,
)


def test_gstin_format_validation():
    # Valid test GSTIN (4th char of PAN is 'X')
    # Format: 2-digit state + 3-char + 'X' + 1-char + 4-digit + 1-char + 1-alphanumeric + 'Z' + 1-alphanumeric
    valid_test_gstin = "27AAAXA1234F1Z5"
    ok, msg = validate_gstin_format(valid_test_gstin)
    assert ok, f"Expected valid format, got: {msg}"

    # Invalid: length != 15
    ok, msg = validate_gstin_format("27AAAXA1234F1Z")
    assert not ok
    assert "15 characters" in msg

    # Invalid: 4th char of PAN is not 'X' (as per test data requirement)
    ok, msg = validate_gstin_format("27AAAPA1234F1Z5")
    assert not ok
    assert "4th character of PAN must be X" in msg


def test_gstin_registry_lookup(gstin_reg):
    assert len(gstin_reg) > 3000
    # Pick first key from registry
    sample_gstin = next(iter(gstin_reg.keys()))
    res = lookup_gstin(sample_gstin)
    assert res["status"] == "found"
    assert res["record"]["gstin"] == sample_gstin
    assert "principal_place_masked" in res["record"]
    # PII privacy check: masked address
    assert "***" in res["record"]["principal_place_masked"]

    # Non-existent valid format GSTIN
    res_fake = lookup_gstin("27AAAXA9999Z1Z9")
    assert res_fake["status"] == "not_found"


def test_udyam_registry_lookup(udyam_reg):
    assert len(udyam_reg) > 2500
    sample_udyam = next(iter(udyam_reg.keys()))
    res = lookup_udyam(sample_udyam)
    assert res["status"] == "found"
    assert res["record"]["udyam_number"] == sample_udyam

    res_fake = lookup_udyam("UDYAM-XX-00-9999999")
    assert res_fake["status"] == "not_found"


def test_address_proof_age_validation():
    # Test valid recent address proof (< 90 days from 2026-07-15)
    # 2026-06-01 is 44 days old -> should be verified
    status, notes, _ = verify_document(
        doc_type="address_proof",
        extracted_fields={"document_date": "01/06/2026"},
        ocr_status="success"
    )
    assert status == "verified"
    assert "within acceptable range" in notes

    # Test expired address proof (> 90 days from 2026-07-15)
    # 2026-01-10 is > 180 days old -> should FAIL
    status, notes, _ = verify_document(
        doc_type="address_proof",
        extracted_fields={"document_date": "10/01/2026"},
        ocr_status="success"
    )
    assert status == "failed"
    assert "old" in notes


def test_missing_document_handling():
    # Applicant K05 has missing Udyam certificate
    documents = [
        {"doc_type": "gst_certificate", "extracted_fields": {"gstin": "27AAAXA1234F1Z5"}, "verification_status": "verified"},
        {"doc_type": "signatory_id", "extracted_fields": {"name": "Test Signatory"}, "verification_status": "verified"},
        {"doc_type": "address_proof", "extracted_fields": {"document_date": "01/06/2026"}, "verification_status": "verified"},
        # No udyam_certificate
    ]
    cross_results = cross_check_documents(documents)
    assert cross_results["gst_udyam_name_match"]["status"] == "skip"
    assert "Udyam Certificate" in cross_results["gst_udyam_name_match"]["message"]
    assert cross_results["required_documents"]["status"] == "pass"


def test_cancelled_gstin_status_rejection():
    # K01 specimen GSTIN has status 'Cancelled' in mock_gstin_registry.csv
    status, notes, res = verify_document(
        doc_type="gst_certificate",
        extracted_fields={"gstin": "37IHKXV5167L1ZS", "legal_name": "Neha Kaur (Prop. Vindhya Tours & Travels)"},
        ocr_status="success"
    )
    assert status == "failed"
    assert "Cancelled" in notes


def test_specimen_fallback_ocr():
    from app.services.kyc_service import run_ocr
    txt, status = run_ocr("dummy_path", "K01_gst_certificate.png")
    assert status == "success"
    assert "37IHKXV5167L1ZS" in txt
