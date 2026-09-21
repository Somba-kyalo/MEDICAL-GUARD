from django.conf import settings
from django.db import models


class Patient(models.Model):

    class Sex(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
    )

    date_of_birth = models.DateField()

    sex = models.CharField(
        max_length=6,
        choices=Sex.choices,
    )

    phone_number = models.CharField(
        max_length=20,
    )

    address = models.CharField(
        max_length=255,
    )

    emergency_contact_name = models.CharField(
        max_length=150,
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.user.username