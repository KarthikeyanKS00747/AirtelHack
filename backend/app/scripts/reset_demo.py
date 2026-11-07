"""
Reset Demo script for Project Udyam Digital.
Resets the database to a clean demo state in seconds.
Usage:
    python -m app.scripts.reset_demo
"""
import sys
import os
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.core.database import SessionLocal, engine, Base
from app.models import (
    User, Product, Lead, BusinessProfile, Conversation,
    Recommendation, Bundle, BundleItem, Quote, Order,
    OrderMilestone, KYCSubmission, KYCDocument, ConsentRecord, AuditEvent
)
from app.scripts.seed_data import seed_products, seed_leads, seed_demo_users


def reset_demo():
    print("=" * 60)
    print("[RESET] RESETTING UDYAM DIGITAL DEMO STATE")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Clean dynamic transactional records
        print("Clearing transactional tables...")
        db.query(KYCDocument).delete()
        db.query(KYCSubmission).delete()
        db.query(OrderMilestone).delete()
        db.query(Order).delete()
        db.query(Quote).delete()
        db.query(BundleItem).delete()
        db.query(Bundle).delete()
        db.query(Recommendation).delete()
        db.query(Conversation).delete()
        db.query(ConsentRecord).delete()
        db.query(AuditEvent).delete()
        db.query(BusinessProfile).delete()
        db.commit()
        print("  [+] Cleared dynamic transactions and test sessions.")

        # 2. Check and ensure products exist
        prod_count = db.query(Product).count()
        if prod_count < 25:
            print(f"Products count is {prod_count}/25. Re-seeding products...")
            seed_products(db)
        else:
            print(f"  [+] Product catalogue intact ({prod_count} products).")

        # 3. Check and ensure leads exist
        leads_count = db.query(Lead).count()
        if leads_count < 5000:
            print(f"Leads count is {leads_count}/5000. Re-seeding leads...")
            seed_leads(db)
        else:
            print(f"  [+] Historical leads dataset intact ({leads_count} leads).")

        # 4. Check and ensure demo users exist
        user_count = db.query(User).count()
        if user_count < 4:
            print(f"Users count is {user_count}/4. Re-seeding demo users...")
            seed_demo_users(db)
        else:
            print(f"  [+] Demo accounts ready ({user_count} accounts).")

        # 5. Create 3 standard demo personas in business_profiles for instant demo
        demo_customer = db.query(User).filter(User.email == "customer@demo.udyam").first()
        customer_id = demo_customer.id if demo_customer else None

        p1 = BusinessProfile(
            user_id=customer_id,
            session_id="demo-kirana-session",
            business_name="Gupta General Store",
            business_type="Kirana / Grocery",
            segment="micro",
            city="Jaipur",
            city_tier=2,
            state="Rajasthan",
            employee_count=2,
            num_sites=1,
            has_gstin=False,
            current_internet="Mobile Hotspot",
            current_provider="Airtel",
            monthly_telecom_spend_inr=600,
            needs_broadband=True,
            needs_mobile_sims=1,
            needs_pos=True,
            budget_monthly_inr=1500,
        )

        p2 = BusinessProfile(
            user_id=customer_id,
            session_id="demo-clinic-session",
            business_name="Apex Healthcare Clinic",
            business_type="Medical Clinic",
            segment="prof",
            city="Pune",
            city_tier=1,
            state="Maharashtra",
            employee_count=8,
            num_sites=1,
            has_gstin=True,
            gstin="27AABCA1234F1Z5",
            has_udyam=True,
            udyam_number="UDYAM-MH-00-1234567",
            current_internet="Consumer Broadband",
            current_provider="Local ISP",
            monthly_telecom_spend_inr=2200,
            needs_broadband=True,
            needs_mobile_sims=4,
            needs_cloud_email=True,
            needs_cctv=2,
            needs_backup=True,
            budget_monthly_inr=4500,
        )

        p3 = BusinessProfile(
            user_id=customer_id,
            session_id="demo-multi-retail-session",
            business_name="Modern Footwear & Apparel",
            business_type="Retail Chain",
            segment="multi",
            city="Bengaluru",
            city_tier=1,
            state="Karnataka",
            employee_count=28,
            num_sites=4,
            has_gstin=True,
            gstin="29ABCDE1234F1Z5",
            has_udyam=True,
            udyam_number="UDYAM-KR-00-9876543",
            current_internet="Mixed Broadband",
            current_provider="Multiple",
            monthly_telecom_spend_inr=12000,
            needs_broadband=True,
            needs_mobile_sims=12,
            needs_cloud_email=True,
            needs_cctv=8,
            needs_pos=True,
            needs_firewall=True,
            budget_monthly_inr=15000,
        )

        db.add_all([p1, p2, p3])
        db.commit()
        print("  [+] Created 3 pre-seeded Demo Personas (Kirana, Clinic, Multi-Site Retail).")

        print("=" * 60)
        print("[SUCCESS] DEMO RESET SUCCESSFUL! System is 100% ready for presentation.")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Reset failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo()
