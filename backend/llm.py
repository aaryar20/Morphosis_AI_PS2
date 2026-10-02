import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

# Keep True while Gemini quota is unavailable.
# Change to False when you want to use the real Gemini API.
DEMO_MODE = True

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if not DEMO_MODE:
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        client = genai.Client(api_key=api_key)


# ============================================================
# DEMO / DETERMINISTIC FALLBACK
# ============================================================

def get_demo_response(profile, scheme_results):
    """
    Deterministic fallback used when Gemini is unavailable.

    IMPORTANT:
    This is NOT an LLM response.

    The Python rule engine remains the source of truth.
    """

    results = []

    for scheme in scheme_results:

        scheme_name = scheme["scheme_name"]
        status = scheme["status"]

        # ----------------------------------------------------
        # NOT ELIGIBLE
        # ----------------------------------------------------

        if status == "Not Eligible":

            failed_rules = scheme.get("failed_rules", [])

            evidence = [
                {
                    "rule_id": rule.get("id", ""),
                    "text": rule.get("text", "")
                }
                for rule in failed_rules
            ]

            if failed_rules:
                reason = (
                    "The student does not satisfy the following "
                    "eligibility condition: "
                    + failed_rules[0].get("text", "")
                )

                next_action = (
                    "Review the failed eligibility condition. "
                    "If the profile information is incorrect, "
                    "update it and re-check."
                )

            else:
                reason = (
                    "The student does not satisfy one or more "
                    "eligibility conditions."
                )

                next_action = (
                    "Review the eligibility conditions and "
                    "verify the profile information."
                )

            results.append(
                {
                    "scheme_name": scheme_name,
                    "status": status,
                    "reason": reason,
                    "evidence": evidence,
                    "missing_information": [],
                    "required_documents": scheme.get(
                        "required_documents",
                        []
                    ),
                    "next_action": next_action
                }
            )

        # ----------------------------------------------------
        # NEEDS MORE INFORMATION
        # ----------------------------------------------------

        elif status == "Needs More Information":

            missing_rules = scheme.get("missing_rules", [])

            evidence = [
                {
                    "rule_id": rule.get("id", ""),
                    "text": rule.get("text", "")
                }
                for rule in missing_rules
            ]

            missing_information = [
                rule.get("text", "")
                for rule in missing_rules
            ]

            next_action = (
                "Provide the missing information above, "
                "then click Re-check Eligibility."
            )

            results.append(
                {
                    "scheme_name": scheme_name,
                    "status": status,
                    "reason": (
                        "More information is required before "
                        "a final eligibility decision can be made."
                    ),
                    "evidence": evidence,
                    "missing_information": missing_information,
                    "required_documents": scheme.get(
                        "required_documents",
                        []
                    ),
                    "next_action": next_action
                }
            )

        # ----------------------------------------------------
        # ELIGIBLE
        # ----------------------------------------------------

        else:

            satisfied_rules = scheme.get(
                "satisfied_rules",
                []
            )

            evidence = [
                {
                    "rule_id": rule.get("id", ""),
                    "text": rule.get("text", "")
                }
                for rule in satisfied_rules
            ]

            results.append(
                {
                    "scheme_name": scheme_name,
                    "status": status,
                    "reason": (
                        "The student's profile satisfies all "
                        "currently available eligibility conditions."
                    ),
                    "evidence": evidence,
                    "missing_information": [],
                    "required_documents": scheme.get(
                        "required_documents",
                        []
                    ),
                    "next_action": (
                        "Review the required documents and "
                        "proceed to the official application portal."
                    )
                }
            )

    return {
        "results": results
    }


# ============================================================
# GEMINI EXPLANATION
# ============================================================

def explain_eligibility(profile, scheme_results):
    """
    Explain deterministic eligibility results using Gemini.

    IMPORTANT:

    Gemini does NOT determine eligibility.

    The Python rule engine determines:

        Eligible
        Not Eligible
        Needs More Information

    Gemini only explains those decisions.
    """

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if DEMO_MODE or client is None:
        return get_demo_response(
            profile,
            scheme_results
        )

    # --------------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an AI assistant explaining scholarship and welfare
scheme eligibility to a college student.

A Python rule engine has ALREADY evaluated the eligibility rules.

The Python rule engine is the SOURCE OF TRUTH.

You MUST NOT:

- change the eligibility status
- invent eligibility requirements
- invent documents
- add rules that are not provided
- remove evidence
- override the rule engine

You MAY:

- explain the result in simple language
- summarize why the student is eligible or not eligible
- explain which information is missing
- suggest the next action using ONLY the supplied information

==================================================
STUDENT PROFILE
==================================================

{json.dumps(profile, indent=2)}

==================================================
RULE ENGINE RESULTS
==================================================

{json.dumps(scheme_results, indent=2)}

==================================================
ALLOWED STATUSES
==================================================

Eligible
Not Eligible
Needs More Information

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Use this exact structure:

{{
    "results": [
        {{
            "scheme_name": "string",
            "status": "Eligible | Not Eligible | Needs More Information",
            "reason": "clear explanation",
            "evidence": [
                {{
                    "rule_id": "string",
                    "text": "string"
                }}
            ],
            "missing_information": [
                "string"
            ],
            "required_documents": [
                "string"
            ],
            "next_action": "string"
        }}
    ]
}}

