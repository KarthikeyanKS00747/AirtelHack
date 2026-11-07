import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

gstin_path = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\mock_gstin_registry.csv"
udyam_path = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\mock_udyam_registry.csv"

# Check K03
with open(gstin_path, encoding='utf-8') as f:
    gstins = {r['gstin']: r for r in csv.DictReader(f)}

with open(udyam_path, encoding='utf-8') as f:
    udyams = {r['udyam_number']: r for r in csv.DictReader(f)}

print("K03 GSTIN: 27XUIXG0767D1ZP ->", gstins.get("27XUIXG0767D1ZP"))

# Search Udyam for Ganesh Woodcraft
print("\nSearching Udyam for 'Ganesh Woodcraft':")
for u, r in udyams.items():
    if "Ganesh" in r.get("enterprise_name", ""):
        print(f"  {u} -> {r}")

# Check all applicants K01-K12 to see which ones are in BOTH GST and Udyam!
print("\n--- Checking all applicants K01 to K12 in Udyam registry by name ---")
app_names = {
    "K01": "Vindhya Tours",
    "K02": "Harmony Dental",
    "K03": "Ganesh Woodcraft",
    "K04": "Saffron Dental",
    "K05": "Balaji Realty",
    "K06": "Saffron",
    "K07": "Neelgiri Physio",
    "K08": "Green Leaf Legal",
    "K09": "Kaveri Insurance",
    "K10": "Kaveri Stays",
    "K11": "Trinity Bake",
    "K12": "Star Electronics",
}

for k, name in app_names.items():
    matches = [f"{u}: {r['enterprise_name']} ({r['city']})" for u, r in udyams.items() if name.lower() in r.get('enterprise_name', '').lower()]
    print(f"{k} ({name}): {len(matches)} match(es) -> {matches[:2]}")
