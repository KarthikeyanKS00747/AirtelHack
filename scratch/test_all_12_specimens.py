import os
import sys
import glob

sys.path.insert(0, r"C:\Users\LENOVO\GitHubRepos\AirtelHack\backend")
sys.stdout.reconfigure(encoding='utf-8')

from app.services.kyc_service import (
    run_ocr, extract_fields_by_type, verify_document,
    cross_check_documents, determine_overall_result
)

kyc_dir = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\kyc_documents"
applicants = [f"K{i:02d}" for i in range(1, 13)]

print(f"{'Applicant':<10} | {'Doc Type':<18} | {'OCR Status':<12} | {'Extracted Preview':<30} | {'Verify Status':<14} | {'Notes / Defect'}")
print("-" * 125)

applicant_summaries = {}

for app in applicants:
    doc_results = []
    # Find files for this applicant
    pattern = os.path.join(kyc_dir, f"{app}_*.png")
    files = sorted(glob.glob(pattern))
    
    for fpath in files:
        fname = os.path.basename(fpath)
        # Determine doc_type from filename
        if "gst" in fname: doc_type = "gst_certificate"
        elif "udyam" in fname: doc_type = "udyam_certificate"
        elif "address" in fname: doc_type = "address_proof"
        elif "id" in fname or "signatory" in fname: doc_type = "signatory_id"
        else: doc_type = "unknown"
        
        # 1. OCR (tests specimen fallback when Tesseract CLI is absent)
        ocr_text, ocr_status = run_ocr(fpath, fname)
        
        # 2. Field extraction
        fields = extract_fields_by_type(doc_type, ocr_text)
        
        # 3. Verification
        status, notes, reg_res = verify_document(doc_type, fields, ocr_status)
        
        preview = ""
        if "gstin" in fields: preview += f"GSTIN: {fields['gstin']} "
        if "udyam_number" in fields: preview += f"Udyam: {fields['udyam_number']} "
        if "document_date" in fields: preview += f"Date: {fields['document_date']} "
        if "name" in fields: preview += f"Name: {fields['name'][:15]} "
        if not preview and ocr_text: preview = ocr_text[:25].replace("\n", " ")
        if not preview: preview = "(None extracted)"
        
        doc_results.append({
            "doc_type": doc_type,
            "filename": fname,
            "ocr_status": ocr_status,
            "extracted_fields": fields,
            "verification_status": status,
            "notes": notes,
            "registry_result": reg_res
        })
        
        print(f"{app:<10} | {doc_type:<18} | {ocr_status:<12} | {preview[:30]:<30} | {status:<14} | {notes[:45]}")
    
    # Cross-check across documents for applicant
    cross = cross_check_documents(doc_results)
    doc_statuses = [d["verification_status"] for d in doc_results]
    overall = determine_overall_result(cross, doc_statuses)
    applicant_summaries[app] = {
        "docs_submitted": len(files),
        "overall": overall,
        "cross": cross
    }

print("\n=== Summary of All 12 Applicants ===")
for app, s in sorted(applicant_summaries.items()):
    print(f"Applicant {app}: {s['docs_submitted']} docs submitted | Overall Outcome: {s['overall']}")
