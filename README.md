# 🎓 Scholarship & Scheme Eligibility Assistant

An AI-powered scholarship and scheme eligibility assistant that helps students understand which scholarships and government schemes they may qualify for.

Students often have to read lengthy eligibility guidelines containing conditions related to income, category, state, course, year of study, institution and required documents.

This project converts those conditions into a structured, interactive eligibility experience.

Instead of only returning a Yes/No result, the system can:

- Evaluate a student's profile against scheme rules
- Explain why a student is eligible or not eligible
- Identify missing information
- Ask the student to provide missing information
- Re-check eligibility after the profile is updated
- Show supporting eligibility rules
- Display required documents
- Provide a next action for the student

---

## 💡 Problem

Scholarship and welfare scheme eligibility information is often distributed across lengthy documents and different portals.

A student may need to determine:

- Am I eligible?
- Why am I eligible or not eligible?
- Which requirement did I fail?
- What information is missing?
- What documents do I need?
- What should I do next?

Traditional search and filtering can help find schemes, but students may still need to manually interpret complicated eligibility requirements.

---

## 🎯 Our Solution

We built an interactive eligibility assistant that combines:

1. A structured scholarship rule database
2. A deterministic Python eligibility engine
3. An LLM explanation layer
4. Interactive missing-information resolution

### Core flow

```text
Student Profile
       ↓
Match Against Scheme Rules
       ↓
Evaluate Eligibility
       ↓
┌──────────────┬──────────────────────┬────────────────┐
│   Eligible   │ Needs More           │ Not Eligible   │
│              │ Information          │                │
└──────────────┴──────────────────────┴────────────────┘
                         ↓
                Identify Missing Info
                         ↓
                  Ask the Student
                         ↓
                    Re-check
                         ↓
             Updated Eligibility Result
                         ↓
       Explanation + Evidence + Documents
                         ↓
                    Next Action
```

---

## ⭐ Key Feature — Interactive Uncertainty Resolution

The main differentiator of our prototype is how it handles incomplete information.

Instead of assuming an answer or immediately rejecting an incomplete profile, the system identifies what information is missing.

For example:

```text
AICTE approval status = Unknown
            ↓
Needs More Information
            ↓
System identifies the missing condition
            ↓
Student provides the information
            ↓
Eligibility is re-evaluated
```

This creates an interactive loop:

> **Profile → Match → Explain → Identify Missing Information → Ask → Re-evaluate**

---

## 🧠 AI Architecture

The system deliberately separates deterministic eligibility logic from LLM-generated explanations.

```text
                 Student Profile
                       │
                       ▼
              Python Rule Engine
                       │
                       ▼
          Eligibility Status
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Eligible      Needs Info     Not Eligible
                       │
                       ▼
                LLM Explanation
                       │
                       ▼
       ┌─────────────┬─────────────┐
       │             │             │
   Explanation    Evidence    Next Action
                       │
                       ▼
               Student Guidance
```

### Rule Engine

The Python rule engine is responsible for determining the actual eligibility status.

It evaluates structured conditions such as:

- Equality conditions
- Inequality conditions
- Membership conditions
- Income limits
- Course requirements
- Category requirements
- Institution requirements
- Other scheme-specific conditions

The possible results are:

```text
Eligible
Not Eligible
Needs More Information
```

### LLM Layer

The LLM is used as an explanation and interaction layer.

It receives the student profile and the rule-engine results and can generate:

- Human-readable explanations
- Relevant evidence
- Missing information
- Required next actions

The LLM is **not intended to be the source of truth for eligibility**.

---

## 🛡️ Hallucination Mitigation

Large language models can potentially hallucinate.

Our architecture therefore does not allow the LLM to independently determine eligibility.

The system follows this process:

```text
Student Profile
      ↓
Deterministic Rule Engine
      ↓
Eligibility Decision
      ↓
LLM Explanation
      ↓
Response Validation
      ↓
Final Result
```

The system instructs the LLM not to:

- Change the eligibility status
- Invent eligibility requirements
- Invent documents
- Add unsupported rules
- Override the rule engine

The generated response is also validated against the original rule-engine result.

The deterministic rule engine therefore remains the source of truth for the eligibility decision.

---

## 📋 Example Outputs

### 🟢 Eligible

The system can show:

```text
Status: Eligible

Why:
The student's profile satisfies the currently available
eligibility conditions.

Evidence:
Relevant eligibility rules

Required Documents:
- Income Certificate
- Admission / Institution Certificate
- Bank / Aadhaar-linked account details

Next Action:
Review the required documents and proceed to the
official application portal.
```

### 🟡 Needs More Information

