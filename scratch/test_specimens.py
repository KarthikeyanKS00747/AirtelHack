import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

repo_root = r"C:\Users\LENOVO\GitHubRepos\AirtelHack"
kyc_dir = os.path.join(repo_root, "dataset_raw", "kyc_documents")

print(f"Checking KYC specimens in: {kyc_dir}")
files = sorted(os.listdir(kyc_dir))
print(f"Total specimen files: {len(files)}")

# Group by applicant
applicants = {}
for f in files:
    if f.endswith(".png"):
        app_id = f.split("_")[0]
        applicants.setdefault(app_id, []).append(f)

print(f"Total applicants found: {len(applicants)}")
for app_id, doc_list in sorted(applicants.items()):
    types = [d.replace(f"{app_id}_", "").replace(".png", "") for d in doc_list]
    print(f"  {app_id}: {len(doc_list)} documents -> {', '.join(types)}")

# Check tesseract availability
try:
    import pytesseract
    from PIL import Image
    # Try finding tesseract
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        "tesseract"
    ]
    tess_path = None
    for p in possible_paths:
        if os.path.exists(p):
            tess_path = p
            break
    print(f"Tesseract binary found: {tess_path}")
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
        # Test on K01_gst_certificate.png
        sample = os.path.join(kyc_dir, "K01_gst_certificate.png")
        txt = pytesseract.image_to_string(Image.open(sample))
        print("K01 GST OCR Sample (first 120 chars):", repr(txt[:120]))
except Exception as e:
    print("OCR note:", e)
