from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.AccountsApp.models import User
from apps.AmrApp.models import AMRRecord, Antibiotic, Organism, ResistanceTest
from apps.AnalyticsApp.queries import (
    amr_statistics,
    facility_statistics,
    follow_up_statistics,
    patient_statistics,
    referral_statistics,
    resistance_statistics,
    screening_risk_statistics,
    screening_statistics,
)
from apps.FacilitiesApp.models import Facility
from apps.FollowupsApp.models import FollowUp
from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral
from apps.ScreeningApp.models import Screening, ScreeningAssessment


class AnalyticsTestDataMixin:
    def create_user(self, username, role):
        return User.objects.create_user(
            username=username,
            password="TestPass123!",
            role=role,
        )

    def create_patient(self, username="patient1", sex=Patient.Sex.MALE):
        user = self.create_user(username, User.Role.PATIENT)

        return Patient.objects.create(
            user=user,
            date_of_birth=date(2000, 1, 1),
            sex=sex,
            phone_number="0712345678",
            address="Voi",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0798765432",
        )


class AnalyticsQueryTests(AnalyticsTestDataMixin, TestCase):
    def setUp(self):
        self.admin = self.create_user("admin", User.Role.ADMIN)
        self.patient = self.create_patient()

    def test_patient_statistics(self):
        self.create_patient(
            username="patient2",
            sex=Patient.Sex.FEMALE,
        )

        statistics = patient_statistics()

        self.assertEqual(statistics["total"], 2)
        self.assertEqual(statistics["male"], 1)
        self.assertEqual(statistics["female"], 1)

    def test_screening_statistics(self):
        screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.GENERAL,
            status=Screening.Status.COMPLETED,
            created_by=self.admin,
        )

        Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.IN_PROGRESS,
            created_by=self.admin,
        )

        Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.INFECTIOUS,
            status=Screening.Status.UNDER_REVIEW,
            created_by=self.admin,
        )

        Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.COMPREHENSIVE,
            status=Screening.Status.REVIEWED,
            created_by=self.admin,
        )

        statistics = screening_statistics()

        self.assertEqual(statistics["total"], 4)
        self.assertEqual(statistics["completed"], 1)
        self.assertEqual(statistics["in_progress"], 1)
        self.assertEqual(statistics["under_review"], 1)
        self.assertEqual(statistics["reviewed"], 1)
        self.assertEqual(len(statistics["by_type"]), 4)

    def test_screening_risk_statistics(self):
        screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.GENERAL,
            status=Screening.Status.COMPLETED,
            created_by=self.admin,
        )

        for risk_level in ScreeningAssessment.RiskLevel:
            ScreeningAssessment.objects.create(
                screening=screening,
                risk_level=risk_level.value,
            )

            screening = Screening.objects.create(
                patient=self.patient,
                screening_type=Screening.ScreeningType.GENERAL,
                status=Screening.Status.COMPLETED,
                created_by=self.admin,
            )

        statistics = screening_risk_statistics()

        self.assertEqual(statistics["low"], 1)
        self.assertEqual(statistics["moderate"], 1)
        self.assertEqual(statistics["high"], 1)
        self.assertEqual(statistics["urgent"], 1)

    def test_amr_statistics(self):
        screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.admin,
        )

        AMRRecord.objects.create(
            patient=self.patient,
            screening=screening,
            risk_level=AMRRecord.RiskLevel.HIGH,
            status=AMRRecord.Status.OPEN,
            created_by=self.admin,
        )

        AMRRecord.objects.create(
            patient=self.patient,
            screening=screening,
            risk_level=AMRRecord.RiskLevel.URGENT,
            status=AMRRecord.Status.REVIEWED,
            created_by=self.admin,
        )

        statistics = amr_statistics()

        self.assertEqual(statistics["records"], 2)
        self.assertEqual(statistics["open"], 1)
        self.assertEqual(statistics["reviewed"], 1)
        self.assertEqual(statistics["high_risk"], 1)
        self.assertEqual(statistics["urgent"], 1)

    def test_resistance_statistics(self):
        screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.admin,
        )

        amr_record = AMRRecord.objects.create(
            patient=self.patient,
            screening=screening,
            created_by=self.admin,
        )

        organism = Organism.objects.create(
            name="Escherichia coli",
            code="ECOLI",
        )

        antibiotic = Antibiotic.objects.create(
            name="Amoxicillin",
            code="AMX",
            antibiotic_class="Penicillin",
        )

        ResistanceTest.objects.create(
            amr_record=amr_record,
            organism=organism,
            antibiotic=antibiotic,
            result=ResistanceTest.Result.RESISTANT,
        )

        statistics = resistance_statistics()

        self.assertEqual(statistics["resistant"], 1)
        self.assertEqual(statistics["susceptible"], 0)
        self.assertEqual(statistics["intermediate"], 0)
        self.assertEqual(statistics["unknown"], 0)

    def test_referral_statistics(self):
        Referral.objects.create(
            patient=self.patient,
            referral_reason="Routine review",
            priority=Referral.Priority.ROUTINE,
            status=Referral.Status.PENDING,
            created_by=self.admin,
        )

        Referral.objects.create(
            patient=self.patient,
            referral_reason="Urgent review",
            priority=Referral.Priority.URGENT,
            status=Referral.Status.ACCEPTED,
            created_by=self.admin,
        )

        Referral.objects.create(
            patient=self.patient,
            referral_reason="Emergency review",
            priority=Referral.Priority.EMERGENCY,
            status=Referral.Status.COMPLETED,
            created_by=self.admin,
        )

        statistics = referral_statistics()

        self.assertEqual(statistics["total"], 3)
        self.assertEqual(statistics["pending"], 1)
        self.assertEqual(statistics["accepted"], 1)
        self.assertEqual(statistics["completed"], 1)
        self.assertEqual(statistics["urgent"], 1)
        self.assertEqual(statistics["emergency"], 1)

    def test_facility_statistics(self):
        Facility.objects.create(
            name="Voi County Hospital",
            facility_code="VOI-001",
            facility_type=Facility.FacilityType.HOSPITAL,
            county="Taita Taveta",
            operating_status=Facility.OperatingStatus.ACTIVE,
            referral_available=True,
        )

        Facility.objects.create(
            name="Voi Clinic",
            facility_code="VOI-002",
            facility_type=Facility.FacilityType.CLINIC,
            county="Taita Taveta",
            operating_status=Facility.OperatingStatus.INACTIVE,
            referral_available=False,
        )

        statistics = facility_statistics()

        self.assertEqual(statistics["total"], 2)
        self.assertEqual(statistics["active"], 1)
        self.assertEqual(statistics["inactive"], 1)
        self.assertEqual(statistics["referral_available"], 1)

    def test_follow_up_statistics(self):
        FollowUp.objects.create(
            patient=self.patient,
            follow_up_type=FollowUp.FollowUpType.GENERAL_REVIEW,
            reason="General review",
            scheduled_at=timezone.now() + timedelta(days=1),
            status=FollowUp.Status.PENDING,
            created_by=self.admin,
        )

        FollowUp.objects.create(
            patient=self.patient,
            follow_up_type=FollowUp.FollowUpType.AMR_REVIEW,
            reason="AMR review",
            scheduled_at=timezone.now() + timedelta(days=1),
            status=FollowUp.Status.COMPLETED,
            created_by=self.admin,
        )

        statistics = follow_up_statistics()

        self.assertEqual(statistics["total"], 2)
        self.assertEqual(statistics["pending"], 1)
        self.assertEqual(statistics["completed"], 1)


