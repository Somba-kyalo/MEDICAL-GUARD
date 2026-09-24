from django.core.exceptions import ValidationError


def generate_explanation(analysis_result):
    if not isinstance(analysis_result, dict):
        raise ValidationError("A valid analysis result is required.")

    summary = analysis_result.get("summary", "").strip()
    risk_level = analysis_result.get("risk_level", "").strip()
    recommended_action = analysis_result.get(
        "recommended_action",
        "",
    ).strip()

    if not summary:
        raise ValidationError("Analysis summary is required.")

    if not risk_level:
        raise ValidationError("Risk level is required.")

    if not recommended_action:
        raise ValidationError("Recommended action is required.")

    explanation = (
        f"The screening analysis identified a {risk_level.lower()} "
        f"risk level based on the information provided. "
        f"{summary} "
        f"The suggested next step is to {recommended_action.lower()} "
        f"This explanation is assistive and must be reviewed by a clinician "
        f"before any clinical decision is made."
    )

    return explanation
