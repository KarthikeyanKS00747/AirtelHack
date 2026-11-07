# 3-Minute Hackathon Demo Script — Project Udyam Digital
**Airtel SYNC Hackathon 2026 — Judging Walkthrough**
*Time: Exactly 3:00 Minutes | Coherent End-to-End Story*

---

## Preparation & Quick Reset (Before Judging)
Run this single command to reset the database to a clean, deterministic state in 5 seconds:
```bash
cd backend
python -m app.scripts.reset_demo
```
Ensure servers are active:
- Backend: `uvicorn app.main:app --reload --port 8000`
- Frontend: `npm run dev` (running on `http://localhost:3000`)

---

## The Demo Script: "From Lead to Activation in One Sitting"

### Part 1: The Macro Problem & Kirana Store Persona (0:00 – 0:45)
- **Speaker:**
  > *"Judges, India has over 6 crore small businesses, but Accel's historical data reveals a painful reality: only 7% of MSME leads ever get activated, taking 18 days and costing ₹15,000 per business. Today, we introduce Project Udyam Digital—making small businesses go digital in one sitting.*
  >
  > *Let's meet our first persona: **Gupta General Store**, a price-sensitive micro-retailer in Jaipur.*
- **Action on Screen:**
  1. Open `http://localhost:3000`. Show the premium Airtel-inspired enterprise landing page.
  2. Click **"Get Started"** or select **"Gupta General Store (Kirana)"** persona.
  3. The AI Advisor opens: *"Hello! I see you run Gupta General Store in Jaipur..."*
  4. Notice the system recognizes they need quick, reliable broadband and UPI billing without complex paperwork.
  5. Click **"Generate Recommended Bundle"**.
  6. The Intelligent Bundle Builder appears instantly:
     - Recommends **5G AirFiber 100 (`P04`)** + **Cloud POS & Billing (`P19`)** + **Business Postpaid 299 (`P07`)**.
     - Monthly total: **₹2,147/month**, setup fee: **₹2,500**.
     - Highlights why: Zero fiber trenching delay in Tier-2 Jaipur, plus GST-ready POS.

---

### Part 2: The Professional Clinic Persona & Smart KYC (0:45 – 1:45)
- **Speaker:**
  > *"Now let's see how our engine adapts for a higher-value professional business: **Apex Healthcare Clinic** in Pune—8 employees, 1 site, GSTIN registered, and needing strict patient data privacy.*
- **Action on Screen:**
  1. Switch to the **Clinic Persona**.
  2. The recommendation updates deterministically:
     - Recommends **Biz Fibre 1G (`P03`)**, **Cloud Email & Office Suite (`P16`)** for 8 staff, **2× Cloud CCTV cameras (`P23`)**, and **1 TB Cloud Backup (`P17`)**.
     - Total: **₹6,096/month**.
  3. Click **"Proceed to Checkout"**.
  4. Review the itemized quote with transparent 18% GST and explicit DPDP Act 2023 consent checkbox. Click **"Confirm Order"**.
  5. The **Smart KYC** screen opens:
     - Upload specimen documents from `dataset_raw/kyc_documents/` (e.g. `K01_gst_certificate.png`, `K01_udyam_certificate.png`, `K01_signatory_id.png`, `K01_address_proof.png`).
     - Click **"Verify Documents"**.
     - Live OCR extracts the GSTIN and Udyam number in real time.
     - Dual registry check confirms valid GSTIN (validating the synthetic `X` PAN flag) and Udyam registry match.
     - Address proof date is checked: verified as within 90 days of the hackathon reference date (`2026-07-15`).
     - KYC status updates to **VERIFIED**!

---

### Part 3: Real-Time Order Stepper & Back-Office Intelligence (1:45 – 2:30)
- **Speaker:**
  > *"In the legacy journey, customers made an average of 3 status chase calls because they were left in the dark. With Udyam Digital, the customer has complete visibility."*
- **Action on Screen:**
  1. Navigate to **"Track Order"**.
  2. Show the **7-stage milestone timeline**: *Order Placed $\rightarrow$ KYC Verification $\rightarrow$ Serviceability Assessment $\rightarrow$ Installation Scheduled*.
  3. Next, open the **Back-Office & Partner Dashboard** (`/dashboard`):
     - Log in as Sales / Admin (`sales@demo.udyam` / `Demo1234!`).
     - Show the **Real-Time Funnel** calculated from all 5,000 dataset leads (5,000 $\rightarrow$ 3,406 $\rightarrow$ 1,974 $\rightarrow$ 861 $\rightarrow$ 588 $\rightarrow$ 368).
     - Point out the **Lead Propensity Score (0–100)**: Show how a lead with GSTIN and 25 employees gets an 85+ score with explainable factor badges.
     - Demonstrate how channel partners can intervene on abandoned quotes before the lead goes cold.

---

### Part 4: Commercial Impact & Wrap-Up (2:30 – 3:00)
- **Speaker:**
  > *"To summarize our impact:*
  > 1. *We eliminate the 56% quote cliff with instant, transparent bundle generation.*
  > 2. *We slash KYC drop-offs from 32% to under 10% using automated document verification.*
  > 3. *We cut activation time from 17.6 days to under 4 days.*
  > 4. *Most importantly, we triple lead-to-activation conversion from 7.36% to over 20%, reducing Accel's blended CAC from ₹15,000 to under ₹5,500.*
  >
  > *Project Udyam Digital is built on real data, grounded in the real catalogue, tested with 21 automated tests, and ready for production deployment. Thank you!"*
