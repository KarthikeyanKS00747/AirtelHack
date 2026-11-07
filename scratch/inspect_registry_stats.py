import os
import csv
import sys
from datetime import date, datetime

sys.stdout.reconfigure(encoding='utf-8')

repo_root = r"C:\Users\LENOVO\GitHubRepos\AirtelHack"
gstin_path = os.path.join(repo_root, "dataset_raw", "mock_gstin_registry.csv")
udyam_path = os.path.join(repo_root, "dataset_raw", "mock_udyam_registry.csv")

with open(gstin_path, encoding='utf-8') as f:
    gstins = {r['gstin']: r for r in csv.DictReader(f)}

with open(udyam_path, encoding='utf-8') as f:
    udyams = {r['udyam_number']: r for r in csv.DictReader(f)}

print(f"Total GSTIN records: {len(gstins)}")
print(f"Total Udyam records: {len(udyams)}")

# Let's check status counts in GST registry
status_counts = {}
for r in gstins.values():
    s = r.get('status', 'Unknown')
    status_counts[s] = status_counts.get(s, 0) + 1
print("GST Statuses:", status_counts)
