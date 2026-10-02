import json

from backend.eligibility import evaluate_all_schemes
from backend.llm import explain_eligibility


# Load scholarship rules
with open("data/schemes.json", "r", encoding="utf-8") as file:
    schemes = json.load(file)


# Test student profile
student_profile = {
    "state": "Maharashtra",
    "domicile_certificate": "Yes",
    "category": "OBC",
    "gender": "Female",
    "course": "B.Tech",
    "course_level": "Undergraduate Degree",
    "year": 2,
    "family_income": 250000,
    "institution_type": "Private / Unaided",
    "aicte_approved": "Yes",
    "other_scholarship": "No",
    "disability_status": "No",
    "special_circumstance": "None",
    "lateral_entry": "No"
}


# First: deterministic rule engine
scheme_results = evaluate_all_schemes(
    schemes,
    student_profile
)


# Second: Gemini explanation layer
ai_results = explain_eligibility(
    student_profile,
    scheme_results
)


print(json.dumps(ai_results, indent=2, ensure_ascii=False))