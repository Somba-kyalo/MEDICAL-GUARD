from django.conf import settings
from django.db import models

from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral


class FollowUp(models.Model):
    class FollowUpType(models.TextChoices):
        REFERRAL_REVIEW = "REFERRAL_REVIEW", "Referral Review"
        TREATMENT_REVIEW = "TREATMENT_REVIEW", "Treatment Review"
        SCREENING_REVIEW = "SCREENING_REVIEW", "Screening Review"
        AMR_REVIEW = "AMR_REVIEW", "AMR Review"
        GENERAL_REVIEW = "GENERAL_REVIEW", "General Review"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        MISSED = "MISSED", "Missed"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="follow_ups",
    )

    referral = models.ForeignKey(
        Referral,
        on_delete=models.SET_NULL,
        related_name="follow_ups",
        null=True,
        blank=True,
    )

    follow_up_type = models.CharField(
        max_length=20,
        choices=FollowUpType.choices,
        default=FollowUpType.GENERAL_REVIEW,
    )

    reason = models.TextField()

    scheduled_at = models.DateTimeField()

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )

    outcome = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_follow_ups",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Follow-up - {self.patient} - {self.get_status_display()}"
