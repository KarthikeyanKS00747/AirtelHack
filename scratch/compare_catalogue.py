import csv
import json
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

repo_root = r"C:\Users\LENOVO\GitHubRepos\AirtelHack"
csv_path = os.path.join(repo_root, "dataset_raw", "product_catalogue.csv")
db_path = os.path.join(repo_root, "backend", "udyam_digital.db")

# 1. Read CSV
with open(csv_path, encoding='utf-8') as f:
    csv_products = list(csv.DictReader(f))

print(f"Total CSV products: {len(csv_products)}")

# 2. Read SQLite DB
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM products ORDER BY id")
db_products = {r['id']: dict(r) for r in cur.fetchall()}
conn.close()

print(f"Total DB products: {len(db_products)}")

discrepancies = []
for p in csv_products:
    pid = p['product_id']
    if pid not in db_products:
        discrepancies.append(f"Missing in DB: {pid}")
        continue
    dbp = db_products[pid]
    
    # Check fields
    min_p = float(p['price_min_inr_per_month'])
    max_p = float(p['price_max_inr_per_month'])
    expected_mid = round((min_p + max_p) / 2, 2)
    setup = float(p['one_time_setup_inr'])
    req_gst = p['requires_gstin']
    min_emp = int(p['min_employees'])
    min_sites = int(p['min_sites'])
    city_tiers = p['available_city_tiers']
    deps = p['requires_one_of']
    
    # Compare with DB
    db_min = float(dbp.get('price_min_inr_per_month', 0))
    db_max = float(dbp.get('price_max_inr_per_month', 0))
    db_setup = float(dbp.get('one_time_setup_inr', 0))
    db_gst = dbp.get('requires_gstin')
    if isinstance(db_gst, bool):
        db_gst = 'Y' if db_gst else 'N'
    db_emp = int(dbp.get('min_employees', 1))
    db_sites = int(dbp.get('min_sites', 1))
    
    diffs = []
    if abs(db_min - min_p) > 0.01: diffs.append(f"min_p: db={db_min} vs csv={min_p}")
    if abs(db_max - max_p) > 0.01: diffs.append(f"max_p: db={db_max} vs csv={max_p}")
    if abs(db_setup - setup) > 0.01: diffs.append(f"setup: db={db_setup} vs csv={setup}")
    if db_gst != req_gst: diffs.append(f"requires_gstin: db={db_gst} vs csv={req_gst}")
    if db_emp != min_emp: diffs.append(f"min_emp: db={db_emp} vs csv={min_emp}")
    if db_sites != min_sites: diffs.append(f"min_sites: db={db_sites} vs csv={min_sites}")
    
    if diffs:
        discrepancies.append(f"{pid} ({p['product_name']}): " + ", ".join(diffs))

print(f"Total DB discrepancies: {len(discrepancies)}")
for d in discrepancies:
    print("  *", d)
