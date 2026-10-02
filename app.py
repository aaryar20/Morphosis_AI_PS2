import json

import streamlit as st

from backend.eligibility import evaluate_all_schemes

from backend.llm import explain_eligibility

# ============================================================

# PAGE CONFIGURATION

# ============================================================

st.set_page_config(

    page_title="Scholarship Eligibility AI",

    page_icon="🎓",

    layout="wide"

)

# ============================================================

# LOAD SCHEME DATA

# ============================================================

with open("data/schemes.json", "r", encoding="utf-8") as file:

    schemes = json.load(file)

# ============================================================

# SESSION STATE

# ============================================================

if "student_profile" not in st.session_state:

    st.session_state.student_profile = None

if "rule_results" not in st.session_state:

    st.session_state.rule_results = None

if "ai_results" not in st.session_state:

    st.session_state.ai_results = None

# ============================================================

# HEADER

# ============================================================

st.title("🎓 Scholarship Eligibility AI")

st.write(

    "Find scholarships and welfare schemes you may qualify for — "

    "with reasons, supporting rules, and missing information."

)

# ============================================================

# STUDENT PROFILE

# ============================================================

st.header("👤 Student Profile")

col1, col2 = st.columns(2)

with col1:

    state = st.selectbox(

        "State of Domicile",

        [

            "Maharashtra",

            "Gujarat",

            "Karnataka",

            "Delhi",

            "Other"

        ]

    )

    domicile_certificate = st.selectbox(

        "Domicile Certificate",

        [

            "Yes",

            "No",

            "Unknown"

        ]

    )

    category = st.selectbox(

        "Category",

        [

            "General",

            "OBC",

            "SC",

            "ST",

            "EWS",

            "DNT",

            "Other"

        ]

    )

    gender = st.selectbox(

        "Gender",

        [

            "Female",

            "Male",

            "Other / Prefer not to say"

        ]

    )

with col2:

    course = st.text_input(

        "Course",

        placeholder="e.g. B.Tech Computer Science"

    )

    course_level = st.selectbox(

        "Course Level",

        [

            "Diploma",

            "Undergraduate Degree",

            "Postgraduate Degree",

            "Other"

        ]

    )

    year = st.selectbox(

        "Year of Study",

        [

            "1",

            "2",

            "3",

            "4",

            "5+"

        ]

    )

    lateral_entry = st.selectbox(

        "Entered through lateral entry?",

        [

            "No",

            "Yes",

            "Unknown"

        ]

    )

    income = st.number_input(

        "Annual Family Income (₹)",

        min_value=0,

        value=200000,

        step=10000

    )

# ============================================================

# ADDITIONAL INFORMATION

# ============================================================

st.header("🔎 Additional Information")

col3, col4 = st.columns(2)

with col3:

    institution_type = st.selectbox(

        "Institution Type",

        [

            "Government",

            "Government Aided",

            "Private / Unaided",

            "Unknown"

        ]

    )

    institution_notified = st.selectbox(

        "Is your institution listed as eligible for the scheme?",

        [

            "Yes",

            "No",

            "Unknown"

        ]

    )

    aiCTE_approved = st.selectbox(

        "Is your institution/course AICTE approved?",

        [

            "Yes",

            "No",

            "Unknown",

            "Not Applicable"

        ]

    )

    other_scholarship = st.selectbox(

        "Currently receiving another government/AICTE scholarship?",

        [

            "No",

            "Yes",

            "Unknown"

        ]

    )

with col4:

    disability_status = st.selectbox(

        "Person with Disability?",

        [

            "Yes",

            "No",

            "Unknown"

        ]

    )

    special_circumstance = st.selectbox(

        "Special Circumstance",

        [

            "None",

            "Orphan",

            "Parent(s) died due to COVID-19",

            "Ward of Armed/Central Paramilitary Forces personnel martyred in action",

            "Parent has critical illness / severe disability",

            "Unknown"

        ]

    )

# ============================================================

# FIELD LABELS

# ============================================================

FIELD_LABELS = {

    "state":

        "State of domicile",

    "domicile_certificate":

        "Domicile certificate",

    "category":

        "Category",

    "gender":

        "Gender",

    "course":

        "Course",

    "course_level":

        "Course level",

    "year":

        "Year of study",

    "lateral_entry":

        "Lateral entry status",

    "family_income":

        "Annual family income",

    "institution_type":

        "Institution type",

    "institution_notified":

        "Whether the institution is notified under the scheme",

    "aicte_approved":

        "AICTE approval status",

    "other_scholarship":

        "Other scholarship status",

    "disability_status":

        "Disability status",

    "special_circumstance":

        "Special circumstance"

}

# ============================================================

# DISPLAY RESULT

# ============================================================

