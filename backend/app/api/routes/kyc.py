from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models import (
    KYCSubmission, KYCDocument, KYCSubmission, Order,
    ConsentRecord, AuditEvent, User
)
from app.services.kyc_service import (
    run_ocr, extract_fields_by_type, verify_document,
    cross_check_documents, determine_overall_result,
    lookup_gstin, lookup_udyam
)

router = APIRouter(prefix="/api/kyc", tags=["kyc"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024
DOC_TYPES = {"gst_certificate", "udyam_certificate", "signatory_id", "address_proof"}


class ConsentRequest(BaseModel):
    order_id: str
    consented: bool = True
    session_id: Optional[str] = None


@router.post("/consent")
def record_consent(
    data: ConsentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.consented:
        raise HTTPException(400, "Consent is required to proceed with KYC")

    consent = ConsentRecord(
        user_id=current_user.id,
        purpose="kyc_processing",
        consent_text_version="1.0",
        consented=True,
        ip_address=request.client.host if request.client else None,
    )
    db.add(consent)

    # Create KYC submission
    submission = KYCSubmission(
        order_id=data.order_id,
        user_id=current_user.id,
        consent_record_id=None,  # will set after flush
        status="pending",
    )
    db.add(submission)
    db.flush()

    consent.id = consent.id  # already set
    submission.consent_record_id = consent.id

    # Advance order to kyc_pending
    from app.models import Order, OrderMilestone
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if order and order.status == "placed":
        order.status = "kyc_pending"
        m = OrderMilestone(
            order_id=order.id,
            stage="kyc_pending",
            label="KYC Started",
            description="Customer has given consent and started KYC verification.",
            agent="system",
        )
        db.add(m)

    db.commit()
    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "message": "Consent recorded. You can now upload your documents.",
        "consent_notice": {
            "purpose": "KYC document processing for Accel Business service activation",
            "what_collected": ["GST Certificate", "Udyam Registration", "Signatory ID", "Address Proof"],
            "why_collected": "Regulatory requirement for business telecom service activation",
            "how_processed": "OCR extraction and matching against mock government registries",
            "retention_policy": "Documents retained for 90 days post-activation, then deleted",
            "withdrawal": "Contact support@accel.business to withdraw consent and delete your data",
            "grievance": "Grievance Officer: dpo@accel.business",
            "dpdp_compliance": "Processed in accordance with the Digital Personal Data Protection Act, 2023",
        }
    }


@router.post("/upload")
async def upload_document(
    submission_id: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate doc type
    if doc_type not in DOC_TYPES:
        raise HTTPException(400, f"Invalid doc_type. Must be one of: {DOC_TYPES}")

    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"File type {file.content_type} not allowed. Use JPEG, PNG, WebP or PDF.")

    # Check submission
    submission = db.query(KYCSubmission).filter(
        KYCSubmission.id == submission_id,
        KYCSubmission.user_id == current_user.id
    ).first()
    if not submission:
        raise HTTPException(404, "KYC submission not found")

    # Read and size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB} MB")

    # Store with UUID filename (no PII in filename)
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../uploads/kyc"))
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[-1] or ".png"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(upload_dir, stored_name)

    with open(stored_path, "wb") as f:
        f.write(content)

    # Create document record
    doc = KYCDocument(
        submission_id=submission_id,
        doc_type=doc_type,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_size_bytes=len(content),
        mime_type=file.content_type,
        ocr_status="pending",
        verification_status="pending",
    )
    db.add(doc)
    db.flush()

    # Run OCR
    ocr_text, ocr_status = run_ocr(stored_path, file.filename or "")
    doc.ocr_text = ocr_text[:5000] if ocr_text else None  # truncate for DB
    doc.ocr_status = ocr_status

    # Extract fields
    extracted = extract_fields_by_type(doc_type, ocr_text or "")
    doc.extracted_fields = extracted

    # Verify document
    ver_status, ver_notes, reg_result = verify_document(doc_type, extracted, ocr_status)
    doc.verification_status = ver_status
    doc.verification_notes = ver_notes
    doc.registry_result = reg_result
    doc.processed_at = datetime.utcnow()

    # Registry lookup status
    if doc_type == "gst_certificate":
        status_val = reg_result.get("status", "not_applicable") if reg_result else "not_applicable"
        doc.registry_lookup_status = "matched" if status_val == "found" else ("not_found" if status_val == "not_found" else "not_applicable")
    elif doc_type == "udyam_certificate":
        status_val = reg_result.get("status", "not_applicable") if reg_result else "not_applicable"
        doc.registry_lookup_status = "matched" if status_val == "found" else ("not_found" if status_val == "not_found" else "not_applicable")

    # Audit
    audit = AuditEvent(
        user_id=current_user.id,
        event_type="kyc_document_uploaded",
        resource_type="kyc_document",
        resource_id=doc.id,
        details={"doc_type": doc_type, "ocr_status": ocr_status, "verification_status": ver_status},
    )
    db.add(audit)

    submission.status = "processing"
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "doc_type": doc_type,
        "ocr_status": ocr_status,
        "extracted_fields": _mask_extracted_fields(extracted, doc_type),
        "verification_status": ver_status,
        "verification_notes": ver_notes,
        "registry_result": _mask_registry_result(reg_result),
    }


@router.post("/submissions/{submission_id}/verify")
def run_cross_verification(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submission = db.query(KYCSubmission).filter(
        KYCSubmission.id == submission_id,
        KYCSubmission.user_id == current_user.id,
    ).first()
    if not submission:
        raise HTTPException(404, "Submission not found")

    docs = db.query(KYCDocument).filter(KYCDocument.submission_id == submission_id).all()
    doc_list = [
        {
            "doc_type": d.doc_type,
            "extracted_fields": d.extracted_fields or {},
            "verification_status": d.verification_status,
        } for d in docs
    ]

    cross_results = cross_check_documents(doc_list)
    doc_statuses = [d.verification_status for d in docs]
    overall = determine_overall_result(cross_results, doc_statuses)

    submission.cross_check_results = cross_results
    submission.overall_result = overall
    submission.status = "verified" if overall == "verified" else ("needs_review" if overall == "needs_review" else "failed")

    # Advance order status
    if overall in ("verified", "needs_review"):
        order = db.query(Order).filter(Order.id == submission.order_id).first()
        if order and order.status in ("kyc_pending", "kyc_review"):
            from app.models import OrderMilestone
            new_status = "kyc_complete" if overall == "verified" else "kyc_review"
            order.status = new_status
            m = OrderMilestone(
                order_id=order.id,
                stage=new_status,
                label="KYC Complete" if overall == "verified" else "KYC Under Review",
                description=f"Automated verification result: {overall}",
                agent="system",
            )
            db.add(m)

    db.commit()

    return {
        "submission_id": submission_id,
        "overall_result": overall,
        "cross_check_results": cross_results,
        "document_statuses": [
            {"doc_type": d.doc_type, "status": d.verification_status, "notes": d.verification_notes}
            for d in docs
        ],
    }


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    submission = db.query(KYCSubmission).filter(
        KYCSubmission.id == submission_id,
        KYCSubmission.user_id == current_user.id,
    ).first()
    if not submission:
        raise HTTPException(404, "Submission not found")

    docs = db.query(KYCDocument).filter(KYCDocument.submission_id == submission_id).all()
    return {
        "id": submission.id,
        "order_id": submission.order_id,
        "status": submission.status,
        "overall_result": submission.overall_result,
        "cross_check_results": submission.cross_check_results,
        "documents": [
            {
                "id": d.id,
                "doc_type": d.doc_type,
                "original_filename": d.original_filename,
                "ocr_status": d.ocr_status,
                "extracted_fields": _mask_extracted_fields(d.extracted_fields or {}, d.doc_type),
                "verification_status": d.verification_status,
                "verification_notes": d.verification_notes,
                "registry_lookup_status": d.registry_lookup_status,
                "uploaded_at": str(d.uploaded_at),
            } for d in docs
        ],
    }


@router.post("/lookup/gstin")
def gstin_lookup(gstin: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = lookup_gstin(gstin)
    audit = AuditEvent(
        user_id=current_user.id,
        event_type="gstin_lookup",
        resource_type="gstin",
        resource_id=gstin[:6] + "***",  # masked
        details={"status": result["status"]},
    )
    db.add(audit)
    db.commit()
    return _mask_registry_result(result)


@router.post("/lookup/udyam")
def udyam_lookup(udyam_number: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = lookup_udyam(udyam_number)
    return result


def _mask_extracted_fields(fields: dict, doc_type: str) -> dict:
    """Mask sensitive fields in extracted data."""
    masked = dict(fields)
    if "gstin" in masked:
        g = masked["gstin"]
        masked["gstin"] = g[:6] + "***" + g[-4:] if len(g) == 15 else g  # partial mask
    return masked


def _mask_registry_result(result: Optional[dict]) -> Optional[dict]:
    if not result:
        return result
    masked = dict(result)
    if "record" in masked and masked["record"]:
        rec = dict(masked["record"])
        if "gstin" in rec:
            g = rec["gstin"]
            rec["gstin"] = g[:6] + "***" + g[-4:] if len(g) == 15 else g
        masked["record"] = rec
    return masked
