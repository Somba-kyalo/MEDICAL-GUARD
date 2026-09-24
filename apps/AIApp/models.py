from django.db import models

from apps.ScreeningApp.models import Screening


class AIAnalysis(models.Model):

    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MODERATE = "MODERATE", "Moderate"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        REVIEWED = "REVIEWED", "Reviewed"

    screening = models.ForeignKey(
        Screening,
        on_delete=models.CASCADE,
        related_name="ai_analyses",
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

    explanation = models.TextField(
        blank=True,
    )

    provider = models.CharField(
        max_length=100,
        blank=True,
    )

    model_name = models.CharField(
        max_length=100,
        blank=True,
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )

    error_message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"AI Analysis - {self.screening}"