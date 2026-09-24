from django.core.exceptions import ValidationError
from django.db import transaction

from .models import AMRRecord, ResistanceTest
from .rules import validate_amr_text, validate_resistance_result, validate_risk_level


class AMRServiceError(Exception):
    pass


@transaction.atomic
def create_amr_record(
    patient,
    screening,
    created_by,
    ai_analysis=None,
    exposure_history="",
    infection_information="",
    risk_level="",
    clinical_notes="",
):
    if screening.patient_id != patient.id:
        raise ValidationError("The screening does not belong to the selected patient.")

    if risk_level:
        risk_level = validate_risk_level(risk_level)

    return AMRRecord.objects.create(
        patient=patient,
        screening=screening,
        ai_analysis=ai_analysis,
        exposure_history=exposure_history,
        infection_information=infection_information,
        risk_level=risk_level,
        clinical_notes=clinical_notes,
        status=AMRRecord.Status.OPEN,
        created_by=created_by,
    )


@transaction.atomic
def update_amr_record(
    amr_record,
    exposure_history=None,
    infection_information=None,
    risk_level=None,
    clinical_notes=None,
    status=None,
):
    if risk_level is not None:
        risk_level = validate_risk_level(risk_level) if risk_level else ""

    if status is not None:
        valid_statuses = {choice[0] for choice in AMRRecord.Status.choices}
        status = str(status).strip().upper()

        if status not in valid_statuses:
            raise ValidationError("A valid AMR record status is required.")

    fields = []

    if exposure_history is not None:
        amr_record.exposure_history = exposure_history
        fields.append("exposure_history")

    if infection_information is not None:
        amr_record.infection_information = infection_information
        fields.append("infection_information")

    if risk_level is not None:
        amr_record.risk_level = risk_level
        fields.append("risk_level")

    if clinical_notes is not None:
        amr_record.clinical_notes = clinical_notes
        fields.append("clinical_notes")

    if status is not None:
        amr_record.status = status
        fields.append("status")

    if fields:
        fields.append("updated_at")
        amr_record.save(update_fields=fields)

    return amr_record


@transaction.atomic
def add_resistance_test(
    amr_record,
    organism,
    antibiotic,
    result,
    test_notes="",
    tested_at=None,
):
    if not amr_record:
        raise ValidationError("A valid AMR record is required.")

    if not organism:
        raise ValidationError("An organism is required.")

    if not antibiotic:
        raise ValidationError("An antibiotic is required.")

    result = validate_resistance_result(result)

    return ResistanceTest.objects.create(
        amr_record=amr_record,
        organism=organism,
        antibiotic=antibiotic,
        result=result,
        test_notes=test_notes,
        tested_at=tested_at,
    )


def get_amr_record(amr_record_id):
    return (
        AMRRecord.objects.select_related(
            "patient",
            "screening",
            "ai_analysis",
            "created_by",
        )
        .prefetch_related(
            "resistance_tests__organism",
            "resistance_tests__antibiotic",
        )
        .get(id=amr_record_id)
    )


def get_patient_amr_records(patient):
    return (
        AMRRecord.objects.filter(patient=patient)
        .select_related(
            "screening",
            "ai_analysis",
            "created_by",
        )
        .prefetch_related(
            "resistance_tests__organism",
            "resistance_tests__antibiotic",
        )
        .order_by("-created_at")
    )
