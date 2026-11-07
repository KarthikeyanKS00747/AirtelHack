"""All SQLAlchemy models for Udyam Digital."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    Text, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def new_uuid():
    return str(uuid.uuid4())


# ── Users & Roles ──────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(30), default="customer", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business_profiles = relationship("BusinessProfile", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    orders = relationship("Order", back_populates="user")
    audit_events = relationship("AuditEvent", back_populates="user")
    consent_records = relationship("ConsentRecord", back_populates="user")


# ── Business Profiles ──────────────────────────────────────────────────────

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True, index=True)  # for anonymous sessions

    # Business info
    business_name = Column(String(255))
    business_type = Column(String(100))
    segment = Column(String(30), nullable=True)
    city = Column(String(100))
    city_tier = Column(Integer, default=1)
    state = Column(String(100))

    # Size
    employee_count = Column(Integer, default=1)
    num_sites = Column(Integer, default=1)
    annual_turnover_band = Column(String(50))

    # Registration
    has_gstin = Column(Boolean, default=False)
    gstin = Column(String(15), nullable=True)
    has_udyam = Column(Boolean, default=False)
    udyam_number = Column(String(20), nullable=True)

    # Current setup
    current_internet = Column(String(100))
    current_provider = Column(String(100))
    monthly_telecom_spend_inr = Column(Float, default=0)

    # Requirements captured by advisor
    needs_broadband = Column(Boolean, default=True)
    needs_mobile_sims = Column(Integer, default=0)
    needs_cloud_email = Column(Boolean, default=False)
    needs_pos = Column(Boolean, default=False)
    needs_cctv = Column(Integer, default=0)
    needs_backup = Column(Boolean, default=False)
    needs_website = Column(Boolean, default=False)
    needs_whatsapp = Column(Boolean, default=False)
    needs_toll_free = Column(Boolean, default=False)
    needs_sms = Column(Boolean, default=False)
    needs_firewall = Column(Boolean, default=False)
    needs_fleet_tracking = Column(Integer, default=0)

    budget_monthly_inr = Column(Float, nullable=True)
    preferred_contract_months = Column(Integer, nullable=True)

    # Raw profile JSON from advisor
    raw_profile = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="business_profiles")
    conversations = relationship("Conversation", back_populates="business_profile")
    recommendations = relationship("Recommendation", back_populates="business_profile")
    quotes = relationship("Quote", back_populates="business_profile")


# ── Products ───────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"
    id = Column(String(10), primary_key=True)  # P01, P02, etc.
    category = Column(String(50), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    unit = Column(String(50), default="per site")
    price_min_inr_per_month = Column(Float, nullable=False)
    price_max_inr_per_month = Column(Float, nullable=False)
    one_time_setup_inr = Column(Float, default=0)
    min_contract_months = Column(Integer, default=12)
    available_city_tiers = Column(String(10), default="1;2")  # "1", "2", "1;2"
    min_employees = Column(Integer, default=1)
    min_sites = Column(Integer, default=1)
    requires_gstin = Column(Boolean, default=False)
    requires_one_of = Column(String(100), nullable=True)  # "P01|P02|P03"
    typical_install_days = Column(Integer, default=5)
    target_segments = Column(String(50), default="micro;prof;multi;mfg")
    is_active = Column(Boolean, default=True)

    # Relationships
    bundle_items = relationship("BundleItem", back_populates="product")


# ── Conversations ──────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    persona = Column(String(50), nullable=True)  # kirana, clinic, multi_retail
    status = Column(String(30), default="active")
    messages = Column(JSON, default=list)  # [{role, content, timestamp}]
    extracted_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    business_profile = relationship("BusinessProfile", back_populates="conversations")


# ── Recommendations ────────────────────────────────────────────────────────

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String(36), primary_key=True, default=new_uuid)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    primary_bundle = Column(JSON)      # [{product_id, qty, reason, monthly_cost, setup_cost}]
    alternative_bundles = Column(JSON, default=list)
    total_monthly_inr = Column(Float)
    total_setup_inr = Column(Float)
    explanation = Column(Text)
    score = Column(Float, default=0)
    eligibility_checks = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="recommendations")
    quotes = relationship("Quote", back_populates="recommendation")


# ── Bundles & Quotes ───────────────────────────────────────────────────────

class Bundle(Base):
    __tablename__ = "bundles"
    id = Column(String(36), primary_key=True, default=new_uuid)
    name = Column(String(255))
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=True)
    total_monthly_inr = Column(Float, default=0)
    total_setup_inr = Column(Float, default=0)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("BundleItem", back_populates="bundle", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="bundle")


class BundleItem(Base):
    __tablename__ = "bundle_items"
    id = Column(String(36), primary_key=True, default=new_uuid)
    bundle_id = Column(String(36), ForeignKey("bundles.id"), nullable=False)
    product_id = Column(String(10), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price_inr = Column(Float)   # locked at time of bundle creation
    monthly_cost_inr = Column(Float)
    setup_cost_inr = Column(Float)
    is_mandatory = Column(Boolean, default=True)
    reason = Column(Text)

    bundle = relationship("Bundle", back_populates="items")
    product = relationship("Product", back_populates="bundle_items")


class Quote(Base):
    __tablename__ = "quotes"
    id = Column(String(36), primary_key=True, default=new_uuid)
    quote_number = Column(String(20), unique=True, nullable=False)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    bundle_id = Column(String(36), ForeignKey("bundles.id"), nullable=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Customer details
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(20))
    billing_address = Column(Text)
    gstin_for_invoice = Column(String(15), nullable=True)

    # Pricing (server-calculated, immutable)
    line_items = Column(JSON)          # [{product_id, name, qty, monthly, setup}]
    total_monthly_inr = Column(Float)
    total_setup_inr = Column(Float)
    contract_months = Column(Integer, default=12)
    discount_pct = Column(Float, default=0)
    tax_pct = Column(Float, default=18)  # GST
    total_with_tax_inr = Column(Float)

    status = Column(String(30), default="draft")
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business_profile = relationship("BusinessProfile", back_populates="quotes")
    bundle = relationship("Bundle", back_populates="quotes")
    recommendation = relationship("Recommendation", back_populates="quotes")
    orders = relationship("Order", back_populates="quote")


# ── Orders & Tracking ──────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"
    id = Column(String(36), primary_key=True, default=new_uuid)
    order_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    quote_id = Column(String(36), ForeignKey("quotes.id"), nullable=False)
    business_profile_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=True)

    status = Column(String(30), default="placed")

    total_monthly_inr = Column(Float)
    total_setup_inr = Column(Float)
    contract_months = Column(Integer)
    payment_ref = Column(String(100), nullable=True)  # simulated
    payment_status = Column(String(30), default="pending")

    expected_activation_date = Column(Date, nullable=True)
    activated_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    quote = relationship("Quote", back_populates="orders")
    milestones = relationship("OrderMilestone", back_populates="order", order_by="OrderMilestone.occurred_at")
    kyc_submissions = relationship("KYCSubmission", back_populates="order")


class OrderMilestone(Base):
    __tablename__ = "order_milestones"
    id = Column(String(36), primary_key=True, default=new_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    stage = Column(String(50), nullable=False)
    label = Column(String(255))
    description = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    agent = Column(String(100), nullable=True)  # system, customer, sales-rep name

    order = relationship("Order", back_populates="milestones")


# ── KYC ───────────────────────────────────────────────────────────────────

class KYCSubmission(Base):
    __tablename__ = "kyc_submissions"
    id = Column(String(36), primary_key=True, default=new_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    consent_record_id = Column(String(36), ForeignKey("consent_records.id"), nullable=True)

    status = Column(String(30), default="pending")
    overall_result = Column(String(30), nullable=True)

    # Cross-document checks
    cross_check_results = Column(JSON, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(36), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="kyc_submissions")
    documents = relationship("KYCDocument", back_populates="submission")
    consent_record = relationship("ConsentRecord")


class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    id = Column(String(36), primary_key=True, default=new_uuid)
    submission_id = Column(String(36), ForeignKey("kyc_submissions.id"), nullable=False)
    doc_type = Column(String(30), nullable=False)

    # File info
    original_filename = Column(String(255))
    stored_filename = Column(String(255))    # UUID-based, no PII
    file_size_bytes = Column(Integer)
    mime_type = Column(String(50))

    # OCR results
    ocr_text = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=True)  # {gstin, legal_name, date, etc}

    # Verification
    ocr_status = Column(String(30), default="pending")
    registry_lookup_status = Column(String(30), default="not_applicable")
    registry_result = Column(JSON, nullable=True)
    verification_status = Column(String(30), default="pending")
    verification_notes = Column(Text, nullable=True)
    expiry_check_passed = Column(Boolean, nullable=True)

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    submission = relationship("KYCSubmission", back_populates="documents")


# ── Consent ───────────────────────────────────────────────────────────────

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    purpose = Column(String(100), nullable=False)  # "kyc_processing", "marketing"
    consent_text_version = Column(String(20), default="1.0")
    consented = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)   # masked in logs
    user_agent = Column(String(255), nullable=True)
    consented_at = Column(DateTime, default=datetime.utcnow)
    withdrawn_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consent_records")


# ── Leads (from dataset) ──────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String(10), primary_key=True)   # L00001 etc.
    created_date = Column(Date)
    lead_source = Column(String(50))
    business_name = Column(String(255))
    business_type = Column(String(100))
    segment = Column(String(30))
    city = Column(String(100))
    city_tier = Column(Integer)
    state = Column(String(100))
    preferred_language = Column(String(50))
    employee_count = Column(Integer)
    num_sites = Column(Integer)
    annual_turnover_band = Column(String(50))
    has_gstin = Column(Boolean, default=False)
    gstin = Column(String(15), nullable=True)
    has_udyam = Column(Boolean, default=False)
    udyam_number = Column(String(20), nullable=True)
    current_internet = Column(String(100))
    current_provider = Column(String(100))
    monthly_telecom_spend_inr = Column(Float, nullable=True)
    products_of_interest = Column(String(255))
    contact_name = Column(String(255))
    contact_role = Column(String(100))
    stage_reached = Column(String(30))
    outcome = Column(String(20))
    drop_reason = Column(String(100), nullable=True)
    contacted_date = Column(Date, nullable=True)
    needs_assessed_date = Column(Date, nullable=True)
    quote_accepted_date = Column(Date, nullable=True)
    kyc_complete_date = Column(Date, nullable=True)
    activated_date = Column(Date, nullable=True)
    days_lead_to_activation = Column(Float, nullable=True)
    customer_follow_up_calls = Column(Integer, nullable=True)
    bundle_products = Column(String(255), nullable=True)
    monthly_bundle_value_inr = Column(Float, nullable=True)
    one_time_setup_inr = Column(Float, nullable=True)
    contract_months = Column(Integer, nullable=True)
    churned_within_6_months = Column(Boolean, nullable=True)
    nps_score = Column(Integer, nullable=True)
    acquisition_cost_inr = Column(Float, nullable=True)

    # Back-office
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    partner_id = Column(String(36), nullable=True)
    propensity_score = Column(Float, nullable=True)
    propensity_factors = Column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_leads_segment", "segment"),
        Index("ix_leads_outcome", "outcome"),
        Index("ix_leads_stage", "stage_reached"),
        Index("ix_leads_source", "lead_source"),
    )


# ── Audit Events ──────────────────────────────────────────────────────────

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_events")
