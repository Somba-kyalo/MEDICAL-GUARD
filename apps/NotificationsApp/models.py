from django.conf import settings
from django.db import models

from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral
from apps.FollowupsApp.models import FollowUp


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        REFERRAL_CREATED = "REFERRAL_CREATED", "Referral Created"
        REFERRAL_UPDATED = "REFERRAL_UPDATED", "Referral Updated"
        REFERRAL_ACCEPTED = "REFERRAL_ACCEPTED", "Referral Accepted"
        REFERRAL_DECLINED = "REFERRAL_DECLINED", "Referral Declined"
        FOLLOW_UP_CREATED = "FOLLOW_UP_CREATED", "Follow-up Created"
        FOLLOW_UP_REMINDER = "FOLLOW_UP_REMINDER", "Follow-up Reminder"
        FOLLOW_UP_COMPLETED = "FOLLOW_UP_COMPLETED", "Follow-up Completed"
        FOLLOW_UP_MISSED = "FOLLOW_UP_MISSED", "Follow-up Missed"
        AMR_ALERT = "AMR_ALERT", "AMR Alert"
        SYSTEM_ALERT = "SYSTEM_ALERT", "System Alert"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    referral = models.ForeignKey(
        Referral,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    follow_up = models.ForeignKey(
        FollowUp,
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    action_url = models.CharField(
        max_length=500,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
