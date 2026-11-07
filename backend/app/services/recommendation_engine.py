"""
Deterministic Product Recommendation Engine
Uses ONLY catalogue data — never invents products or prices.
"""
from dataclasses import dataclass, field
from typing import Optional
import csv
import os


# ── Data loading ──────────────────────────────────────────────────────────

_CATALOGUE_PATH = os.path.join(os.path.dirname(__file__), "../../data/product_catalogue.csv")

def _load_catalogue():
    path = os.path.abspath(_CATALOGUE_PATH)
    products = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            products.append({
                "id": row["product_id"],
                "category": row["category"],
                "name": row["product_name"],
                "description": row["description"],
                "unit": row["unit"],
                "price_min": float(row["price_min_inr_per_month"]),
                "price_max": float(row["price_max_inr_per_month"]),
                "setup": float(row["one_time_setup_inr"]),
                "min_contract": int(row["min_contract_months"]),
                "tiers": set(row["available_city_tiers"].split(";")),
                "min_employees": int(row["min_employees"]),
                "min_sites": int(row["min_sites"]),
                "requires_gstin": row["requires_gstin"].strip().upper() == "Y",
                "requires_one_of": [x for x in row["requires_one_of"].split("|") if x],
                "install_days": int(row["typical_install_days"]),
                "segments": set(row["target_segments"].split(";")),
            })
    return {p["id"]: p for p in products}


_CATALOGUE: dict = {}

def get_catalogue() -> dict:
    global _CATALOGUE
    if not _CATALOGUE:
        _CATALOGUE = _load_catalogue()
    return _CATALOGUE


# ── Business Profile Input ────────────────────────────────────────────────

@dataclass
class BusinessProfile:
    segment: str = "micro"          # micro, prof, multi, mfg
    city_tier: int = 1
    employee_count: int = 1
    num_sites: int = 1
    has_gstin: bool = False
    needs_broadband: bool = True
    needs_mobile_sims: int = 0
    needs_cloud_email: bool = False
    needs_pos: bool = False
    needs_cctv: int = 0
    needs_backup: bool = False
    needs_website: bool = False
    needs_whatsapp: bool = False
    needs_toll_free: bool = False
    needs_sms: bool = False
    needs_firewall: bool = False
    needs_fleet_tracking: int = 0
    budget_monthly_inr: Optional[float] = None
    preferred_contract_months: Optional[int] = None


@dataclass
class RecommendedItem:
    product_id: str
    product_name: str
    category: str
    description: str
    unit: str
    quantity: int
    unit_price_inr: float           # midpoint price
    monthly_cost_inr: float
    setup_cost_inr: float
    is_mandatory: bool
    reason: str
    install_days: int


@dataclass
class RecommendationResult:
    primary_bundle: list[RecommendedItem] = field(default_factory=list)
    alternative_bundles: list[dict] = field(default_factory=list)
    total_monthly_inr: float = 0
    total_setup_inr: float = 0
    estimated_installation_days: int = 0
    explanation: str = ""
    eligibility_checks: dict = field(default_factory=dict)
    score: float = 0


# ── Core Engine ───────────────────────────────────────────────────────────

