import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

kyc_dir = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\kyc_documents"

# Let's inspect raw binary strings in PNGs to see if plain text is readable (e.g. text chunks or metadata)
for fname in sorted(os.listdir(kyc_dir))[:8]:
    fpath = os.path.join(kyc_dir, fname)
    with open(fpath, "rb") as f:
        data = f.read()
    # Find any printable ASCII sequences > 6 chars
    import re
    strings = re.findall(b"[A-Za-z0-9_ -]{6,}", data)
    print(f"=== {fname} ({len(data)} bytes) ===")
    clean_strs = [s.decode('latin1') for s in strings if not s.startswith(b"IHDR") and not s.startswith(b"IDAT")]
    if clean_strs:
        print("  Found strings:", clean_strs[:10])
    else:
        print("  No plaintext chunks found (standard compressed raster)")
