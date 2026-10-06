from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.FollowupsApp.models import FollowUp


def validate_follow_up_type(follow_up_type):
    valid_types = {choice[0] for choice in FollowUp.FollowUpType.choices}

    if follow_up_type not in valid_types:
        raise ValidationError("Invalid follow-up type.")

    return follow_up_type


def validate_status(status):
    valid_statuses = {choice[0] for choice in FollowUp.Status.choices}

    if status not in valid_statuses:
        raise ValidationError("Invalid follow-up status.")

    return status


def create_follow_up(
    patient,
    created_by,
    reason,
    scheduled_at,
    follow_up_type=FollowUp.FollowUpType.GENERAL_REVIEW,
    referral=None,
    status=FollowUp.Status.PENDING,
    outcome="",
    notes="",
    completed_at=None,
):
    validate_follow_up_type(follow_up_type)
    validate_status(status)

    if not reason or not reason.strip():
        raise ValidationError("Follow-up reason is required.")

    if status == FollowUp.Status.COMPLETED and completed_at is None:
        completed_at = timezone.now()

    return FollowUp.objects.create(
        patient=patient,
        referral=referral,
        follow_up_type=follow_up_type,
        reason=reason.strip(),
        scheduled_at=scheduled_at,
        status=status,
        outcome=outcome.strip() if outcome else "",
        notes=notes.strip() if notes else "",
        completed_at=completed_at,
        created_by=created_by,
    )


def update_follow_up(
    follow_up,
    reason=None,
    scheduled_at=None,
    follow_up_type=None,
    status=None,
    outcome=None,
    notes=None,
    completed_at=None,
    referral=None,
):
    if follow_up_type is not None:
        validate_follow_up_type(follow_up_type)
        follow_up.follow_up_type = follow_up_type

    if status is not None:
        validate_status(status)
        follow_up.status = status

    if reason is not None:
        if not reason.strip():
            raise ValidationError("Follow-up reason is required.")
        follow_up.reason = reason.strip()

    if scheduled_at is not None:
        follow_up.scheduled_at = scheduled_at

    if outcome is not None:
        follow_up.outcome = outcome.strip()

    if notes is not None:
        follow_up.notes = notes.strip()

    if referral is not None:
        follow_up.referral = referral

    if follow_up.status == FollowUp.Status.COMPLETED:
        follow_up.completed_at = (
            completed_at or follow_up.completed_at or timezone.now()
        )
    elif completed_at is not None:
        follow_up.completed_at = completed_at

    follow_up.save()

    return follow_up


def get_follow_up(follow_up_id):
    return FollowUp.objects.select_related(
        "patient",
        "patient__user",
        "referral",
        "created_by",
    ).get(id=follow_up_id)


def get_all_follow_ups():
    return FollowUp.objects.select_related(
        "patient",
        "patient__user",
        "referral",
        "created_by",
    ).order_by("-scheduled_at")


def get_patient_follow_ups(patient):
    return (
        FollowUp.objects.select_related(
            "patient",
            "patient__user",
            "referral",
            "created_by",
        )
        .filter(patient=patient)
        .order_by("-scheduled_at")
    )


def get_pending_follow_ups():
    return get_all_follow_ups().filter(status=FollowUp.Status.PENDING)


def get_missed_follow_ups():
    return get_all_follow_ups().filter(status=FollowUp.Status.MISSED)


def complete_follow_up(follow_up, outcome="", notes=""):
    follow_up.status = FollowUp.Status.COMPLETED
    follow_up.completed_at = timezone.now()

    if outcome:
        follow_up.outcome = outcome.strip()

    if notes:
        follow_up.notes = notes.strip()

    follow_up.save()

    return follow_up


def reschedule_follow_up(follow_up, scheduled_at, notes=""):
    follow_up.status = FollowUp.Status.RESCHEDULED
    follow_up.scheduled_at = scheduled_at

    if notes:
        follow_up.notes = notes.strip()

    follow_up.save()

    return follow_up
