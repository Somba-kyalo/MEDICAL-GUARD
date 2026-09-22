from django.db import transaction
from django.utils import timezone

from .models import Screening, ScreeningAssessment, ScreeningResponse


class ScreeningServiceError(Exception):
    pass


@transaction.atomic
def create_screening(
    patient,
    created_by,
    screening_type=Screening.ScreeningType.GENERAL,
    chief_complaint="",
):
    return Screening.objects.create(
        patient=patient,
        screening_type=screening_type,
        status=Screening.Status.STARTED,
        chief_complaint=chief_complaint,
        created_by=created_by,
    )


@transaction.atomic
def save_screening_response(
    screening,
    question_code,
    question,
    response,
    response_type=ScreeningResponse.ResponseType.TEXT,
):
    if screening.status not in {
        Screening.Status.STARTED,
        Screening.Status.IN_PROGRESS,
    }:
        raise ScreeningServiceError(
            "Responses can only be added while a screening is in progress."
        )

    screening.status = Screening.Status.IN_PROGRESS
    screening.save(update_fields=["status", "updated_at"])

    screening_response, _ = ScreeningResponse.objects.update_or_create(
        screening=screening,
        question_code=question_code,
        defaults={
            "question": question,
            "response": response,
            "response_type": response_type,
        },
    )

    return screening_response


@transaction.atomic
def complete_screening(screening):
    if screening.status != Screening.Status.IN_PROGRESS:
        raise ScreeningServiceError("Only an in-progress screening can be completed.")

    screening.status = Screening.Status.COMPLETED
    screening.completed_at = timezone.now()
    screening.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    return screening


@transaction.atomic
def submit_for_review(screening):
    if screening.status != Screening.Status.COMPLETED:
        raise ScreeningServiceError(
            "Only a completed screening can be submitted for review."
        )

    screening.status = Screening.Status.UNDER_REVIEW
    screening.save(update_fields=["status", "updated_at"])

    return screening


@transaction.atomic
def create_or_update_assessment(
    screening,
    summary="",
    risk_level="",
    recommended_action="",
    ai_assisted=False,
    clinician_notes="",
):
    if screening.status not in {
        Screening.Status.COMPLETED,
        Screening.Status.UNDER_REVIEW,
        Screening.Status.REVIEWED,
    }:
        raise ScreeningServiceError(
            "An assessment can only be created after screening is completed."
        )

    assessment, _ = ScreeningAssessment.objects.update_or_create(
        screening=screening,
        defaults={
            "summary": summary,
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "ai_assisted": ai_assisted,
            "clinician_notes": clinician_notes,
        },
    )

    return assessment


@transaction.atomic
def review_screening(
    screening,
    reviewed_by,
    summary="",
    risk_level="",
    recommended_action="",
    ai_assisted=False,
    clinician_notes="",
):
    if screening.status != Screening.Status.UNDER_REVIEW:
        raise ScreeningServiceError("Only screenings under review can be reviewed.")

    assessment = create_or_update_assessment(
        screening=screening,
        summary=summary,
        risk_level=risk_level,
        recommended_action=recommended_action,
        ai_assisted=ai_assisted,
        clinician_notes=clinician_notes,
    )

    screening.status = Screening.Status.REVIEWED
    screening.reviewed_by = reviewed_by
    screening.reviewed_at = timezone.now()
    screening.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    return screening, assessment
