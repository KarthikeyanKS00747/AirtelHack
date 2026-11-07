import sys
sys.path.insert(0, r"C:\Users\LENOVO\GitHubRepos\AirtelHack\backend")

from app.services.kyc_service import (
    run_ocr, extract_fields_by_type, verify_document,
    cross_check_documents, determine_overall_result
)

docs = []
for dtype, fname in [
    ("address_proof", "K03_address_proof.png"),
    ("gst_certificate", "K03_gst_certificate.png"),
    ("signatory_id", "K03_signatory_id.png"),
    ("udyam_certificate", "K03_udyam_certificate.png"),
]:
    txt, status = run_ocr("dummy", fname)
    fields = extract_fields_by_type(dtype, txt)
    vstat, vnotes, reg = verify_document(dtype, fields, status)
    docs.append({
        "doc_type": dtype,
        "extracted_fields": fields,
        "verification_status": vstat
    })
    print(f"{dtype}: {vstat} | fields: {fields}")

cross = cross_check_documents(docs)
print("\nCross check results:", cross)
doc_statuses = [d["verification_status"] for d in docs]
print("Doc statuses:", doc_statuses)
print("Overall result:", determine_overall_result(cross, doc_statuses))
