from django.core.exceptions import ValidationError

from .models import Screening, ScreeningAssessment, ScreeningResponse


def validate_screening_type(screening_type):
    valid_types = Screening.ScreeningType.values

    if screening_type not in valid_types:
        raise ValidationError("Invalid screening type.")

    return screening_type


def validate_response_type(response_type):
    valid_types = ScreeningResponse.ResponseType.values

    if response_type not in valid_types:
        raise ValidationError("Invalid response type.")

    return response_type


def validate_risk_level(risk_level):
    if not risk_level:
        return risk_level

    valid_levels = ScreeningAssessment.RiskLevel.values

    if risk_level not in valid_levels:
        raise ValidationError("Invalid risk level.")

    return risk_level


def validate_question_code(question_code):
    if not question_code or not question_code.strip():
        raise ValidationError("Question code is required.")

    if len(question_code.strip()) > 100:
        raise ValidationError("Question code must not exceed 100 characters.")

    return question_code.strip()


def validate_question(question):
    if not question or not question.strip():
        raise ValidationError("Question is required.")

    return question.strip()


def validate_response(response, response_type):
    response = "" if response is None else str(response).strip()

    if response_type == ScreeningResponse.ResponseType.BOOLEAN:
        if response.lower() not in {"yes", "no", "true", "false"}:
            raise ValidationError("Boolean responses must be Yes, No, True, or False.")

    elif response_type == ScreeningResponse.ResponseType.NUMBER:
        try:
            float(response)
        except (TypeError, ValueError):
            raise ValidationError("Number responses must contain a valid number.")

    return response
