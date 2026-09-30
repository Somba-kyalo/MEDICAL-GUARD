from django.conf import settings
from django.db import models

from apps.AmrApp.models import AMRRecord
from apps.PatientsApp.models import Patient


class Referral(models.Model):
    class Priority(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine"
        URGENT = "URGENT", "Urgent"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="referrals",
    )

    amr_record = models.ForeignKey(
        AMRRecord,
        on_delete=models.SET_NULL,
        related_name="referrals",
        null=True,
        blank=True,
    )

    referral_reason = models.TextField()

    clinical_summary = models.TextField(blank=True)

    destination_name = models.CharField(
        max_length=255,
        blank=True,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.ROUTINE,
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )

    referral_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_referrals",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Referral - {self.patient} - {self.get_status_display()}"