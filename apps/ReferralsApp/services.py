from django.core.exceptions import ValidationError
from django.db import transaction

from apps.AmrApp.models import AMRRecord

from .models import Referral


def validate_priority(priority):
    priority = str(priority).strip().upper()

    valid_priorities = {choice[0] for choice in Referral.Priority.choices}

    if priority not in valid_priorities:
        raise ValidationError("A valid referral priority is required.")

    return priority


def validate_status(status):
    status = str(status).strip().upper()

    valid_statuses = {choice[0] for choice in Referral.Status.choices}

    if status not in valid_statuses:
        raise ValidationError("A valid referral status is required.")

    return status


def validate_referral_reason(reason):
    reason = str(reason).strip()

    if not reason:
        raise ValidationError("A referral reason is required.")

    return reason


@transaction.atomic
def create_referral(
    patient,
    created_by,
    referral_reason,
    amr_record=None,
    clinical_summary="",
    destination_name="",
    priority=Referral.Priority.ROUTINE,
    referral_notes="",
):
    referral_reason = validate_referral_reason(referral_reason)
    priority = validate_priority(priority)

    if amr_record is not None:
        if amr_record.patient_id != patient.id:
            raise ValidationError(
                "The AMR record does not belong to the selected patient."
            )

    return Referral.objects.create(
        patient=patient,
        amr_record=amr_record,
        referral_reason=referral_reason,
        clinical_summary=clinical_summary,
        destination_name=destination_name,
        priority=priority,
        status=Referral.Status.PENDING,
        referral_notes=referral_notes,
        created_by=created_by,
    )


@transaction.atomic
def update_referral(
    referral,
    referral_reason=None,
    clinical_summary=None,
    destination_name=None,
    priority=None,
    status=None,
    referral_notes=None,
):
    fields = []

    if referral_reason is not None:
        referral_reason = validate_referral_reason(referral_reason)
        referral.referral_reason = referral_reason
        fields.append("referral_reason")

    if clinical_summary is not None:
        referral.clinical_summary = clinical_summary
        fields.append("clinical_summary")

    if destination_name is not None:
        referral.destination_name = destination_name
        fields.append("destination_name")

    if priority is not None:
        referral.priority = validate_priority(priority)
        fields.append("priority")

    if status is not None:
        referral.status = validate_status(status)
        fields.append("status")

    if referral_notes is not None:
        referral.referral_notes = referral_notes
        fields.append("referral_notes")

    if fields:
        fields.append("updated_at")
        referral.save(update_fields=fields)

    return referral


@transaction.atomic
def update_referral_status(referral, status):
    referral.status = validate_status(status)
    referral.save(update_fields=["status", "updated_at"])
    return referral


def get_referral(referral_id):
    return Referral.objects.select_related(
        "patient",
        "patient__user",
        "amr_record",
        "created_by",
    ).get(id=referral_id)


def get_patient_referrals(patient):
    return (
        Referral.objects.filter(patient=patient)
        .select_related(
            "amr_record",
            "created_by",
        )
        .order_by("-created_at")
    )


def get_all_referrals():
    return Referral.objects.select_related(
        "patient",
        "patient__user",
        "amr_record",
        "created_by",
    ).order_by("-created_at")