```text
Status: Needs More Information

Missing:
- AICTE approval status
- Other scholarship status

Next Action:
Provide the missing information and re-check eligibility.
```

### 🔴 Not Eligible

```text
Status: Not Eligible

Reason:
The student does not satisfy a required eligibility condition.

Evidence:
The specific failed rule is displayed.

Next Action:
Review the failed condition and verify the profile information.
```

---

## 📄 Explainability

The system does not only display a final status.

Each result can include:

- Eligibility status
- Reason
- Supporting rule IDs
- Supporting rule text
- Missing information
- Required documents
- Next action
- Scheme source

This makes the result easier for students to understand and verify.

---

## 🗂️ Project Structure

```text
AI-Hackathon/
│
├── app.py
├── app_backup.py
│
├── backend/
│   ├── __init__.py
│   ├── eligibility.py
│   └── llm.py
│
├── data/
│   └── schemes.json
│
├── tests/
│
├── test_gemini.py
├── test_llm.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

### `app.py`

The Streamlit frontend.

It handles:

- Student profile input
- Eligibility checking
- Result presentation
- Missing-information interaction
- Re-checking eligibility
- Explanation and document display

### `backend/eligibility.py`

The deterministic eligibility engine.

It evaluates the student's profile against the structured scheme rules.

### `backend/llm.py`

The LLM explanation layer.

It takes the deterministic rule-engine results and generates the natural-language explanation and next-action guidance.

### `data/schemes.json`

Contains the structured scholarship and scheme data used by the prototype, including eligibility rules, documents and source information.

---

## 🛠️ Technology Stack

- **Python**
- **Streamlit**
- **Google Gemini / Google GenAI**
- **python-dotenv**
- **JSON**
- **Git / GitHub**

---

## ▶️ Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/aaryar20/Morphosis_AI_PS2.git
cd Morphosis_AI_PS2
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file.

### 5. Run the application

```bash
python -m streamlit run app.py
```

The Streamlit application will open in your browser.

---

## 🔐 API Key Security

The Gemini API key is stored in `.env` and excluded from Git using `.gitignore`.

The repository does not contain the API key.

---

## 📚 Current Prototype Scope

This is a hackathon prototype focused on demonstrating the core eligibility and AI interaction pipeline.

The current prototype uses a curated set of scholarship and scheme rules rather than attempting to cover every scholarship available.

The scheme data is structured so that additional schemes can be added without changing the core eligibility engine.

---

## 🚀 Future Scope

The prototype can be extended into a larger scholarship assistance platform.

### 1. Larger Scheme Database

Expand the curated dataset to include more:

- Central government schemes
- State government schemes
- University scholarships
- Private scholarships
- Welfare schemes

### 2. Database Integration

For larger-scale deployment, structured data can be moved from JSON into a database such as PostgreSQL.

This would allow the system to manage:

- Thousands of schemes
- Student profiles
- Applications
- Documents
- Scheme versions
- Eligibility rules

### 3. Automatic Scheme Updates

A future version could monitor official scheme sources and help identify changes to:

- Income limits
- Categories
- Course requirements
- Application dates
- Document requirements

Updates would still require verification before becoming eligibility rules.

### 4. Document Intelligence

Students could upload documents such as:

- Income certificates
- Domicile certificates
- Category certificates
- Admission certificates

AI could extract relevant information from these documents and reduce manual data entry.

### 5. Application Assistance

The system could guide students beyond eligibility by providing:

- Application checklists
- Document preparation
- Application deadlines
- Application status tracking
- Links to official application portals

### 6. Multilingual Support

The assistant could support multiple Indian languages to make scholarship information more accessible to students and families.

---

## 🎯 Why This Approach?

The goal is not to replace official scholarship portals.

The goal is to provide an intelligent eligibility layer before application.

The assistant helps students answer:

> **"Which schemes might apply to me?"**

> **"Why?"**

> **"What information am I missing?"**

> **"What should I do next?"**

---

## 👥 Team

Built as part of an AI college hackathon.

### Team Roles

- **Frontend / Data / Integration**
  - Streamlit interface
  - Structured scheme data
  - Eligibility integration
  - User interaction

- **Backend / LLM**
  - Eligibility logic
  - Gemini integration
  - LLM explanation and validation

- **Pitch / Product**
  - Problem framing
  - Product direction
  - Demonstration and presentation

---

## 📌 Project Status

**Hackathon Prototype**

The core pipeline is implemented:

```text
Profile
  ↓
Rule Matching
  ↓
Eligibility Decision
  ↓
Missing Information
  ↓
Re-evaluation
  ↓
AI Explanation
  ↓
Evidence + Documents + Next Action
```

The architecture is designed to be extended with additional verified schemes and production-scale infrastructure.