class AnalyticsAccessTests(AnalyticsTestDataMixin, TestCase):
    def setUp(self):
        self.patient_user = self.create_user(
            "patient_access",
            User.Role.PATIENT,
        )
        self.clinician = self.create_user(
            "clinician_access",
            User.Role.CLINICIAN,
        )
        self.facility_staff = self.create_user(
            "facility_access",
            User.Role.FACILITY_STAFF,
        )
        self.admin = self.create_user(
            "admin_access",
            User.Role.ADMIN,
        )

    def test_patient_cannot_access_dashboard(self):
        self.client.force_login(self.patient_user)

        response = self.client.get(reverse("AnalyticsApp:dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_clinician_can_access_dashboard(self):
        self.client.force_login(self.clinician)

        response = self.client.get(reverse("AnalyticsApp:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_facility_staff_can_access_dashboard(self):
        self.client.force_login(self.facility_staff)

        response = self.client.get(reverse("AnalyticsApp:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_dashboard(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("AnalyticsApp:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_access_dashboard_api(self):
        self.client.force_login(self.patient_user)

        response = self.client.get(reverse("AnalyticsApp:api_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_clinician_can_access_dashboard_api(self):
        self.client.force_login(self.clinician)

        response = self.client.get(reverse("AnalyticsApp:api_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("patients", response.json())
