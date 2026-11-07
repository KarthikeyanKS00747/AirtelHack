"""
Deterministic AI Business Advisor — conversational flow without external LLM dependency.
Implements multi-turn conversation with adaptive questioning.
Falls back gracefully when no LLM API key is configured.
"""
from typing import Optional
import json
import re

SYSTEM_PROMPT = """You are Accel Business Advisor, an expert consultant helping Indian small and medium businesses (MSMEs) 
choose the right telecom and digital connectivity bundle. You are friendly, knowledgeable and concise.
Your goal is to understand the business and recommend the most suitable products from the Accel Business catalogue.

Ask only relevant questions based on what you already know. Do not ask for information already provided.
After gathering enough information, generate a structured business profile as JSON.
"""

# ── Persona Presets ───────────────────────────────────────────────────────

PERSONAS = {
    "kirana": {
        "name": "Price-sensitive Kirana Store",
        "description": "Small neighbourhood grocery store with 1-2 staff",
        "profile": {
            "segment": "micro",
            "business_type": "Retail - Grocery / Kirana",
            "employee_count": 2,
            "num_sites": 1,
            "city_tier": 2,
            "has_gstin": False,
            "needs_broadband": True,
            "needs_mobile_sims": 1,
            "needs_pos": True,
            "needs_cctv": 1,
            "needs_whatsapp": True,
            "budget_monthly_inr": 2000,
        },
        "opening": "Hello! I run a small kirana store in a Tier 2 city. I need internet for my UPI payments and maybe a camera. My budget is around ₹2,000/month.",
    },
    "clinic": {
        "name": "Professional Clinic / Office",
        "description": "5-doctor medical clinic with 15 staff, GST registered",
        "profile": {
            "segment": "prof",
            "business_type": "Healthcare - Medical Clinic",
            "employee_count": 15,
            "num_sites": 1,
            "city_tier": 1,
            "has_gstin": True,
            "needs_broadband": True,
            "needs_mobile_sims": 5,
            "needs_cloud_email": True,
            "needs_cctv": 2,
            "needs_backup": True,
            "needs_toll_free": True,
            "needs_firewall": True,
        },
        "opening": "We're a medical clinic with 15 staff in a Tier 1 city. We have a GSTIN. We need reliable internet, email for doctors, CCTV, and a toll-free number for appointments.",
    },
    "multi_retail": {
        "name": "Multi-location Retail Chain",
        "description": "Fashion retail with 5 stores, 40 employees, GST registered",
        "profile": {
            "segment": "multi",
            "business_type": "Retail - Fashion / Apparel",
            "employee_count": 40,
            "num_sites": 5,
            "city_tier": 1,
            "has_gstin": True,
            "needs_broadband": True,
            "needs_mobile_sims": 10,
            "needs_cloud_email": True,
            "needs_pos": True,
            "needs_cctv": 3,
            "needs_whatsapp": True,
            "needs_sms": True,
            "needs_firewall": True,
        },
        "opening": "I run 5 fashion retail stores across a Tier 1 city with 40 staff. All stores are GST-registered. We need connectivity across all sites, POS systems, employee mobiles, CCTV, and customer communication tools.",
    },
}


# ── Conversation State Machine ────────────────────────────────────────────

QUESTIONS = [
    ("business_name", "What is your business name?"),
    ("business_type", "What type of business do you run? (e.g., retail, clinic, manufacturing, restaurant)"),
    ("employee_count", "How many employees work at your business?"),
    ("num_sites", "Do you operate from one location or multiple sites?"),
    ("city", "Which city is your main location?"),
    ("city_tier", "Is your city a major metro (Tier 1) or a smaller city (Tier 2)?"),
    ("has_gstin", "Is your business registered for GST (do you have a GSTIN)?"),
    ("needs_broadband", "Do you need a business internet connection?"),
    ("needs_mobile_sims", "How many business mobile SIM cards do you need?"),
    ("needs_cloud_email", "Do you need business email on your own domain (e.g., name@yourbusiness.com)?"),
    ("needs_pos", "Do you need a digital billing and POS system for payments?"),
    ("needs_cctv", "How many CCTV cameras do you need for security?"),
    ("needs_backup", "Do you need cloud backup for your business data?"),
    ("needs_website", "Would you like a website for your business?"),
    ("needs_whatsapp", "Do you want a verified WhatsApp Business channel for customer service?"),
    ("budget_monthly_inr", "What is your approximate monthly budget for these services (in ₹)?"),
]

QUESTION_KEYS = [q[0] for q in QUESTIONS]
QUESTION_TEXT = {q[0]: q[1] for q in QUESTIONS}

