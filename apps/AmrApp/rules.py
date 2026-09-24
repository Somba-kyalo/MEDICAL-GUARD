from django.core.exceptions import ValidationError

from .models import AMRRecord, ResistanceTest


def validate_risk_level(risk_level):
    risk_level = str(risk_level).strip().upper()

    valid_levels = {choice[0] for choice in AMRRecord.RiskLevel.choices}

    if risk_level not in valid_levels:
        raise ValidationError("A valid AMR risk level is required.")

    return risk_level


def validate_resistance_result(result):
    result = str(result).strip().upper()

    valid_results = {choice[0] for choice in ResistanceTest.Result.choices}

    if result not in valid_results:
        raise ValidationError("A valid resistance test result is required.")

    return result


def is_resistant(result):
    return validate_resistance_result(result) == ResistanceTest.Result.RESISTANT


def validate_amr_text(value, field_name):
    value = str(value).strip()

    if not value:
        raise ValidationError(f"{field_name} is required.")

    return value
