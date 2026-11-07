# Project Udyam Digital — Accel Business
### Making Small Businesses Go Digital in One Sitting
**Airtel SYNC Hackathon 2026 — Track A (MSME Digital Onboarding Platform)**

---

## 1. Executive Summary

India has over 6.3 crore MSMEs, yet acquiring and activating them with enterprise-grade connectivity currently takes **17.6 days on average**, involves **3–4 follow-up calls**, costs **₹15,000 per activated business**, and suffers from an abysmal **7.36% lead-to-activation conversion rate** (only 368 activated out of 5,000 leads).

**Project Udyam Digital** transforms this fragmented journey into an intelligent, end-to-end digital acquisition platform:
- **Conversational AI Advisor**: Contextual, adaptive dialogue that extracts business requirements without tedious forms.
- **Deterministic Recommendation Engine**: Grounded 100% in the real 25-product catalogue—never invents products, specs, or pricing.
- **Intelligent Bundle Builder**: Transparent pricing, dynamic add-on selection, and real-time dependency/eligibility enforcement.
- **Smart KYC & Verification**: In-browser document OCR, dual mock registry lookup (GSTIN and Udyam), cross-document name/PAN validation, and 90-day address proof expiration verification.
- **Real-Time Order Stepper**: Transparent 7-stage lifecycle tracking from order submission to SIM & fiber activation.
- **Back-Office Partner Intelligence**: Explainable Lead Propensity Scoring (0–100) augmenting channel partners and field sales agents.

---

## 2. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Next.js 14 / TypeScript Frontend                     │
│  - Landing Page (Airtel Enterprise Visual Identity)                    │
│  - AI Advisor (Adaptive persona dialogue)                              │
│  - Bundle Builder (Dynamic pricing & dependency validation)            │
│  - Transparent Checkout (DPDP consent & itemized quote)                │
│  - Smart KYC (OCR extraction & dual registry cross-check)             │
│  - Order Tracker (7-stage milestone timeline)                          │
│  - Back-Office Dashboard (Funnel analytics, Propensity scoring)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API (JSON / Multipart)
┌───────────────────────────────────▼────────────────────────────────────┐
│                   Python FastAPI Modular Monolith Backend              │
│  - /api/advisor         : Contextual dialogue & persona handlers       │
│  - /api/recommendations : Deterministic rule-based bundling engine     │
│  - /api/products        : 25-product catalogue service                 │
│  - /api/quotes          : Server-side pricing & GST calculation        │
│  - /api/orders          : Order lifecycle & milestone management       │
│  - /api/kyc             : Pytesseract OCR & registry verification      │
│  - /api/leads           : 5,000 lead analytics & propensity scoring    │
│  - /api/analytics       : Historical funnel, churn & NPS metrics       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQLAlchemy ORM
┌───────────────────────────────────▼────────────────────────────────────┐
│             SQLite / PostgreSQL Database (15 Relational Tables)        │
│  - users, products, business_profiles, conversations, recommendations  │
│  - bundles, bundle_items, quotes, orders, order_milestones             │
│  - kyc_submissions, kyc_documents, consent_records, leads, audit_events│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Quickstart & Installation Guide

### Prerequisites
- Python 3.11+ (Python 3.12 / 3.13 supported)
- Node.js 18+ (Node.js 20 recommended) & npm
- Git

### Step 1: Clone & Configure Backend
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure environment variables are set
copy .env.example .env   # (or cp on Linux/macOS)
```

### Step 2: Seed the Database
The project comes pre-configured with SQLite (`udyam_digital.db`) and seeds all 5,000 historical leads, 25 catalogue products, and 4 demo user roles:
```bash
# Seed initial dataset
python -m app.scripts.seed_data

# Or reset demo state at any time in under 5 seconds
python -m app.scripts.reset_demo
```

### Step 3: Start the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- Interactive Swagger Docs: `http://localhost:8000/api/docs`
- ReDoc API Spec: `http://localhost:8000/api/redoc`

### Step 4: Start the Frontend Application
```bash
cd ../frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 4. Demo Accounts & Seed Credentials

The demo seed script provides pre-configured role-based credentials:

| Role | Email | Password | Access Area |
|---|---|---|---|
| **Demo Customer** | `customer@demo.udyam` | `Demo1234!` | Storefront, AI Advisor, KYC, Order Tracker |
| **Sales Manager** | `sales@demo.udyam` | `Demo1234!` | Back-Office Lead Pipeline & Interventions |
| **Channel Partner** | `partner@demo.udyam` | `Demo1234!` | Partner Lead Dashboard & Attribution |
| **Platform Admin** | `admin@demo.udyam` | `Demo1234!` | Full System Analytics & Audit Logs |

---

## 5. Verification & Automated Test Suite

Project Udyam Digital includes a full automated test suite covering recommendation logic, catalogue dependencies, server-side pricing math, and KYC document validation.

```bash
cd backend
pytest -v
```

**Test Results:**
- `tests/test_recommendation_engine.py`: 6 passed (All 4 segments, dependencies, tier restrictions, GSTIN rules)
- `tests/test_kyc_verification.py`: 5 passed (GSTIN checksum, Udyam lookup, address proof age <= 90 days, missing doc handling)
- `tests/test_pricing_and_quotes.py`: 2 passed (Deterministic price midpointing, 18% GST calculation)
- `tests/test_api_endpoints.py`: 8 passed (Health, products, personas, recommendations, leads funnel, analytics)
- **Total: 21 Passed, 0 Failed (100% Pass Rate)**

---

## 6. Complete Documentation Pack

Explore the formal hackathon submission deliverables in `/docs`:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture & sequence diagrams
- [docs/DATABASE_AND_API.md](docs/DATABASE_AND_API.md) — Complete 15-table DB schema & 18 API route specifications
- [docs/DATA_ANALYSIS_REPORT.md](docs/DATA_ANALYSIS_REPORT.md) — 5,000-lead statistical analysis, funnel drop-offs, and propensity model
- [docs/BUSINESS_CASE.md](docs/BUSINESS_CASE.md) — 10-slide commercial strategy & GTM business case
- [docs/PRIVACY_AND_SECURITY.md](docs/PRIVACY_AND_SECURITY.md) — DPDP Act 2023 compliance & security architecture note
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) — 3-minute judging demonstration script across 3 personas
- [docs/TEST_REPORT.md](docs/TEST_REPORT.md) — Automated test suite report and journey verification
