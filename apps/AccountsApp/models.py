from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        CLINICIAN = 'CLINICIAN', 'Clinician'
        FACILITY_STAFF = 'FACILITY_STAFF', 'Facility Staff'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )

    def __str__(self):
        return self.username