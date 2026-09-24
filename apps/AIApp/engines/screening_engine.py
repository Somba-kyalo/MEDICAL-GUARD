from django.core.exceptions import ValidationError

RISK_LEVELS = {
    "LOW",
    "MODERATE",
    "HIGH",
    "URGENT",
}


def analyze_screening_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError("A valid screening payload is required.")

    screening = payload.get("screening")
    patient = payload.get("patient")
    responses = payload.get("responses")

    if not isinstance(screening, dict):
        raise ValidationError("Screening data is required.")

    if not isinstance(patient, dict):
        raise ValidationError("Patient data is required.")

    if not isinstance(responses, list):
        raise ValidationError("Screening responses are required.")

    screening_type = screening.get("type", "")
    chief_complaint = screening.get("chief_complaint", "").strip()
    screening_notes = screening.get("screening_notes", "").strip()

    response_data = []

    for item in responses:
        if not isinstance(item, dict):
            continue

        response_data.append(
            {
                "question_code": item.get("question_code", ""),
                "question": item.get("question", ""),
                "response": item.get("response", ""),
                "response_type": item.get("response_type", ""),
            }
        )

    summary_parts = []

    if screening_type:
        summary_parts.append(f"Screening type: {screening_type}.")

    if chief_complaint:
        summary_parts.append(f"Chief complaint: {chief_complaint}.")

    if response_data:
        summary_parts.append(f"{len(response_data)} screening response(s) recorded.")
    else:
        summary_parts.append("No screening responses were recorded.")

    if screening_notes:
        summary_parts.append(f"Screening notes: {screening_notes}.")

    return {
        "summary": " ".join(summary_parts),
        "risk_level": "LOW",
        "recommended_action": (
            "Review the screening information and recorded responses "
            "before making a clinical decision."
        ),
        "explanation": (
            "This analysis summarizes the information submitted during "
            "screening. It is assistive and requires clinician review."
        ),
        "confidence": None,
        "response_count": len(response_data),
        "responses": response_data,
    }
