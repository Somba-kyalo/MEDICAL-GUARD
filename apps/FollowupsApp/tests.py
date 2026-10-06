from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.FollowupsApp.models import FollowUp
from apps.FollowupsApp.services import (
    complete_follow_up,
    create_follow_up,
    get_all_follow_ups,
    get_follow_up,
    get_missed_follow_ups,
    get_patient_follow_ups,
    get_pending_follow_ups,
    reschedule_follow_up,
    update_follow_up,
)
from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral

User = get_user_model()


class FollowupsAppTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="clinician",
            password="testpass123",
            role=User.Role.CLINICIAN,
        )

        self.patient_user = User.objects.create_user(
            username="patient",
            password="testpass123",
            role=User.Role.PATIENT,
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth="2000-01-01",
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Voi",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0798765432",
        )

        self.referral = Referral.objects.create(
            patient=self.patient,
            referral_reason="Specialist review required.",
            clinical_summary="Patient requires additional assessment.",
            destination_name="Referral Hospital",
            priority=Referral.Priority.ROUTINE,
            created_by=self.user,
        )

        self.scheduled_at = timezone.now() + timedelta(days=2)

        self.follow_up = FollowUp.objects.create(
            patient=self.patient,
            referral=self.referral,
            follow_up_type=FollowUp.FollowUpType.REFERRAL_REVIEW,
            reason="Review referral progress.",
            scheduled_at=self.scheduled_at,
            status=FollowUp.Status.PENDING,
            created_by=self.user,
        )

        self.client.login(
            username="clinician",
            password="testpass123",
        )

    def test_follow_up_creation(self):
        follow_up = create_follow_up(
            patient=self.patient,
            created_by=self.user,
            reason="Review patient progress.",
            scheduled_at=self.scheduled_at,
        )

        self.assertEqual(follow_up.patient, self.patient)
        self.assertEqual(follow_up.created_by, self.user)
        self.assertEqual(
            follow_up.status,
            FollowUp.Status.PENDING,
        )

    def test_follow_up_requires_reason(self):
        with self.assertRaises(ValidationError):
            create_follow_up(
                patient=self.patient,
                created_by=self.user,
                reason="",
                scheduled_at=self.scheduled_at,
            )

    def test_invalid_follow_up_type_rejected(self):
        with self.assertRaises(ValidationError):
            create_follow_up(
                patient=self.patient,
                created_by=self.user,
                reason="Review patient.",
                scheduled_at=self.scheduled_at,
                follow_up_type="INVALID",
            )

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValidationError):
            create_follow_up(
                patient=self.patient,
                created_by=self.user,
                reason="Review patient.",
                scheduled_at=self.scheduled_at,
                status="INVALID",
            )

    def test_get_follow_up(self):
        follow_up = get_follow_up(self.follow_up.id)

        self.assertEqual(
            follow_up.id,
            self.follow_up.id,
        )
        self.assertEqual(
            follow_up.patient,
            self.patient,
        )

    def test_get_all_follow_ups(self):
        follow_ups = get_all_follow_ups()

        self.assertEqual(follow_ups.count(), 1)
        self.assertEqual(
            follow_ups.first().id,
            self.follow_up.id,
        )

    def test_get_patient_follow_ups(self):
        follow_ups = get_patient_follow_ups(self.patient)

        self.assertEqual(follow_ups.count(), 1)
        self.assertEqual(
            follow_ups.first().patient,
            self.patient,
        )

    def test_get_pending_follow_ups(self):
        pending = get_pending_follow_ups()

        self.assertEqual(pending.count(), 1)
        self.assertEqual(
            pending.first().status,
            FollowUp.Status.PENDING,
        )

    def test_get_missed_follow_ups(self):
        self.follow_up.status = FollowUp.Status.MISSED
        self.follow_up.save()

        missed = get_missed_follow_ups()

        self.assertEqual(missed.count(), 1)
        self.assertEqual(
            missed.first().status,
            FollowUp.Status.MISSED,
        )

    def test_update_follow_up(self):
        updated = update_follow_up(
            self.follow_up,
            reason="Updated follow-up reason.",
            notes="Updated notes.",
        )

        self.assertEqual(
            updated.reason,
            "Updated follow-up reason.",
        )
        self.assertEqual(
            updated.notes,
            "Updated notes.",
        )

    def test_complete_follow_up(self):
        completed = complete_follow_up(
            self.follow_up,
            outcome="Patient reviewed successfully.",
            notes="No further immediate action required.",
        )

        self.assertEqual(
            completed.status,
            FollowUp.Status.COMPLETED,
        )
        self.assertIsNotNone(completed.completed_at)
        self.assertEqual(
            completed.outcome,
            "Patient reviewed successfully.",
        )

    def test_reschedule_follow_up(self):
        new_date = timezone.now() + timedelta(days=7)

        rescheduled = reschedule_follow_up(
            self.follow_up,
            scheduled_at=new_date,
            notes="Patient requested a new appointment date.",
        )

        self.assertEqual(
            rescheduled.status,
            FollowUp.Status.RESCHEDULED,
        )
        self.assertEqual(
            rescheduled.scheduled_at,
            new_date,
        )

    def test_all_follow_ups_api(self):
        response = self.client.get(reverse("FollowupsApp:api_records"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["count"], 1)

    def test_patient_follow_ups_api(self):
        response = self.client.get(
            reverse(
                "FollowupsApp:api_patient",
                args=[self.patient.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["count"], 1)

    def test_pending_follow_ups_api(self):
        response = self.client.get(reverse("FollowupsApp:api_pending"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_missed_follow_ups_api(self):
        self.follow_up.status = FollowUp.Status.MISSED
        self.follow_up.save()

        response = self.client.get(reverse("FollowupsApp:api_missed"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["count"], 1)

    def test_follow_up_detail_api(self):
        response = self.client.get(
            reverse(
                "FollowupsApp:api_detail",
                args=[self.follow_up.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(
            response.json()["follow_up"]["id"],
            self.follow_up.id,
        )

    def test_follow_up_detail_page(self):
        response = self.client.get(
            reverse(
                "FollowupsApp:detail",
                args=[self.follow_up.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_list_page(self):
        response = self.client.get(reverse("FollowupsApp:list"))

        self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        response = self.client.get(reverse("FollowupsApp:create"))

        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_access_follow_ups(self):
        self.client.logout()

        self.client.login(
            username="patient",
            password="testpass123",
        )

        response = self.client.get(reverse("FollowupsApp:api_records"))

        self.assertEqual(response.status_code, 403)
