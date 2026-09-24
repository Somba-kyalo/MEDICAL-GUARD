from django.core.exceptions import ValidationError
from django.db import transaction

from apps.ScreeningApp.models import Screening

from .engines.screening_engine import analyze_screening_payload
from .models import AIAnalysis


def build_screening_payload(screening):
    if not isinstance(screening, Screening):
        raise ValidationError("A valid screening is required.")

    if screening.status != Screening.Status.COMPLETED:
        raise ValidationError(
            "AI analysis can only be performed on a completed screening."
        )

    responses = [
        {
            "question_code": response.question_code,
            "question": response.question,
            "response": response.response,
            "response_type": response.response_type,
        }
        for response in screening.responses.all()
    ]

    return {
        "screening": {
            "id": screening.id,
            "type": screening.screening_type,
            "chief_complaint": screening.chief_complaint,
            "screening_notes": screening.screening_notes,
        },
        "patient": {
            "id": screening.patient.id,
            "sex": screening.patient.sex,
            "date_of_birth": screening.patient.date_of_birth.isoformat(),
        },
        "responses": responses,
    }


@transaction.atomic
def create_ai_analysis(screening):
    payload = build_screening_payload(screening)

    analysis = AIAnalysis.objects.create(
        screening=screening,
        status=AIAnalysis.Status.PROCESSING,
        provider="internal",
        model_name="screening_engine",
    )

    try:
        result = analyze_screening_payload(payload)

        analysis.summary = result["summary"]
        analysis.risk_level = result["risk_level"]
        analysis.recommended_action = result["recommended_action"]
        analysis.explanation = result["explanation"]
        analysis.confidence = result["confidence"]
        analysis.status = AIAnalysis.Status.COMPLETED
        analysis.error_message = ""

        analysis.save(
            update_fields=[
                "summary",
                "risk_level",
                "recommended_action",
                "explanation",
                "confidence",
                "status",
                "error_message",
                "updated_at",
            ]
        )

    except Exception as error:
        analysis.status = AIAnalysis.Status.FAILED
        analysis.error_message = str(error)

        analysis.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        raise

    return analysis