# Which questions to skip based on prior answers
SKIP_CONDITIONS = {
    "needs_cloud_email": lambda p: p.get("segment") == "micro" and p.get("employee_count", 1) <= 3,
    "needs_backup": lambda p: not p.get("needs_broadband", False),
    "needs_pos": lambda p: p.get("business_type", "").lower() in ("manufacturing", "mfg"),
    "needs_fleet_tracking": lambda p: p.get("segment") not in ("multi", "mfg"),
}


def _extract_value(key: str, user_text: str, profile: dict) -> Optional[any]:
    """Try to extract a profile value from natural language."""
    text = user_text.lower().strip()

    if key == "employee_count":
        nums = re.findall(r'\b(\d+)\b', text)
        if nums:
            return int(nums[0])

    elif key == "num_sites":
        # Check explicit digit first
        nums = re.findall(r'\b(\d+)\b', text)
        if nums:
            return int(nums[0])

        # Check explicit word numbers
        word_nums = {
            "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "both": 2, "couple": 2, "pair": 2
        }
        for w, val in word_nums.items():
            if re.search(r'\b' + w + r'\b', text):
                return val

        # Check multi-site general phrases
        if any(w in text for w in ["multiple", "many", "several", "chain", "few", "multi", "more than one", "branches", "sites"]):
            return 3

        # Check single-site phrases
        if any(w in text for w in ["one", "single", "only one"]):
            return 1

        return 1

    elif key == "has_gstin":
        if any(w in text for w in ["yes", "have", "registered", "gst", "gstin"]):
            return True
        if any(w in text for w in ["no", "not", "don't", "unregistered"]):
            return False

    elif key == "needs_broadband":
        if any(w in text for w in ["yes", "need", "want", "require", "internet"]):
            return True
        return any(w in text for w in ["no", "not"])

    elif key == "needs_mobile_sims":
        nums = re.findall(r'\b(\d+)\b', text)
        if nums:
            return int(nums[0])
        if "no" in text or "none" in text or "don't" in text:
            return 0
        return 0

    elif key == "needs_cloud_email":
        return any(w in text for w in ["yes", "need", "want", "email"])

    elif key == "needs_pos":
        return any(w in text for w in ["yes", "need", "want", "billing", "pos"])

    elif key == "needs_cctv":
        nums = re.findall(r'\b(\d+)\b', text)
        if nums:
            return int(nums[0])
        if any(w in text for w in ["yes", "need", "want", "camera", "cctv"]):
            return 1
        return 0

    elif key == "needs_backup":
        return any(w in text for w in ["yes", "need", "want", "backup"])

    elif key == "needs_website":
        return any(w in text for w in ["yes", "need", "want", "website"])

    elif key == "needs_whatsapp":
        return any(w in text for w in ["yes", "need", "want", "whatsapp"])

    elif key == "city_tier":
        if any(w in text for w in ["metro", "tier 1", "tier-1", "tier1", "major"]):
            return 1
        if any(w in text for w in ["tier 2", "tier-2", "tier2", "smaller", "town"]):
            return 2
        # Tier 1 cities
        tier1 = ["mumbai", "delhi", "bangalore", "bengaluru", "chennai", "hyderabad", "pune", "kolkata", "ahmedabad"]
        if any(city in text for city in tier1):
            return 1
        return 2

    elif key == "budget_monthly_inr":
        nums = re.findall(r'[\d,]+', text.replace(",", ""))
        if nums:
            return float(nums[0])

    elif key == "city":
        # Return as-is
        words = text.split()
        if words:
            return words[-1].title()

    elif key == "business_type":
        return user_text.strip()

    elif key == "business_name":
        return user_text.strip()

    return None


def _infer_segment(profile: dict) -> str:
    btype = profile.get("business_type", "").lower()
    emp = profile.get("employee_count", 1)
    sites = profile.get("num_sites", 1)

    if sites >= 2 or any(w in btype for w in ["chain", "multi", "branches"]):
        return "multi"
    if any(w in btype for w in ["manufactur", "factory", "mill", "plant", "workshop"]):
        return "mfg"
    if any(w in btype for w in ["clinic", "doctor", "lawyer", "architect", "consultant", "office", "ca ", "cs ", "agency", "tech", "software"]):
        return "prof"
    if any(w in btype for w in ["retail", "shop", "store", "kirana", "restaurant", "cafe", "salon", "service"]):
        return "micro" if sites == 1 else "multi"
    if emp >= 15:
        return "prof"
    return "micro"


