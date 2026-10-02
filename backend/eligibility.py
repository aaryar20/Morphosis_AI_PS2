def evaluate_rule(rule, profile):
    """
    Evaluate one rule.

    Returns:
        True  -> satisfied
        False -> failed
        None  -> missing/unknown
    """

    field = rule.get("field")
    operator = rule.get("operator")
    expected = rule.get("value")

    actual = profile.get(field)

    # Missing information
    if actual is None or actual == "" or actual == "Unknown":
        return None

    if operator == "equals":
        return actual == expected

    if operator == "not_equals":
        return actual != expected

    if operator == "in":
        return actual in expected

    if operator == "contains":
        return str(expected).lower() in str(actual).lower()

    if operator == "less_than":
        try:
            return float(actual) < float(expected)
        except (ValueError, TypeError):
            return None

    if operator == "less_than_or_equal":
        try:
            return float(actual) <= float(expected)
        except (ValueError, TypeError):
            return None

    if operator == "greater_than":
        try:
            return float(actual) > float(expected)
        except (ValueError, TypeError):
            return None

    if operator == "greater_than_or_equal":
        try:
            return float(actual) >= float(expected)
        except (ValueError, TypeError):
            return None

    return None


def evaluate_scheme(scheme, profile):
    """
    Evaluate one scholarship scheme.
    """

    satisfied = []
    failed = []
    missing = []

    for rule in scheme.get("rules", []):

        result = evaluate_rule(rule, profile)

        if result is True:
            satisfied.append(rule)

        elif result is False:
            failed.append(rule)

        else:
            missing.append(rule)

    if failed:
        status = "Not Eligible"
    elif missing:
        status = "Needs More Information"
    else:
        status = "Eligible"

    return {
        "scheme_name": scheme["name"],
        "status": status,
        "satisfied_rules": satisfied,
        "failed_rules": failed,
        "missing_rules": missing,
        "required_documents": scheme.get("documents", []),
        "source": scheme.get("source", {})
    }


def evaluate_all_schemes(schemes, profile):
    """
    Evaluate the student's profile against all schemes.
    """

    return [
        evaluate_scheme(scheme, profile)
        for scheme in schemes
    ]