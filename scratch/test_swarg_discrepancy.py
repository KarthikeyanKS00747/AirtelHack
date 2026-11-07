import sys
import os
sys.path.insert(0, r"C:\Users\LENOVO\GitHubRepos\AirtelHack\backend")
sys.stdout.reconfigure(encoding='utf-8')

from app.services.recommendation_engine import RecommendationEngine, BusinessProfile

engine = RecommendationEngine()

# Test 1: Swarg with segment="prof", num_sites=1, has_gstin=False
p1 = BusinessProfile(
    segment="prof",
    city_tier=1,
    employee_count=40,
    num_sites=1,
    has_gstin=False,
    needs_broadband=True,
    needs_mobile_sims=40,
    needs_cloud_email=False,
    needs_pos=True,
    needs_cctv=20,
    needs_backup=True,
    needs_website=False,
    needs_whatsapp=False,
    budget_monthly_inr=100000
)

res1 = engine.recommend(p1)
print("=== Profile 1 (segment=prof, num_sites=1, has_gstin=False) ===")
print(f"Total Monthly: Rs. {res1.total_monthly_inr}")
print(f"Total Setup:   Rs. {res1.total_setup_inr}")
for item in res1.primary_bundle:
    print(f"  - {item.product_id}: {item.product_name} | Qty: {item.quantity} | Unit: Rs. {item.unit_price_inr} | Subtotal: Rs. {item.monthly_cost_inr} | Setup: Rs. {item.setup_cost_inr}")

# Test 2: Swarg with segment="multi", num_sites=2, has_gstin=False
p2 = BusinessProfile(
    segment="multi",
    city_tier=1,
    employee_count=40,
    num_sites=2,
    has_gstin=False,
    needs_broadband=True,
    needs_mobile_sims=40,
    needs_cloud_email=False,
    needs_pos=True,
    needs_cctv=20,
    needs_backup=True,
    needs_website=False,
    needs_whatsapp=False,
    budget_monthly_inr=100000
)

res2 = engine.recommend(p2)
print("\n=== Profile 2 (segment=multi, num_sites=2, has_gstin=False) ===")
print(f"Total Monthly: Rs. {res2.total_monthly_inr}")
print(f"Total Setup:   Rs. {res2.total_setup_inr}")
for item in res2.primary_bundle:
    print(f"  - {item.product_id}: {item.product_name} | Qty: {item.quantity} | Unit: Rs. {item.unit_price_inr} | Subtotal: Rs. {item.monthly_cost_inr} | Setup: Rs. {item.setup_cost_inr}")

# Test 3: Swarg with has_gstin=True
p3 = BusinessProfile(
    segment="multi",
    city_tier=1,
    employee_count=40,
    num_sites=2,
    has_gstin=True,
    needs_broadband=True,
    needs_mobile_sims=40,
    needs_cloud_email=False,
    needs_pos=True,
    needs_cctv=20,
    needs_backup=True,
    needs_website=False,
    needs_whatsapp=False,
    budget_monthly_inr=100000
)

res3 = engine.recommend(p3)
print("\n=== Profile 3 (segment=multi, num_sites=2, has_gstin=True) ===")
print(f"Total Monthly: Rs. {res3.total_monthly_inr}")
print(f"Total Setup:   Rs. {res3.total_setup_inr}")
for item in res3.primary_bundle:
    print(f"  - {item.product_id}: {item.product_name} | Qty: {item.quantity} | Unit: Rs. {item.unit_price_inr} | Subtotal: Rs. {item.monthly_cost_inr} | Setup: Rs. {item.setup_cost_inr}")
