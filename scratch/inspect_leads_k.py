import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

leads_path = r"C:\Users\LENOVO\GitHubRepos\AirtelHack\dataset_raw\smb_leads.csv"

with open(leads_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total leads: {len(rows)}")

# Let's see if any lead_id starts with K or matches K01-K12
k_leads = [r for r in rows if 'K0' in r.get('lead_id', '') or 'K1' in r.get('lead_id', '')]
print(f"Leads with K in ID: {len(k_leads)}")

# Let's inspect first 12 leads in smb_leads
for i, r in enumerate(rows[:12]):
    print(f"Lead {r['lead_id']}: {r['business_name']} | GSTIN: {r['gstin']} | Udyam: {r['udyam_number']} | Stage: {r['stage_reached']} | Outcome: {r['outcome']} | Drop: {r['drop_reason']}")
