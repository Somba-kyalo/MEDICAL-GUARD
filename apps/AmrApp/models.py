from django.conf import settings
from django.db import models

from apps.AIApp.models import AIAnalysis
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening


class AMRRecord(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MODERATE = "MODERATE", "Moderate"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        REVIEWED = "REVIEWED", "Reviewed"
        CLOSED = "CLOSED", "Closed"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="amr_records"
    )
    screening = models.ForeignKey(
        Screening, on_delete=models.CASCADE, related_name="amr_records"
    )
    ai_analysis = models.ForeignKey(
        AIAnalysis,
        on_delete=models.SET_NULL,
        related_name="amr_records",
        null=True,
        blank=True,
    )
    exposure_history = models.TextField(blank=True)
    infection_information = models.TextField(blank=True)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices, blank=True)
    clinical_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.OPEN
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_amr_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AMR Record - {self.patient}"


class Organism(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Antibiotic(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=50, unique=True)
    antibiotic_class = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ResistanceTest(models.Model):
    class Result(models.TextChoices):
        SUSCEPTIBLE = "SUSCEPTIBLE", "Susceptible"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        RESISTANT = "RESISTANT", "Resistant"
        UNKNOWN = "UNKNOWN", "Unknown"

    amr_record = models.ForeignKey(
        AMRRecord, on_delete=models.CASCADE, related_name="resistance_tests"
    )
    organism = models.ForeignKey(
        Organism, on_delete=models.PROTECT, related_name="resistance_tests"
    )
    antibiotic = models.ForeignKey(
        Antibiotic, on_delete=models.PROTECT, related_name="resistance_tests"
    )
    result = models.CharField(
        max_length=12, choices=Result.choices, default=Result.UNKNOWN
    )
    test_notes = models.TextField(blank=True)
    tested_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organism} - {self.antibiotic} - {self.result}"
