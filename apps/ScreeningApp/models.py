from django.conf import settings
from django.db import models

from apps.PatientsApp.models import Patient


class Screening(models.Model):

    class ScreeningType(models.TextChoices):
        GENERAL = "GENERAL", "General Health"
        INFECTIOUS = "INFECTIOUS", "Infectious Disease"
        AMR = "AMR", "Antimicrobial Resistance"
        COMPREHENSIVE = "COMPREHENSIVE", "Comprehensive"

    class Status(models.TextChoices):
        STARTED = "STARTED", "Started"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        REVIEWED = "REVIEWED", "Reviewed"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="screenings",
    )

    screening_type = models.CharField(
        max_length=20,
        choices=ScreeningType.choices,
        default=ScreeningType.GENERAL,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.STARTED,
    )

    chief_complaint = models.TextField(
        blank=True,
    )

    screening_notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_screenings",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_screenings",
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.patient.user.username} - " f"{self.get_screening_type_display()}"


class ScreeningResponse(models.Model):

    class ResponseType(models.TextChoices):
        TEXT = "TEXT", "Text"
        BOOLEAN = "BOOLEAN", "Yes/No"
        NUMBER = "NUMBER", "Number"
        CHOICE = "CHOICE", "Choice"

    screening = models.ForeignKey(
        Screening,
        on_delete=models.CASCADE,
        related_name="responses",
    )

    question_code = models.CharField(
        max_length=100,
    )

    question = models.TextField()

    response = models.TextField(
        blank=True,
    )

    response_type = models.CharField(
        max_length=10,
        choices=ResponseType.choices,
        default=ResponseType.TEXT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.screening} - {self.question_code}"


class ScreeningAssessment(models.Model):

    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MODERATE = "MODERATE", "Moderate"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    screening = models.OneToOneField(
        Screening,
        on_delete=models.CASCADE,
        related_name="assessment",
    )

    summary = models.TextField(
        blank=True,
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        blank=True,
    )

    recommended_action = models.TextField(
        blank=True,
    )

    ai_assisted = models.BooleanField(
        default=False,
    )

    clinician_notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Assessment for {self.screening}"
