# Privacy & Security Architecture Note — Project Udyam Digital
**Compliance with the Digital Personal Data Protection (DPDP) Act, 2023**
*Accel Business | Airtel SYNC Hackathon 2026*

---

## 1. Regulatory Context

Under India's **Digital Personal Data Protection (DPDP) Act, 2023**, telecommunications and enterprise onboarding platforms operating as **Data Fiduciaries** must adhere to strict principles of lawful processing, purpose specification, explicit consent, data minimization, and demonstrable accountability. Project Udyam Digital is architected from the ground up to satisfy these statutory obligations.

---

## 2. Core Privacy Engineering Principles

```
┌────────────────────────────────────────────────────────────────────────┐
│                      DPDP Act, 2023 Architecture                       │
├───────────────────┬───────────────────┬────────────────────────────────┤
│ Explicit Consent  │ Data Minimisation │ Purpose Limitation             │
│ Clear notices,    │ UUID filenames,   │ Separate KYC, billing,         │
│ versioned records │ masked PII        │ & service delivery scopes      │
├───────────────────┼───────────────────┼────────────────────────────────┤
│ Right to Erasure  │ Access Control    │ Audit Logging                  │
│ Defined 180-day   │ Role-based JWT    │ Tamper-resistant immutable     │
│ retention policy  │ authorization     │ security audit trail           │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

### 1. Explicit, Informed Consent (Section 6)
- **Granular Consent Capture:** Before initiating digital KYC or quote creation, the applicant must review a plain-language summary detailing:
  1. What personal and business information is collected.
  2. The exact operational purposes (identity verification, serviceability, invoicing).
  3. Which third-party services process the data (OCR engines, mock government registries).
  4. The retention duration and grievance redressal mechanism.
- **Immutable Consent Ledger:** Consent decisions are captured in the `consent_records` database table, storing timestamp, consent version (`v1.0`), client IP address, and revocation status.

### 2. Purpose Limitation & Data Minimization (Section 7 & 8)
- **PII Masking in Registries:** GSTIN lookups and Udyam records return masked principal addresses (e.g., `Shop/Unit 124, Ashok Nagar***`) to prevent unauthorized scraping or exposure.
- **UUID File Storage:** Uploaded KYC document images are renamed to random UUID hashes upon upload (`stored_filename`), stripping all client-identifiable filenames (such as `Rajesh_Aadhaar_Front.jpg`).
- **No Unnecessary Data Collection:** The platform collects only what is strictly required to verify business identity and establish telecommunications serviceability.

### 3. Role-Based Access Control (RBAC) & Authorization
- **Least-Privilege Model:** Access is segregated strictly across four roles:
  - `customer`: Can view and manage only their own business profile, quotes, orders, and KYC status.
  - `sales`: Can view assigned leads, quote statuses, and follow-up recommendations.
  - `partner`: Can view only attributable leads registered through their channel.
  - `admin`: Full system access, configuration, and security event auditing.
- **Token Security:** Bearer tokens are signed using HMAC-SHA256 with strict expiration timeouts. Secrets are stored in server-side environment variables and are never exposed to the frontend client.

### 4. Storage Security & Document Retention Policy
- **Encryption:** In-transit traffic is secured via TLS 1.3. Uploaded documents are stored in private server directories (`uploads/kyc/`) inaccessible via direct public HTTP URLs.
- **Defined Retention Schedule:**
  - *Activated Customers:* Verification records retained for the duration of the commercial contract plus statutory telecom regulatory compliance requirements (2 years).
  - *Abandoned / Unactivated Applications:* KYC documents and extracted identity payloads are scheduled for automatic hard purging after 180 days.
  - *Right to Erasure / Withdrawal:* Applicants who do not complete checkout can trigger immediate data withdrawal, revoking consent and deleting unverified uploads.

### 5. Audit Logging & Accountability
- **Tamper-Resistant Audit Trail:** All critical operations—including authentication attempts, document uploads, OCR extractions, registry lookups, order placements, and milestone status transitions—are recorded in the `audit_events` ledger with user ID, event type, resource reference, and timestamp.
- **Grievance Redressal:** The platform includes an explicit data protection officer contact mechanism (`dpo@accelbusiness.in`) and a formal channel for data correction and consent withdrawal requests.