IMPORTANT:

The "status" MUST exactly match the status calculated
by the Python rule engine.

The "evidence" MUST use only rule IDs and rule text
provided in the rule-engine results.

The "missing_information" MUST contain only information
that is actually missing according to the rule engine.

The "required_documents" MUST come only from the supplied
scheme results.

The "next_action" must be practical and must use only
information available in the supplied profile and
rule-engine results.
"""

    # --------------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------------

    try:

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        raw_output = interaction.output_text.strip()

        # Remove markdown code fences if Gemini returns them.
        if raw_output.startswith("```"):

            raw_output = raw_output.replace(
                "```json",
                ""
            )

            raw_output = raw_output.replace(
                "```",
                ""
            )

            raw_output = raw_output.strip()

        response = json.loads(raw_output)

        if "results" not in response:
            raise ValueError(
                "Gemini response does not contain results."
            )

        return validate_llm_response(
            response,
            scheme_results
        )

    except Exception as e:

        print(
            f"Gemini explanation failed: {e}"
        )

        # Never allow Gemini failure to break the app.
        return get_demo_response(
            profile,
            scheme_results
        )


# ============================================================
# RESPONSE VALIDATION
# ============================================================

def validate_llm_response(
    llm_response,
    rule_results
):
    """
    Validate Gemini output against deterministic
    rule-engine results.

    Python remains the source of truth.
    """

    llm_results = llm_response.get(
        "results",
        []
    )

    rule_result_map = {
        result["scheme_name"]: result
        for result in rule_results
    }

    validated_results = []

    for item in llm_results:

        scheme_name = item.get(
            "scheme_name"
        )

        if scheme_name not in rule_result_map:
            continue

        original = rule_result_map[
            scheme_name
        ]

        # ----------------------------------------------------
        # STATUS SAFETY
        # ----------------------------------------------------

        # Gemini is NEVER allowed to change the
        # deterministic status.
        item["status"] = original["status"]

        # ----------------------------------------------------
        # EVIDENCE SAFETY
        # ----------------------------------------------------

        allowed_rules = (
            original.get("satisfied_rules", [])
            + original.get("failed_rules", [])
            + original.get("missing_rules", [])
        )

        allowed_rule_ids = {
            rule.get("id")
            for rule in allowed_rules
        }

        allowed_rule_map = {
            rule.get("id"): rule
            for rule in allowed_rules
        }

        safe_evidence = []

        for evidence in item.get(
            "evidence",
            []
        ):

            rule_id = evidence.get(
                "rule_id"
            )

            if rule_id in allowed_rule_ids:

                # Use the original rule text instead of
                # trusting Gemini's rewritten evidence.
                safe_evidence.append(
                    {
                        "rule_id": rule_id,
                        "text": allowed_rule_map[
                            rule_id
                        ].get("text", "")
                    }
                )

        item["evidence"] = safe_evidence

        # ----------------------------------------------------
        # REQUIRED DOCUMENTS SAFETY
        # ----------------------------------------------------

        item["required_documents"] = (
            original.get(
                "required_documents",
                []
            )
        )

        # ----------------------------------------------------
        # MISSING INFORMATION SAFETY
        # ----------------------------------------------------

        if original["status"] == "Needs More Information":

            item["missing_information"] = [
                rule.get("text", "")
                for rule in original.get(
                    "missing_rules",
                    []
                )
            ]

        else:

            item["missing_information"] = []

        # ----------------------------------------------------
        # NEXT ACTION
        # ----------------------------------------------------

        next_action = item.get(
            "next_action",
            ""
        )

        if not next_action:

            if original["status"] == "Eligible":

                next_action = (
                    "Review the required documents and "
                    "proceed to the official application portal."
                )

            elif original["status"] == "Needs More Information":

                next_action = (
                    "Provide the missing information and "
                    "re-check eligibility."
                )

            else:

                next_action = (
                    "Review the failed eligibility condition "
                    "and verify the profile information."
                )

        item["next_action"] = next_action

        # ----------------------------------------------------
        # REASON FALLBACK
        # ----------------------------------------------------

        if not item.get("reason"):

            if original["status"] == "Eligible":

                item["reason"] = (
                    "The student's profile satisfies all "
                    "currently available eligibility conditions."
                )

            elif original["status"] == "Needs More Information":

                item["reason"] = (
                    "More information is required before "
                    "a final eligibility decision can be made."
                )

            else:

                item["reason"] = (
                    "The student's profile does not satisfy "
                    "one or more eligibility conditions."
                )

        validated_results.append(item)

    # --------------------------------------------------------
    # HANDLE SCHEMES OMITTED BY GEMINI
    # --------------------------------------------------------

    returned_names = {
        result.get("scheme_name")
        for result in validated_results
    }

    missing_schemes = [
        result
        for result in rule_results
        if result["scheme_name"]
        not in returned_names
    ]

    if missing_schemes:

        fallback = get_demo_response(
            {},
            missing_schemes
        )

        validated_results.extend(
            fallback["results"]
        )

    return {
        "results": validated_results
    }