# Data Analysis & Intelligence Report — Project Udyam Digital
**Comprehensive Statistical Insights from the 5,000 Historical SMB Lead Dataset**
*Reference Date: 2026-07-15 | Airtel SYNC Hackathon 2026*

---

## 1. Executive Findings

A thorough statistical analysis of `smb_leads.csv` reveals critical inefficiencies in Accel Business's legacy acquisition model, highlighting where software automation and intelligent bundling create immediate measurable value:

1. **Abysmal Overall Conversion**: Out of 5,000 leads generated, only **368 became activated customers (7.36%)**.
2. **Severe Drop-Off at the Quote Stage**: While 68% of contacted leads complete a needs assessment, **only 44% accept the quote** (1,974 needs assessed $\rightarrow$ 861 quotes accepted). This is the single largest leak in the acquisition funnel (1,113 lost opportunities).
3. **High KYC Friction**: 32% of customers who accept a quote fail to complete KYC (861 quotes accepted $\rightarrow$ 588 KYC completed), representing 273 lost businesses due to physical paperwork and delays.
4. **The GSTIN Conversion Dividend**: Leads possessing a valid GSTIN exhibit an activation rate of **9.6%**, compared to just **2.0%** for non-GSTIN micro-businesses—a **4.8× conversion uplift**.
5. **Slow Velocity & High Follow-Up Friction**: Activated customers endure an average **17.6 days from lead creation to activation** and make **3.0 status follow-up calls**, driving the blended customer acquisition cost (CAC) to **₹15,000**.

---

## 2. Acquisition Funnel Diagnostics

```
[Lead]            5,000  (100.0%)
  │ (68.1% contacted)
[Contacted]       3,406  ( 68.1%)
  │ (58.0% assessed)
[Needs Assessed]  1,974  ( 39.5%)
  │ (43.6% accepted)  <-- CRITICAL BOTTLENECK (1,113 drop-offs)
[Quote Accepted]    861  ( 17.2%)
  │ (68.3% KYC done)  <-- DOCUMENT FRICTION (273 drop-offs)
[KYC Complete]      588  ( 11.8%)
  │ (62.6% activated)
[Activated]         368  (  7.36%)
```

### Root Cause Analysis of Funnel Leaks

| Stage Transition | Drop-off Count | Identified Root Cause in Legacy Journey | Project Udyam Digital Solution |
|---|---|---|---|
| **Needs Assessed $\rightarrow$ Quote Accepted** | **1,113 leads (56.4% drop)** | Sales quotes take 3–5 days to generate; pricing lacks itemized transparency; unbundled pricing creates sticker shock. | **Instant, transparent bundle generation** in under 60 seconds with itemized monthly & setup fees. |
| **Quote Accepted $\rightarrow$ KYC Complete** | **273 leads (31.7% drop)** | Manual physical document pickup, opaque document age rules (expired utility bills), and slow manual PAN verification. | **Smart Digital KYC** with live OCR, instant mock registry cross-checks, and automated 90-day recency validation. |
| **KYC Complete $\rightarrow$ Activated** | **220 leads (37.4% drop)** | Disconnected field technician scheduling; no customer visibility into installation milestones. | **7-Stage Order Stepper** with automated scheduling and transparent SLA countdowns. |

---

## 3. Segment Economics & Prioritization

The dataset classifies MSMEs into four distinct commercial segments:

| Segment | Lead Share | Activation Rate | Median Monthly Bundle | 6-Mo Churn Rate | NPS | Strategic Priority |
|---|---|---|---|---|---|---|
| **Micro Retail & Services** | 55% | 4.8% | ₹2,499 | 18.2% | +28 | **Volume Engine** (Rapid self-serve 5G AirFiber + Cloud POS) |
| **Professional Offices** | 25% | 11.4% | ₹4,999 | 6.5% | +54 | **Value Core** (Fibre 300, Static IP, Cloud Email, CCTV) |
| **Small Multi-Site** | 15% | 14.8% | ₹12,800 | 4.2% | +62 | **Margin Driver** (SD-WAN, Failover, Centralised Invoicing) |
| **Small Manufacturers** | 5% | 8.2% | ₹18,500 | 5.8% | +48 | **Enterprise Expansion** (Dedicated Leased Line, IoT monitoring) |

### Strategic Decision: Prioritizing the "Professional Offices" & "Micro Retail" Dual-Track
- **Micro Retail (55%)**: Lowest average bundle value (~₹2,500/mo) but represents the highest total volume. Onboarding must be 100% zero-touch and self-serve via mobile.
- **Professional Offices (25%)**: Highest net contribution margin (₹4,999/mo, 11.4% conversion, low 6.5% churn). They readily adopt high-margin add-ons (Cloud Backup, Endpoint Security, and Cloud Email).

---

## 4. Lead Propensity Scoring Model

To assist human channel partners and sales reps in prioritizing leads that cannot complete the automated self-serve path, we developed an explainable **Lead Propensity Score (0–100)**:

$$\text{Propensity Score} = w_1 S_{\text{GSTIN}} + w_2 S_{\text{Size}} + w_3 S_{\text{Spend}} + w_4 S_{\text{Funnel}}$$

### Weighting & Factors
1. **GSTIN Registration ($w_1 = 30$ pts)**:
   - Has GSTIN = +30 pts (Based on the 4.8× historical activation differential).
   - No GSTIN = 0 pts.
2. **Employee Size Band ($w_2 = 25$ pts)**:
   - $\ge 25$ employees = +25 pts
   - 10–24 employees = +20 pts
   - 5–9 employees = +15 pts
   - 1–4 employees = +10 pts
3. **Current Telecom Spend ($w_3 = 25$ pts)**:
   - $>$ ₹5,000/mo = +25 pts
   - ₹2,000–₹5,000/mo = +18 pts
   - $<$ ₹2,000/mo = +10 pts
4. **Funnel Engagement Velocity ($w_4 = 20$ pts)**:
   - Reached Quote Accepted = +20 pts
   - Reached Needs Assessed = +12 pts
   - Contacted = +5 pts

**Explainability Principle:** The back-office dashboard displays the exact breakdown of why a lead scored high, ensuring full transparency without using discriminatory personal attributes.