def display_result(result):

    """

    Display one structured eligibility result.

    """

    status = result.get(

        "status",

        "Needs More Information"

    )

    if status == "Eligible":

        st.success("🟢 ELIGIBLE")

    elif status == "Not Eligible":

        st.error("🔴 NOT ELIGIBLE")

    else:

        st.warning(

            "🟡 NEEDS MORE INFORMATION"

        )

    # --------------------------------------------------------

    # Why

    # --------------------------------------------------------

    st.write(

        f"**Why:** "

        f"{result.get('reason', 'No explanation provided.')}"

    )

    # --------------------------------------------------------

    # Evidence

    # --------------------------------------------------------

    evidence = result.get(

        "evidence",

        []

    )

    if evidence:

        with st.expander(

            "📌 Supporting Rule / Evidence",

            expanded=True

        ):

            for item in evidence:

                rule_id = item.get(

                    "rule_id",

                    ""

                )

                text = item.get(

                    "text",

                    ""

                )

                st.markdown(

                    f"**{rule_id}** — {text}"

                )

    # --------------------------------------------------------

    # Missing information

    # --------------------------------------------------------

    missing = result.get(

        "missing_information",

        []

    )

    if missing:

        with st.expander(

            "❓ Information Needed",

            expanded=True

        ):

            for item in missing:

                st.write(

                    f"- {item}"

                )

    # --------------------------------------------------------

    # Documents

    # --------------------------------------------------------

    documents = result.get(

        "required_documents",

        []

    )

    if documents:

        with st.expander(

            "📄 Required Documents"

        ):

            for document in documents:

                st.write(

                    f"- {document}"

                )

# ============================================================

# GENERIC MISSING INFORMATION HELPERS

# ============================================================

def get_missing_fields(results):

    """

    Extract all profile fields responsible for

    Needs More Information results.

    """

    missing_fields = {}

    for result in results:

        for rule in result.get(

            "missing_rules",

            []

        ):

            field = rule.get("field")

            if not field:

                continue

            if field not in missing_fields:

                missing_fields[field] = {

                    "label": FIELD_LABELS.get(

                        field,

                        field.replace(

                            "_",

                            " "

                        ).title()

                    ),

                    "schemes": [],

                    "rules": []

                }

            missing_fields[field]["schemes"].append(

                result["scheme_name"]

            )

            missing_fields[field]["rules"].append(

                rule

            )

    return missing_fields