class DeterministicAdvisor:
    """
    State-machine based advisor that works without any LLM.
    Maintains conversation state and extracts business profile.
    """

    def start_conversation(self, persona: Optional[str] = None) -> tuple[dict, str]:
        """
        Initialize a new conversation.
        Returns (initial_state, greeting_message)
        """
        state = {
            "profile": {},
            "current_question_index": 0,
            "completed": False,
        }

        if persona and persona in PERSONAS:
            preset = PERSONAS[persona]
            state["profile"] = dict(preset["profile"])
            state["completed"] = True
            greeting = f"🎯 **{preset['name']} persona loaded.**\n\n{preset['opening']}\n\nI've pre-filled your business profile. Would you like to see your personalised product recommendations?"
            return state, greeting

        greeting = (
            "Welcome to Accel Business Advisor! 👋\n\n"
            "I'm here to help you find the perfect digital connectivity bundle for your business — "
            "in just a few minutes.\n\n"
            "Let's start: **What is your business name?**"
        )
        return state, greeting

    def process_message(self, state: dict, user_message: str) -> tuple[dict, str, bool]:
        """
        Process a user message and return (updated_state, response, is_complete).
        """
        profile = state.get("profile", {})
        idx = state.get("current_question_index", 0)

        # Try to extract value for current question
        if idx < len(QUESTIONS):
            key, question = QUESTIONS[idx]

            # Skip questions based on conditions
            while idx < len(QUESTIONS):
                key, _ = QUESTIONS[idx]
                cond = SKIP_CONDITIONS.get(key)
                if cond and cond(profile):
                    idx += 1
                    continue
                break

            if idx < len(QUESTIONS):
                key, _ = QUESTIONS[idx]
                value = _extract_value(key, user_message, profile)
                if value is not None:
                    profile[key] = value

            # Move to next question
            idx += 1

            # Skip next questions based on updated profile
            while idx < len(QUESTIONS):
                next_key, _ = QUESTIONS[idx]
                cond = SKIP_CONDITIONS.get(next_key)
                if cond and cond(profile):
                    idx += 1
                    continue
                break

        # Infer segment
        profile["segment"] = _infer_segment(profile)

        state["profile"] = profile
        state["current_question_index"] = idx

        # Check if done
        if idx >= len(QUESTIONS):
            state["completed"] = True
            response = self._build_completion_message(profile)
            return state, response, True

        # Ask next question
        next_key, next_question = QUESTIONS[idx]
        # Context-aware response
        response = self._build_contextual_response(user_message, next_key, next_question, profile)
        return state, response, False

    def _build_contextual_response(self, prev_answer: str, next_key: str, next_question: str, profile: dict) -> str:
        """Build a natural, contextual follow-up."""
        affirmations = ["Got it!", "Thanks!", "Perfect.", "Great.", "Noted."]
        import hashlib
        aff_idx = int(hashlib.md5(prev_answer.encode()).hexdigest(), 16) % len(affirmations)
        aff = affirmations[aff_idx]

        # Special context
        if next_key == "city_tier" and profile.get("city"):
            return f"{aff} And is **{profile['city']}** a major metro city (Tier 1) or a smaller city (Tier 2)?"
        if next_key == "needs_mobile_sims" and profile.get("employee_count"):
            return f"{aff} How many **business mobile SIM cards** do you need for your {profile.get('employee_count')} employees?"
        if next_key == "has_gstin":
            return f"{aff} Is your business **registered for GST** (do you have a GSTIN number)? This unlocks more products."

        return f"{aff} {next_question}"

    def _build_completion_message(self, profile: dict) -> str:
        emp = profile.get("employee_count", 1)
        sites = profile.get("num_sites", 1)
        seg = {"micro": "micro business", "prof": "professional practice", "multi": "multi-site business", "mfg": "manufacturing unit"}.get(profile.get("segment"), "business")
        gstin_note = "" if profile.get("has_gstin") else " (Note: Registering for GST will unlock additional products like cloud telephony and WhatsApp Business.)"

        return (
            f"**Excellent!** I now have a complete picture of your {seg}. 🎉\n\n"
            f"You have **{emp} employee(s)** across **{sites} site(s)** in a "
            f"**Tier {profile.get('city_tier', 1)}** city.{gstin_note}\n\n"
            "Let me now **generate your personalised product recommendations** based on your exact business needs. "
            "Click **View Recommendations** to see your tailored bundle."
        )

    def get_profile_for_engine(self, state: dict) -> dict:
        """Convert advisor state to recommendation engine input dict."""
        return state.get("profile", {})


# LLM-enhanced advisor (when API key available)
class LLMAdvisor:
    def __init__(self, api_key: str, provider: str = "openai"):
        self.api_key = api_key
        self.provider = provider
        self._fallback = DeterministicAdvisor()

    def start_conversation(self, persona=None):
        return self._fallback.start_conversation(persona)

    def process_message(self, state, user_message):
        # TODO: implement LLM call with structured JSON output + Pydantic validation
        # For now, delegate to deterministic advisor
        return self._fallback.process_message(state, user_message)


def get_advisor(api_key: Optional[str] = None):
    """Factory function — returns LLM advisor if API key configured, else deterministic."""
    if api_key:
        return LLMAdvisor(api_key)
    return DeterministicAdvisor()
