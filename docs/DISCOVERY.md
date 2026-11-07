# Phase 1 Discovery Report — Project Udyam Digital

## Dataset Verification

| File | Expected | Actual | Status |
|---|---|---|---|
| product_catalogue.csv | 25 products | 25 products | ✅ |
| smb_leads.csv | 5,000 leads | 5,000 leads | ✅ |
| mock_gstin_registry.csv | 3,534 records | 3,534 records | ✅ |
| mock_udyam_registry.csv | 2,723 records | 2,723 records | ✅ |
| kyc_documents/ | 47 images | 47 images (K01–K12) | ✅ |

## Dataset Reference Date: 2026-07-15

## Product Catalogue — 25 Products

### Connectivity (P01–P11)
| ID | Name | Price/mo (min–max) | Setup | Tier | Min Employees | GSTIN? | Dependency |
|---|---|---|---|---|---|---|---|
| P01 | Biz Fibre 100 | ₹999–1,199 | ₹0 | 1,2 | 1 | N | — |
| P02 | Biz Fibre 300 | ₹1,499–1,799 | ₹0 | 1,2 | 1 | N | — |
| P03 | Biz Fibre 1G | ₹3,999–4,499 | ₹0 | 1 only | 5 | Y | — |
| P04 | Biz 5G AirFiber 100 | ₹899–1,099 | ₹0 | 1,2 | 1 | N | — |
| P05 | Internet Leased Line 20 | ₹8,000–12,000 | ₹10,000 | 1,2 | 10 | Y | — |
| P06 | Internet Leased Line 100 | ₹25,000–35,000 | ₹15,000 | 1,2 | 25 | Y | — |
| P07 | Business Postpaid 299 | ₹299–399 | ₹0 | 1,2 | 1 | N | — |
| P08 | Business Postpaid 599 | ₹599–799 | ₹0 | 1,2 | 1 | N | — |
| P09 | Backup 4G/5G Failover | ₹499–599 | ₹1,500 | 1,2 | 1 | N | P01\|P02\|P03\|P05\|P06 |
| P10 | Managed SD-WAN | ₹2,500–3,500 | ₹5,000 | 1,2 | 10 | Y | P01\|P02\|P03\|P05\|P06; min_sites=3 |
| P11 | Static IP | ₹200–300 | ₹0 | 1,2 | 1 | N | P01\|P02\|P03 |

### Communication (P12–P15)
| ID | Name | Price/mo | Setup | Min Employees | GSTIN? | Dependency |
|---|---|---|---|---|---|---|
| P12 | Cloud Telephony/SIP | ₹1,000–1,500 | ₹2,000 | 3 | Y | P01\|P02\|P03\|P04\|P05\|P06 |
| P13 | Toll-free Number | ₹1,500–2,000 | ₹1,000 | 1 | Y | — |
| P14 | Business SMS 10k | ₹1,500–2,000 | ₹0 | 1 | Y | — |
| P15 | WhatsApp Business API | ₹999–1,499 | ₹0 | 1 | Y | — |

### Cloud & Productivity (P16–P19)
| ID | Name | Price/mo | Setup | GSTIN? |
|---|---|---|---|---|
| P16 | Cloud Email & Office Suite | ₹125–150/user | ₹0 | N |
| P17 | Cloud Backup 1 TB | ₹499–699 | ₹0 | N |
| P18 | Website + Domain Starter | ₹299–499 | ₹0 | N |
| P19 | Cloud POS & Billing | ₹599–899/counter | ₹2,500 | N |

### Security (P20–P22)
| ID | Name | Price/mo | Setup | Min Employees | GSTIN? | Dependency |
|---|---|---|---|---|---|---|
| P20 | Endpoint Security | ₹99–149/device | ₹0 | 1 | N | — |
| P21 | Managed Firewall | ₹1,999–2,999 | ₹4,000 | 10 | Y | P01\|P02\|P03\|P05\|P06 |
| P22 | Secure Wi-Fi Guest Network | ₹399–599 | ₹1,000 | 1 | N | P01\|P02\|P03\|P04 |

### IoT & Physical (P23–P25)
| ID | Name | Price/mo | Setup | Min Employees | GSTIN? | Dependency |
|---|---|---|---|---|---|---|
| P23 | Cloud CCTV | ₹199–299/camera | ₹1,800 | 1 | N | P01\|P02\|P03\|P04\|P05\|P06 |
| P24 | Machine Monitoring IoT | ₹149–249/device | ₹3,000 | 10 | Y | — |
| P25 | Fleet Tracker | ₹199–299/vehicle | ₹1,500 | 1 | N | — |

## SMB Leads Analysis

### Funnel (from data, matches README)
| Stage | Count | % of prior |
|---|---|---|
| Lead | 5,000 | — |
| Contacted | 3,406 | 68% |
| Needs Assessed | 1,974 | 58% |
| Quote Accepted | 861 | 44% |
| KYC Complete | 588 | 68% |
| Activated | 368 | 63% |
| **Lead→Activation** | **7.36%** | |

- Avg days lead→activation: **17.6 days**
- Avg customer follow-up calls: **3.0**

### Segments
- Micro retail & services: ~1,388 leads
- Professional offices: ~1,247 leads  
- Small multi-site: ~750 leads
- Small manufacturers: ~250 leads
(approximate from data)

### Lead Sources
- Field sales: 1,720
- Website form: 995
- Inbound call: 504
- Referral: 413
- WhatsApp campaign: 358
- Channel partner: ~1,010

## GSTIN Registry
- 3,534 records
- Columns: gstin, legal_name, trade_name, constitution, principal_place_of_business, state, registration_date, status
- 4th char of PAN = 'X' (never valid for real taxpayer) ✅
- Format: 2-digit state + 10-char PAN + 1-digit entity + 1-char 'Z' + checksum

## Udyam Registry
- 2,723 records
- Columns: udyam_number, enterprise_name, enterprise_type, major_activity, nic_description, state, city, date_of_registration
- District code 00 used (non-existent) ✅

## KYC Documents
- 12 applicants (K01–K12)
- Types per applicant: gst_certificate, udyam_certificate, signatory_id, address_proof
- K05 has no udyam_certificate (missing document case)
- 47 total images (4×12 = 48 expected, K05 missing udyam = 47)

## Environment
- Python 3.13.5 (conda base)
- Node.js v20.17.0 / npm 10.8.2
- Docker 29.5.3 ✅ (for PostgreSQL)
- FastAPI 0.138.0, SQLAlchemy 2.0.51, Alembic 1.18.4
- Pydantic 2.13.4, Uvicorn 0.49.0, Pillow 12.3.0
- pytesseract, psycopg2-binary, python-jose, bcrypt, aiofiles, python-dotenv — installed ✅

## Next Steps → PHASE 2+3
1. Architecture & API design docs
2. Docker Compose for PostgreSQL
3. FastAPI backend foundation
4. Next.js frontend scaffold
5. Dataset ingestion scripts