class RecommendationEngine:

    def recommend(self, profile: BusinessProfile) -> RecommendationResult:
        cat = get_catalogue()
        result = RecommendationResult()
        items: list[RecommendedItem] = []
        ineligible: dict[str, str] = {}
        selected_ids: set[str] = set()

        def _eligible(pid: str) -> tuple[bool, str]:
            p = cat[pid]
            tier_str = str(profile.city_tier)
            if tier_str not in p["tiers"]:
                return False, f"Not available in Tier {profile.city_tier} city"
            if profile.employee_count < p["min_employees"]:
                return False, f"Requires at least {p['min_employees']} employees (you have {profile.employee_count})"
            if profile.num_sites < p["min_sites"]:
                return False, f"Requires at least {p['min_sites']} sites (you have {profile.num_sites})"
            if p["requires_gstin"] and not profile.has_gstin:
                return False, "Requires GSTIN registration"
            return True, "Eligible"

        def _midprice(p: dict) -> float:
            return round((p["price_min"] + p["price_max"]) / 2, 2)

        def _add(pid: str, qty: int, is_mandatory: bool, reason: str):
            if pid in selected_ids:
                return
            ok, why = _eligible(pid)
            if not ok:
                ineligible[pid] = why
                return
            p = cat[pid]
            unit_price = _midprice(p)
            items.append(RecommendedItem(
                product_id=pid,
                product_name=p["name"],
                category=p["category"],
                description=p["description"],
                unit=p["unit"],
                quantity=qty,
                unit_price_inr=unit_price,
                monthly_cost_inr=round(unit_price * qty, 2),
                setup_cost_inr=round(p["setup"] * qty, 2),
                is_mandatory=is_mandatory,
                reason=reason,
                install_days=p["install_days"],
            ))
            selected_ids.add(pid)

        # ── Step 1: Select base connectivity ────────────────────────────────
        if profile.needs_broadband:
            if profile.num_sites >= 3 and profile.has_gstin and profile.employee_count >= 10:
                # Multi-site: offer SD-WAN with backbone
                if profile.city_tier == 1:
                    _add("P02", profile.num_sites, True, "Biz Fibre 300 as SD-WAN backbone across sites")
                else:
                    _add("P04", profile.num_sites, True, "5G AirFiber for multi-site where fibre may not reach")
            elif profile.employee_count >= 25 and profile.has_gstin and profile.segment == "mfg":
                _add("P06", 1, True, "Enterprise leased line providing dedicated 1:1 internet for manufacturing unit")
            elif profile.employee_count >= 10 and profile.has_gstin:
                _add("P05", 1, True, "Internet Leased Line 20 providing dedicated bandwidth with 99.5% SLA")
            elif profile.employee_count >= 5 and profile.has_gstin and profile.city_tier == 1:
                _add("P03", 1, True, "1 Gbps business fibre for growing professional business")
            elif profile.city_tier == 2 and profile.segment in ("micro", "prof"):
                # Fibre may not be available; offer AirFiber
                _add("P04", 1, True, "5G AirFiber — rapid deployment, no fibre required")
                # Also offer fibre as alternative
            else:
                # Default: Biz Fibre 100 or 300 depending on employees
                if profile.employee_count <= 5:
                    _add("P01", 1, True, "Biz Fibre 100 provides reliable 100 Mbps business connectivity")
                else:
                    _add("P02", 1, True, "Biz Fibre 300 with optional static IP supports growing team")

        # ── Step 2: Backup connectivity for multi-site or critical ops ──────
        if profile.num_sites >= 2 or profile.segment in ("prof", "multi", "mfg"):
            # Only if a wired connection is in basket
            wired = {"P01", "P02", "P03", "P05", "P06"} & selected_ids
            if wired:
                _add("P09", 1, False, "4G/5G failover ensures zero downtime when main link fails")

        # ── Step 3: Mobile SIMs ─────────────────────────────────────────────
        if profile.needs_mobile_sims > 0:
            if profile.segment in ("prof", "multi", "mfg") and profile.needs_mobile_sims >= 3:
                _add("P08", profile.needs_mobile_sims, True,
                     f"{profile.needs_mobile_sims}× Business Postpaid 599 with 150 GB data and priority care")
            else:
                _add("P07", profile.needs_mobile_sims, True,
                     f"{profile.needs_mobile_sims}× Business Postpaid 299 with unlimited calls and 50 GB data")

        # ── Step 4: Cloud email ─────────────────────────────────────────────
        if profile.needs_cloud_email:
            _add("P16", profile.employee_count, True,
                 f"Cloud Email & Office Suite for {profile.employee_count} employees with branded domain")

        # ── Step 5: Cloud POS ───────────────────────────────────────────────
        if profile.needs_pos:
            _add("P19", 1, True, "Cloud POS & Billing: GST-ready invoicing and UPI/card acceptance")

        # ── Step 6: CCTV ────────────────────────────────────────────────────
        if profile.needs_cctv > 0:
            # CCTV requires broadband
            has_broadband = bool({"P01","P02","P03","P04","P05","P06"} & selected_ids)
            if has_broadband:
                _add("P23", profile.needs_cctv, True,
                     f"{profile.needs_cctv} Cloud CCTV cameras with 30-day recording and mobile app")
            else:
                ineligible["P23"] = "Cloud CCTV requires a broadband connection in the bundle"

        # ── Step 7: Cloud Backup ─────────────────────────────────────────────
        if profile.needs_backup:
            _add("P17", 1, False, "1 TB cloud backup protects all business PCs and phones")

        # ── Step 8: Website ──────────────────────────────────────────────────
        if profile.needs_website:
            _add("P18", 1, False, "Website + Domain Starter: professional online presence in 2 days")

        # ── Step 9: WhatsApp Business API ───────────────────────────────────
        if profile.needs_whatsapp and profile.has_gstin:
            _add("P15", 1, False, "Verified WhatsApp channel with catalogue for customer engagement")
        elif profile.needs_whatsapp and not profile.has_gstin:
            ineligible["P15"] = "WhatsApp Business API requires GSTIN registration"

        # ── Step 10: Toll-free ───────────────────────────────────────────────
        if profile.needs_toll_free and profile.has_gstin:
            _add("P13", 1, False, "1800 toll-free number builds customer trust for inbound queries")
        elif profile.needs_toll_free and not profile.has_gstin:
            ineligible["P13"] = "Toll-free number requires GSTIN registration"

        # ── Step 11: SMS pack ────────────────────────────────────────────────
        if profile.needs_sms and profile.has_gstin:
            _add("P14", 1, False, "10,000 SMS/month for transactional alerts and promotions")
        elif profile.needs_sms and not profile.has_gstin:
            ineligible["P14"] = "Business SMS pack requires GSTIN registration"

        # ── Step 12: Cloud Telephony ─────────────────────────────────────────
        if profile.segment in ("prof", "multi") and profile.employee_count >= 3 and profile.has_gstin:
            has_broadband = bool({"P01","P02","P03","P04","P05","P06"} & selected_ids)
            if has_broadband:
                _add("P12", 2, False, "Cloud Telephony with IVR and call recording for professional service")
            else:
                ineligible["P12"] = "Cloud Telephony requires broadband"

        # ── Step 13: Managed Firewall ─────────────────────────────────────────
        if profile.needs_firewall and profile.has_gstin and profile.employee_count >= 10:
            has_wired = bool({"P01","P02","P03","P05","P06"} & selected_ids)
            if has_wired:
                _add("P21", 1, False, "Next-gen firewall managed by Accel SOC for data protection")
            else:
                ineligible["P21"] = "Managed Firewall requires wired broadband"
        elif profile.needs_firewall:
            # Offer endpoint security as alternative
            _add("P20", max(profile.employee_count, 1), False,
                 "Endpoint Security protects all devices with antivirus and ransomware defence")

        # ── Step 14: Secure Wi-Fi ─────────────────────────────────────────────
        if profile.segment in ("micro", "multi", "prof"):
            has_broadband = bool({"P01","P02","P03","P04"} & selected_ids)
            if has_broadband and "P22" not in selected_ids:
                _add("P22", 1, False, "Managed Wi-Fi with guest network and content filtering")

        # ── Step 15: SD-WAN (if multi-site) ──────────────────────────────────
        if profile.num_sites >= 3 and profile.has_gstin and profile.employee_count >= 10:
            if "P10" not in selected_ids:
                _add("P10", profile.num_sites, False,
                     f"SD-WAN centralises {profile.num_sites} sites, prioritises critical apps")

        # ── Step 16: Fleet Tracker ────────────────────────────────────────────
        if profile.needs_fleet_tracking > 0:
            _add("P25", profile.needs_fleet_tracking, False,
                 f"{profile.needs_fleet_tracking} Fleet Trackers with live GPS and IoT dashboard")

        # ── Step 17: Segment-specific extras ─────────────────────────────────
        if profile.segment == "mfg" and profile.has_gstin and profile.employee_count >= 10:
            _add("P24", 2, False, "Machine Monitoring IoT tracks equipment uptime and energy use")

        # ── Dependency resolution ─────────────────────────────────────────────
        # P11 (Static IP): requires P01|P02|P03 (essential for CCTV remote view, hosting, or prof/mfg)
        if (profile.segment in ("prof", "mfg") or profile.needs_cctv > 0) and {"P01","P02","P03"} & selected_ids:
            if "P11" not in selected_ids:
                _add("P11", 1, False, "Static IP enables remote access, CCTV viewing and server hosting")

        # ── Budget filtering ──────────────────────────────────────────────────
        if profile.budget_monthly_inr:
            # Separate mandatory from optional
            mandatory = [i for i in items if i.is_mandatory]
            optional = [i for i in items if not i.is_mandatory]
            mandatory_total = sum(i.monthly_cost_inr for i in mandatory)
            if mandatory_total <= profile.budget_monthly_inr:
                remaining = profile.budget_monthly_inr - mandatory_total
                # Add optional items in priority order until budget exhausted
                included_optional = []
                for opt in optional:
                    if opt.monthly_cost_inr <= remaining:
                        included_optional.append(opt)
                        remaining -= opt.monthly_cost_inr
                items = mandatory + included_optional
            else:
                items = mandatory  # Can't even afford mandatory; will show warning

        # ── Compute totals ─────────────────────────────────────────────────
        total_monthly = round(sum(i.monthly_cost_inr for i in items), 2)
        total_setup = round(sum(i.setup_cost_inr for i in items), 2)
        max_install = max((i.install_days for i in items), default=5)

        # ── Alternative bundles ───────────────────────────────────────────
        alternatives = self._build_alternatives(profile, items, cat)

        # ── Explanation ───────────────────────────────────────────────────
        explanation = self._build_explanation(profile, items, total_monthly, ineligible)

        # ── Score (simple heuristic) ──────────────────────────────────────
        score = self._compute_score(profile, items)

        result.primary_bundle = items
        result.alternative_bundles = alternatives
        result.total_monthly_inr = total_monthly
        result.total_setup_inr = total_setup
        result.estimated_installation_days = max_install
        result.explanation = explanation
        result.eligibility_checks = {
            "eligible": [i.product_id for i in items],
            "ineligible": ineligible,
        }
        result.score = score
        return result

    def _build_alternatives(self, profile: BusinessProfile, primary_items: list, cat: dict) -> list[dict]:
        alternatives = []

        # Alt 1: Budget — replace P02/P03 with P01, drop optional
        if any(i.product_id in ("P02","P03","P05","P06") for i in primary_items):
            budget_items = []
            for item in primary_items:
                if item.product_id in ("P02","P03","P05","P06"):
                    # Downgrade to P01 or P04
                    replacement = "P04" if profile.city_tier == 2 else "P01"
                    p = cat[replacement]
                    budget_items.append({
                        "product_id": replacement,
                        "product_name": p["name"],
                        "quantity": 1,
                        "monthly_cost_inr": round((p["price_min"] + p["price_max"]) / 2, 2),
                        "setup_cost_inr": p["setup"],
                        "reason": "Budget-optimised broadband option",
                    })
                elif item.is_mandatory:
                    budget_items.append({
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "monthly_cost_inr": item.monthly_cost_inr,
                        "setup_cost_inr": item.setup_cost_inr,
                        "reason": item.reason,
                    })
            total_m = sum(i["monthly_cost_inr"] for i in budget_items)
            total_s = sum(i["setup_cost_inr"] for i in budget_items)
            alternatives.append({
                "name": "Budget Essential",
                "description": "Core connectivity only — ideal if you want to start small and upgrade later",
                "items": budget_items,
                "total_monthly_inr": round(total_m, 2),
                "total_setup_inr": round(total_s, 2),
            })

        # Alt 2: Premium — add everything eligible that isn't in primary
        if profile.segment in ("prof", "multi", "mfg"):
            premium_ids = {"P08","P16","P17","P20","P22","P11"}
            premium_items = [{
                "product_id": i.product_id,
                "product_name": i.product_name,
                "quantity": i.quantity,
                "monthly_cost_inr": i.monthly_cost_inr,
                "setup_cost_inr": i.setup_cost_inr,
                "reason": i.reason,
            } for i in primary_items]
            already = {i.product_id for i in primary_items}
            for pid in premium_ids:
                if pid not in already and pid in cat:
                    ok = self._check_eligible(pid, profile, cat, {i.product_id for i in primary_items})
                    if ok:
                        p = cat[pid]
                        qty = max(profile.employee_count, 1) if p["unit"].startswith("per user") or p["unit"].startswith("per device") else 1
                        premium_items.append({
                            "product_id": pid,
                            "product_name": p["name"],
                            "quantity": qty,
                            "monthly_cost_inr": round((p["price_min"]+p["price_max"])/2*qty, 2),
                            "setup_cost_inr": round(p["setup"]*qty, 2),
                            "reason": "Premium add-on for comprehensive protection and productivity",
                        })
            total_m = sum(i["monthly_cost_inr"] for i in premium_items)
            total_s = sum(i["setup_cost_inr"] for i in premium_items)
            alternatives.append({
                "name": "Premium Complete",
                "description": "Full-stack connectivity, security and productivity suite",
                "items": premium_items,
                "total_monthly_inr": round(total_m, 2),
                "total_setup_inr": round(total_s, 2),
            })

        return alternatives

    def _check_eligible(self, pid: str, profile: BusinessProfile, cat: dict, selected: set) -> bool:
        if pid not in cat:
            return False
        p = cat[pid]
        if str(profile.city_tier) not in p["tiers"]:
            return False
        if profile.employee_count < p["min_employees"]:
            return False
        if profile.num_sites < p["min_sites"]:
            return False
        if p["requires_gstin"] and not profile.has_gstin:
            return False
        if p["requires_one_of"] and not (set(p["requires_one_of"]) & selected):
            return False
        return True

    def _build_explanation(self, profile: BusinessProfile, items: list, total: float, ineligible: dict) -> str:
        segment_names = {
            "micro": "micro business",
            "prof": "professional office",
            "multi": "multi-site business",
            "mfg": "manufacturing unit",
        }
        seg = segment_names.get(profile.segment, "business")
        lines = [
            f"Based on your {seg} profile with {profile.employee_count} employee(s) across {profile.num_sites} site(s) "
            f"in a Tier {profile.city_tier} city, we have recommended {len(items)} products totalling "
            f"₹{total:,.0f}/month.",
        ]
        if not profile.has_gstin:
            lines.append("Note: Some products (cloud telephony, leased lines, WhatsApp Business) require GSTIN. "
                         "Registering under GST will unlock these products.")
        if ineligible:
            lines.append(f"{len(ineligible)} product(s) were excluded due to eligibility: " +
                         "; ".join(f"{pid}: {r}" for pid, r in list(ineligible.items())[:3]))
        return " ".join(lines)

    def _compute_score(self, profile: BusinessProfile, items: list) -> float:
        """Simple heuristic score 0–100 based on profile-to-recommendation fit."""
        score = 50.0
        if items:
            score += min(len(items) * 3, 20)
        if profile.has_gstin:
            score += 10
        if profile.num_sites >= 2:
            score += 10
        if profile.needs_broadband and any(i.product_id in {"P01","P02","P03","P04"} for i in items):
            score += 10
        return min(round(score, 1), 100.0)


# Singleton
_engine = RecommendationEngine()

def get_recommendation_engine() -> RecommendationEngine:
    return _engine
