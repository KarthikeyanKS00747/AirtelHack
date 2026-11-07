import sys
import re

sys.path.insert(0, r"C:\Users\LENOVO\GitHubRepos\AirtelHack\backend")
sys.stdout.reconfigure(encoding='utf-8')

from app.services.advisor_service import _extract_value

test_cases = [
    ("Multiple", 3),
    ("More than one", 3),
    ("Several locations", 3),
    ("Chain of stores", 3),
    ("Two branches", 2),
    ("2", 2),
    ("One", 1),
    ("Single location", 1),
]

print("=== Testing num_sites parser ===")
for text, expected in test_cases:
    actual = _extract_value("num_sites", text, {})
    status = "PASS" if actual == expected else f"FAIL (got {actual}, expected {expected})"
    print(f"Input: {text:<20} | Parsed: {actual} | Expected: {expected} | {status}")
