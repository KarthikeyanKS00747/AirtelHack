import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

gstin_path = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\mock_gstin_registry.csv"
udyam_path = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\mock_udyam_registry.csv"

with open(gstin_path, encoding='utf-8') as f:
    gstins = {r['gstin']: r for r in csv.DictReader(f)}

print("37IHKXV5167L1ZS in GST registry?", "37IHKXV5167L1ZS" in gstins)
if "37IHKXV5167L1ZS" in gstins:
    print("Record:", gstins["37IHKXV5167L1ZS"])

# Search by trade name "Vindhya Tours & Travels"
for g, r in gstins.items():
    if "Vindhya" in r.get("trade_name", "") or "Vindhya" in r.get("legal_name", ""):
        print(f"Match by name in GST: {g} -> {r}")

with open(udyam_path, encoding='utf-8') as f:
    udyams = {r['udyam_number']: r for r in csv.DictReader(f)}

for u, r in udyams.items():
    if "Vindhya" in r.get("enterprise_name", ""):
        print(f"Match by name in Udyam: {u} -> {r}")
