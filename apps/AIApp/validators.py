from django.core.exceptions import ValidationError

from .models import AIAnalysis


def validate_risk_level(risk_level):
    risk_level = str(risk_level).strip().upper()

    valid_levels = {choice[0] for choice in AIAnalysis.RiskLevel.choices}

    if risk_level not in valid_levels:
        raise ValidationError("A valid AI risk level is required.")

    return risk_level


def validate_analysis_status(status):
    status = str(status).strip().upper()

    valid_statuses = {choice[0] for choice in AIAnalysis.Status.choices}

    if status not in valid_statuses:
        raise ValidationError("A valid AI analysis status is required.")

    return status


def validate_analysis_text(value, field_name):
    value = str(value).strip()

    if not value:
        raise ValidationError(f"{field_name} is required.")

    return value


def validate_confidence(confidence):
    if confidence is None:
        return None

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        raise ValidationError("Confidence must be a valid number.")

    if confidence < 0 or confidence > 100:
        raise ValidationError("Confidence must be between 0 and 100.")

    return confidence
