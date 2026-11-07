"""
Dataset ingestion + demo seed script.
Run: python -m app.scripts.seed_data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import csv
from datetime import date
from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.models import Product, Lead, User
from app.core.security import get_password_hash


def parse_bool(val: str) -> bool:
    return str(val).strip().upper() in ("Y", "YES", "TRUE", "1")


def parse_int(val: str, default: int = 0) -> int:
    try:
        return int(float(str(val).strip())) if val and str(val).strip() else default
    except:
        return default


def parse_float(val: str) -> float | None:
    try:
        return float(str(val).strip()) if val and str(val).strip() else None
    except:
        return None


def parse_date(val: str) -> date | None:
    try:
        return date.fromisoformat(str(val).strip()) if val and str(val).strip() else None
    except:
        return None


DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../dataset_raw")


def seed_products(db):
    path = os.path.join(DATA_DIR, "product_catalogue.csv")
    path = os.path.abspath(path)
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing = db.query(Product).filter(Product.id == row["product_id"]).first()
            if existing:
                continue
            p = Product(
                id=row["product_id"],
                category=row["category"],
                product_name=row["product_name"],
                description=row["description"],
                unit=row["unit"],
                price_min_inr_per_month=float(row["price_min_inr_per_month"]),
                price_max_inr_per_month=float(row["price_max_inr_per_month"]),
                one_time_setup_inr=float(row["one_time_setup_inr"]),
                min_contract_months=int(row["min_contract_months"]),
                available_city_tiers=row["available_city_tiers"],
                min_employees=int(row["min_employees"]),
                min_sites=int(row["min_sites"]),
                requires_gstin=parse_bool(row["requires_gstin"]),
                requires_one_of=row["requires_one_of"] or None,
                typical_install_days=int(row["typical_install_days"]),
                target_segments=row["target_segments"],
                is_active=True,
            )
            db.add(p)
            count += 1
    db.commit()
    print(f"  Products: {count} inserted")


def seed_leads(db):
    path = os.path.join(DATA_DIR, "smb_leads.csv")
    path = os.path.abspath(path)
    count = 0
    batch = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if db.query(Lead).filter(Lead.id == row["lead_id"]).first():
                continue

            # Compute simple propensity score
            score = 0.0
            if parse_bool(row.get("has_gstin", "N")):
                score += 20
            emp = parse_int(row.get("employee_count", "1"), 1)
            if emp >= 10:
                score += 20
            elif emp >= 5:
                score += 10
            spend = parse_float(row.get("monthly_telecom_spend_inr")) or 0
            if spend >= 5000:
                score += 20
            elif spend >= 2000:
                score += 10
            stage = row.get("stage_reached", "Lead")
            stage_scores = {
                "Lead": 0, "Contacted": 5, "Needs assessed": 10,
                "Quote accepted": 25, "KYC complete": 35, "Activated": 50,
            }
            score += stage_scores.get(stage, 0)
            score = min(round(score, 1), 100.0)

            lead = Lead(
                id=row["lead_id"],
                created_date=parse_date(row.get("created_date")),
                lead_source=row.get("lead_source"),
                business_name=row.get("business_name"),
                business_type=row.get("business_type"),
                segment=row.get("segment"),
                city=row.get("city"),
                city_tier=parse_int(row.get("city_tier", "1"), 1),
                state=row.get("state"),
                preferred_language=row.get("preferred_language"),
                employee_count=parse_int(row.get("employee_count")),
                num_sites=parse_int(row.get("num_sites", "1"), 1),
                annual_turnover_band=row.get("annual_turnover_band"),
                has_gstin=parse_bool(row.get("has_gstin", "N")),
                gstin=row.get("gstin") or None,
                has_udyam=parse_bool(row.get("has_udyam", "N")),
                udyam_number=row.get("udyam_number") or None,
                current_internet=row.get("current_internet"),
                current_provider=row.get("current_provider"),
                monthly_telecom_spend_inr=parse_float(row.get("monthly_telecom_spend_inr")),
                products_of_interest=row.get("products_of_interest"),
                contact_name=row.get("contact_name"),
                contact_role=row.get("contact_role"),
                stage_reached=row.get("stage_reached"),
                outcome=row.get("outcome"),
                drop_reason=row.get("drop_reason") or None,
                contacted_date=parse_date(row.get("contacted_date")),
                needs_assessed_date=parse_date(row.get("needs_assessed_date")),
                quote_accepted_date=parse_date(row.get("quote_accepted_date")),
                kyc_complete_date=parse_date(row.get("kyc_complete_date")),
                activated_date=parse_date(row.get("activated_date")),
                days_lead_to_activation=parse_float(row.get("days_lead_to_activation")),
                customer_follow_up_calls=parse_int(row.get("customer_follow_up_calls")),
                bundle_products=row.get("bundle_products") or None,
                monthly_bundle_value_inr=parse_float(row.get("monthly_bundle_value_inr")),
                one_time_setup_inr=parse_float(row.get("one_time_setup_inr")),
                contract_months=parse_int(row.get("contract_months")),
                churned_within_6_months=parse_bool(row.get("churned_within_6_months", "N")) if row.get("churned_within_6_months") else None,
                nps_score=parse_int(row.get("nps_score")) if row.get("nps_score") else None,
                acquisition_cost_inr=parse_float(row.get("acquisition_cost_inr")),
                propensity_score=score,
                propensity_factors={
                    "has_gstin": parse_bool(row.get("has_gstin", "N")),
                    "employee_size": emp,
                    "monthly_spend": spend,
                    "stage_reached": stage,
                },
            )
            batch.append(lead)
            count += 1

            if len(batch) >= 500:
                db.add_all(batch)
                db.commit()
                batch = []

    if batch:
        db.add_all(batch)
        db.commit()
    print(f"  Leads: {count} inserted")


def seed_demo_users(db):
    users = [
        {"email": "customer@demo.udyam", "password": "Demo1234!", "full_name": "Rajesh Kumar (Demo Customer)", "role": "customer"},
        {"email": "sales@demo.udyam", "password": "Demo1234!", "full_name": "Priya Sharma (Sales Manager)", "role": "sales"},
        {"email": "admin@demo.udyam", "password": "Demo1234!", "full_name": "Arjun Mehta (Admin)", "role": "admin"},
        {"email": "partner@demo.udyam", "password": "Demo1234!", "full_name": "Kavita Nair (Channel Partner)", "role": "partner"},
    ]
    count = 0
    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            continue
        user = User(
            email=u["email"],
            hashed_password=get_password_hash(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
            is_active=True,
        )
        db.add(user)
        count += 1
    db.commit()
    print(f"  Demo users: {count} created")
    print("  Login: customer@demo.udyam / Demo1234!")
    print("         sales@demo.udyam / Demo1234!")
    print("         admin@demo.udyam / Demo1234!")


def run():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.\n")

    db = SessionLocal()
    try:
        print("Seeding products...")
        seed_products(db)
        print("Seeding leads...")
        seed_leads(db)
        print("Seeding demo users...")
        seed_demo_users(db)
        print("\n✅ Seed complete!")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
