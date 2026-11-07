# System Architecture & Technical Design — Project Udyam Digital
**Accel Business | Airtel SYNC Hackathon 2026**

---

## 1. System Overview

Project Udyam Digital is structured as a **clean, modular monolithic architecture** combining a Next.js 14 frontend and a Python FastAPI backend. The modular monolith pattern was intentionally selected over microservices to eliminate unnecessary network latency, maintain transactional consistency across quotes, orders, and KYC records, and ensure rapid, dependable execution for MSME onboarding.

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Presentation (Next.js 14 / TypeScript)"]
        UI_Home["Landing Page (Airtel Theme)"]
        UI_Advisor["Module A: AI Business Advisor"]
        UI_Bundle["Module B: Intelligent Bundle Builder"]
        UI_Checkout["Module C: Quote & Checkout"]
        UI_KYC["Module D: Smart Digital KYC"]
        UI_Track["Module E: 7-Stage Order Tracker"]
        UI_Dash["Module F: Back-Office & Partner Dashboard"]
    end

    subgraph APILayer["FastAPI Application Services (Python)"]
        API_Auth["Auth & RBAC Service (JWT)"]
        API_Advisor["Contextual Advisor & Persona Handler"]
        API_Recom["Deterministic Recommendation Engine"]
        API_Quote["Server-Side Pricing & GST Service"]
        API_Order["Order Lifecycle & Milestone Manager"]
        API_KYC["Document OCR & Dual Registry Verifier"]
        API_Analytics["Lead Funnel & Propensity Service"]
    end

    subgraph DataIntegrations["Data & Registry Layer"]
        DB[(Relational DB: SQLite / PostgreSQL)]
        Storage[Local File Storage: uploads/kyc/]
        GST_Reg[Mock GSTIN Registry - 3,534 Records]
        Udyam_Reg[Mock Udyam Registry - 2,723 Records]
        OCR_Engine[Tesseract OCR Engine / Fallback]
    end

    UI_Advisor --> API_Advisor
    UI_Bundle --> API_Recom
    UI_Checkout --> API_Quote
    UI_KYC --> API_KYC
    UI_Track --> API_Order
    UI_Dash --> API_Analytics

    API_Advisor --> DB
    API_Recom --> DB
    API_Quote --> DB
    API_Order --> DB
    API_KYC --> DB
    API_KYC --> Storage
    API_KYC --> GST_Reg
    API_KYC --> Udyam_Reg
    API_KYC --> OCR_Engine
    API_Analytics --> DB
```

---

## 2. End-to-End Customer Journey Sequence

The onboarding journey seamlessly guides the business owner from requirement discovery to active service:

```mermaid
sequenceDiagram
    autonumber
    actor Customer as MSME Owner
    participant Advisor as Module A: AI Advisor
    participant Engine as Module B: Recommender
    participant Checkout as Module C: Quote & Order
    participant KYC as Module D: Smart KYC
    participant Registry as Dual Registries
    participant Tracker as Module E: Order Tracker
    participant Dashboard as Module F: Back-Office

    Customer->>Advisor: Starts session (Persona / Adaptive questions)
    Advisor-->>Customer: Clarifying questions (Sites, Employees, POS, CCTV)
    Customer->>Advisor: Submits operational requirements
    Advisor->>Engine: Evaluates Business Profile against Catalogue
    Engine-->>Customer: Deterministic primary & alternative bundles
    Customer->>Engine: Customizes quantities & add-ons
    Customer->>Checkout: Initiates purchase & reviews line items
    Checkout-->>Customer: Itemized quote (Setup fees + Monthly + 18% GST)
    Customer->>Checkout: Consents to DPDP terms & confirms order
    Checkout->>Tracker: Generates Order & Initial Milestone ("Order Placed")
    Customer->>KYC: Uploads GST, Udyam, ID, and Address Proof
    KYC->>Registry: Cross-checks GSTIN (char 4 = 'X') & Udyam (dist = '00')
    Registry-->>KYC: Match status & active registration confirmation
    KYC->>KYC: Validates address proof recency (<= 90 days from 2026-07-15)
    KYC->>Tracker: Updates Milestone ("KYC Verified")
    Tracker-->>Customer: Real-time status update & SLA countdown
    Tracker->>Dashboard: Notifies Sales Rep & Partner of new active pipeline
```

---

## 3. Component Boundaries & Responsibilities

### Module A: AI Business Advisor
- **Goal:** Replace manual sales discovery calls with intelligent, low-friction conversational profiling.
- **Design Pattern:** Hybrid state-machine and LLM intent extraction.
- **Fallback:** Deterministic heuristic dialog trees for Kirana, Clinic, and Multi-Site personas ensuring 100% uptime even without external LLM API availability.

### Module B: Intelligent Bundle Builder
- **Goal:** Transparent, flexible bundling grounded in the actual 25-product catalogue.
- **Core Rules:**
  - Connectivity dependency checks (e.g., Static IP `P11` requires Broadband `P01`/`P02`/`P03`).
  - City Tier filtering (`P03` Biz Fibre 1G restricted to Tier 1).
  - Minimum site validation (`P10` SD-WAN requires $\ge 3$ sites).
  - GSTIN requirement enforcement (`P12`, `P13`, `P14`, `P15`, `P21` locked without GSTIN).

### Module C: Quote & Checkout
- **Goal:** Zero hidden charges and compliant contracting.
- **Security:** Immutable server-side price recalculation (client-submitted prices are ignored).
- **Taxation:** Itemized 18% GST calculation applied consistently.

### Module D: Smart KYC
- **Goal:** Cut KYC drop-off from 32% to <10% with instant digital document verification.
- **Integrations:**
  - OCR extraction of GSTIN, Udyam registration, Signatory Name, and Document Issue Date.
  - Mock GSTIN registry lookup (validating the synthetic `X` PAN flag).
  - Mock Udyam registry lookup (validating district code `00`).
  - Address proof recency validation against the hackathon reference date (`2026-07-15`).

### Module E: Order Tracker
- **Goal:** Eliminate customer status chase calls (currently averaging 3.0 calls per lead).
- **Milestones:** Placed $\rightarrow$ KYC Verification $\rightarrow$ Verified $\rightarrow$ Serviceability Assessment $\rightarrow$ Installation Scheduled $\rightarrow$ Installation in Progress $\rightarrow$ Activated.

### Module F: Back-Office Dashboard
- **Goal:** Empower channel partners and enterprise sales teams to intervene where automation stalls.
- **Intelligence:** Real-time funnel metrics computed over the 5,000 lead dataset, segment distribution, and explainable Lead Propensity Scoring (0–100).