def render_missing_information(results):

    """

    Render an interactive questionnaire for

    every missing profile field.

    """

    missing_fields = get_missing_fields(

        results

    )

    if not missing_fields:

        return

    st.divider()

    st.header(

        "🔄 Complete Missing Information"

    )

    st.write(

        "Some schemes cannot be evaluated yet. "

        "Answer the questions below and "

        "re-check your eligibility."

    )

    updated_profile = st.session_state.student_profile.copy()

    # ========================================================

    # QUESTIONS

    # ========================================================

    for field, info in missing_fields.items():

        label = info["label"]

        st.subheader(

            f"❓ {label}"

        )

        # ----------------------------------------------------

        # YES / NO / UNKNOWN

        # ----------------------------------------------------

        if field in [

            "domicile_certificate",

            "institution_notified",

            "aicte_approved",

            "other_scholarship",

            "disability_status",

            "lateral_entry"

        ]:

            options = [

                "Unknown",

                "Yes",

                "No"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # CATEGORY

        # ----------------------------------------------------

        elif field == "category":

            options = [

                "Unknown",

                "General",

                "OBC",

                "SC",

                "ST",

                "EWS",

                "DNT",

                "Other"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # GENDER

        # ----------------------------------------------------

        elif field == "gender":

            options = [

                "Unknown",

                "Female",

                "Male",

                "Other / Prefer not to say"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # COURSE LEVEL

        # ----------------------------------------------------

        elif field == "course_level":

            options = [

                "Unknown",

                "Diploma",

                "Undergraduate Degree",

                "Postgraduate Degree",

                "Other"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # YEAR

        # ----------------------------------------------------

        elif field == "year":

            options = [

                "Unknown",

                "1",

                "2",

                "3",

                "4",

                "5+"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # INSTITUTION TYPE

        # ----------------------------------------------------

        elif field == "institution_type":

            options = [

                "Unknown",

                "Government",

                "Government Aided",

                "Private / Unaided"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # SPECIAL CIRCUMSTANCE

        # ----------------------------------------------------

        elif field == "special_circumstance":

            options = [

                "Unknown",

                "None",

                "Orphan",

                "Parent(s) died due to COVID-19",

                "Ward of Armed/Central Paramilitary Forces personnel martyred in action",

                "Parent has critical illness / severe disability"

            ]

            current_value = updated_profile.get(

                field,

                "Unknown"

            )

            if current_value not in options:

                current_value = "Unknown"

            new_value = st.selectbox(

                label,

                options,

                index=options.index(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # FAMILY INCOME

        # ----------------------------------------------------

        elif field == "family_income":

            current_value = updated_profile.get(

                field,

                0

            )

            try:

                current_value = int(

                    current_value

                )

            except (

                ValueError,

                TypeError

            ):

                current_value = 0

            new_value = st.number_input(

                label,

                min_value=0,

                value=current_value,

                step=10000,

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # TEXT FIELD

        # ----------------------------------------------------

        else:

            current_value = updated_profile.get(

                field,

                ""

            )

            if current_value in [

                None,

                "Unknown"

            ]:

                current_value = ""

            new_value = st.text_input(

                label,

                value=str(

                    current_value

                ),

                key=f"missing_{field}"

            )

            updated_profile[field] = new_value

        # ----------------------------------------------------

        # WHY IS THIS REQUIRED?

        # ----------------------------------------------------

        schemes_text = ", ".join(

            dict.fromkeys(

                info["schemes"]

            )

        )

        st.caption(

            f"Required for: {schemes_text}"

        )

    # ========================================================

    # RE-CHECK BUTTON

    # ========================================================

    st.divider()

    if st.button(
        "🔄 Re-check Eligibility",
        key="generic_recheck"
    ):
        st.session_state.student_profile = updated_profile

        updated_rule_results = evaluate_all_schemes(
            schemes,
            updated_profile
        )

        st.session_state.rule_results = updated_rule_results

        try:
            updated_ai_response = explain_eligibility(
                updated_profile,
                updated_rule_results
            )

            st.session_state.ai_results = (
                updated_ai_response.get("results", [])
            )

        except Exception as e:
            st.session_state.ai_results = []
            st.error(f"Explanation error: {e}")

        st.success("Eligibility has been re-evaluated.")

        st.rerun()

# CHECK ELIGIBILITY

# ============================================================

if st.button(

    "🔍 Check Eligibility",

    type="primary"

):

    student_profile = {

        "state":

            state,

        "domicile_certificate":

            domicile_certificate,

        "category":

            category,

        "gender":

            gender,

        "course":

            course,

        "course_level":

            course_level,

        "year":

            year,

        "family_income":

            income,

        "institution_type":

            institution_type,

        "institution_notified":

            institution_notified,

        "aicte_approved":

            aiCTE_approved,

        "disability_status":

            disability_status,

        "special_circumstance":

            special_circumstance,

        "lateral_entry":

            lateral_entry,

        "other_scholarship":

            other_scholarship

    }

    # --------------------------------------------------------

    # Save profile

    # --------------------------------------------------------

    st.session_state.student_profile = (

        student_profile

    )

    # --------------------------------------------------------

    # Rule engine

    # --------------------------------------------------------

    rule_results = evaluate_all_schemes(

        schemes,

        student_profile

    )

    st.session_state.rule_results = (

        rule_results

    )

    # --------------------------------------------------------

    # Gemini / Demo AI

    # --------------------------------------------------------

    with st.spinner(

        "🤖 AI is analyzing the scholarship rules..."

    ):

        try:

            ai_response = explain_eligibility(

                student_profile,

                rule_results

            )

            st.session_state.ai_results = (

                ai_response.get(

                    "results",

                    []

                )

            )

        except Exception as e:

            st.session_state.ai_results = []

            st.warning(

                "AI explanation was unavailable. "

                "Showing rule-engine results instead."

            )

# ============================================================

# DISPLAY RESULTS

# ============================================================

if st.session_state.ai_results:

    st.divider()

    st.header(

        "📋 Eligibility Results"

    )

    st.info(

        "🤖 AI explanation layer applied."

        )

    for result in st.session_state.ai_results:

        with st.container(

            border=True

        ):

            st.subheader(

                result.get(

                    "scheme_name",

                    "Scholarship Scheme"

                )

            )

            display_result(

                result

            )

elif st.session_state.rule_results:

    st.divider()

    st.header(

        "📋 Eligibility Results"

    )

    st.info(

        "Showing rule-engine results."

    )

    for result in st.session_state.rule_results:

        with st.container(

            border=True

        ):

            st.subheader(

                result["scheme_name"]

            )

            status = result["status"]

            if status == "Eligible":

                st.success(

                    "🟢 ELIGIBLE"

                )

            elif status == "Not Eligible":

                st.error(

                    "🔴 NOT ELIGIBLE"

                )

            else:

                st.warning(

                    "🟡 NEEDS MORE INFORMATION"

                )

# ============================================================

# INTERACTIVE MISSING INFORMATION

# ============================================================

if st.session_state.rule_results:

    needs_information = [

        result

        for result in st.session_state.rule_results

        if result["status"] == "Needs More Information"

    ]

    if needs_information:

        render_missing_information(

            st.session_state.rule_results

        )