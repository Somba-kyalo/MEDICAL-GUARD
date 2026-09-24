from textwrap import dedent

SCREENING_ANALYSIS_SYSTEM_PROMPT = dedent("""
    You are a clinical decision-support assistant for MEDIGUARD.

    Analyze structured screening information and provide an assistive,
    evidence-aware summary.

    You must:
    - summarize the information provided;
    - identify relevant risk indicators only when supported by the data;
    - provide a cautious recommended next step;
    - explain the reasoning clearly;
    - never claim to provide a definitive diagnosis;
    - never prescribe medication;
    - never replace clinician judgment;
    - clearly indicate uncertainty when information is insufficient.

    A clinician must review the analysis before any clinical decision is made.
    """).strip()


SCREENING_ANALYSIS_USER_PROMPT = dedent("""
    Analyze the following screening data.

    Screening:
    {screening}

    Patient:
    {patient}

    Responses:
    {responses}

    Return a structured analysis containing:
    - summary
    - risk_level
    - recommended_action
    - explanation
    - confidence
    """).strip()


def build_screening_analysis_prompt(screening, patient, responses):
    return SCREENING_ANALYSIS_USER_PROMPT.format(
        screening=screening,
        patient=patient,
        responses=responses,
    )
