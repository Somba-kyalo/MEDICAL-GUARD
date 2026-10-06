from django.db import models


class Facility(models.Model):
    class FacilityType(models.TextChoices):
        HOSPITAL = "HOSPITAL", "Hospital"
        HEALTH_CENTER = "HEALTH_CENTER", "Health Center"
        CLINIC = "CLINIC", "Clinic"
        DISPENSARY = "DISPENSARY", "Dispensary"
        LABORATORY = "LABORATORY", "Laboratory"
        PHARMACY = "PHARMACY", "Pharmacy"
        REFERRAL_CENTER = "REFERRAL_CENTER", "Referral Center"
        OTHER = "OTHER", "Other"

    class OperatingStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        TEMPORARILY_CLOSED = "TEMPORARILY_CLOSED", "Temporarily Closed"

    name = models.CharField(max_length=255)

    facility_code = models.CharField(
        max_length=50,
        unique=True,
    )

    facility_type = models.CharField(
        max_length=30,
        choices=FacilityType.choices,
    )

    county = models.CharField(max_length=100)

    sub_county = models.CharField(
        max_length=100,
        blank=True,
    )

    address = models.CharField(
        max_length=255,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    services = models.TextField(
        blank=True,
    )

    referral_available = models.BooleanField(
        default=True,
    )

    operating_status = models.CharField(
        max_length=25,
        choices=OperatingStatus.choices,
        default=OperatingStatus.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name} ({self.facility_code})"


class FacilityResource(models.Model):
    class ResourceCategory(models.TextChoices):
        STAFF = "STAFF", "Staff"
        EQUIPMENT = "EQUIPMENT", "Equipment"
        BED = "BED", "Beds"
        MEDICINE = "MEDICINE", "Medicine"
        LABORATORY = "LABORATORY", "Laboratory"
        OTHER = "OTHER", "Other"

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="resources",
    )

    name = models.CharField(
        max_length=255,
    )

    category = models.CharField(
        max_length=20,
        choices=ResourceCategory.choices,
    )

    quantity = models.PositiveIntegerField(
        default=0,
    )

    available = models.BooleanField(
        default=True,
    )

    notes = models.TextField(
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.facility.name} - {self.name}"
