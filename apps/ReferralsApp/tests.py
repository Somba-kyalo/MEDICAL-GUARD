from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.AmrApp.models import AMRRecord
from apps.AmrApp.services import create_amr_record
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening

from apps.ReferralsApp.models import Referral
from apps.ReferralsApp.serializers import ReferralSerializer
from apps.ReferralsApp.services import (
    create_referral,
    get_all_referrals,
    get_patient_referrals,
    get_referral,
    update_referral,
    update_referral_status,
    validate_priority,
    validate_referral_reason,
    validate_status,
)

User = get_user_model()


class ReferralTestBase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="referral_staff",
            password="TestPass123!",
            role=User.Role.CLINICIAN,
        )

        self.facility_staff = User.objects.create_user(
            username="facility_staff",
            password="TestPass123!",
            role=User.Role.FACILITY_STAFF,
        )

        self.admin_user = User.objects.create_user(
            username="referral_admin",
            password="TestPass123!",
            role=User.Role.ADMIN,
        )

        self.patient_user = User.objects.create_user(
            username="patient_user",
            password="TestPass123!",
            role=User.Role.PATIENT,
        )

        self.other_patient_user = User.objects.create_user(
            username="other_patient",
            password="TestPass123!",
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

        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            date_of_birth="2001-01-01",
            sex=Patient.Sex.FEMALE,
            phone_number="0723456789",
            address="Mombasa",
            emergency_contact_name="Other Contact",
            emergency_contact_phone="0787654321",
        )

        self.screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )

        self.amr_record = create_amr_record(
            patient=self.patient,
            screening=self.screening,
            created_by=self.staff_user,
            risk_level=AMRRecord.RiskLevel.HIGH,
        )

    def create_referral(self, **kwargs):
        defaults = {
            "patient": self.patient,
            "created_by": self.staff_user,
            "referral_reason": "Requires specialized antimicrobial management.",
        }
        defaults.update(kwargs)
        return create_referral(**defaults)

    def login_staff(self):
        self.client.login(
            username="referral_staff",
            password="TestPass123!",
        )


class ReferralServiceTests(ReferralTestBase):
    def test_create_referral(self):
        referral = self.create_referral()

        self.assertEqual(referral.patient, self.patient)
        self.assertEqual(referral.created_by, self.staff_user)
        self.assertEqual(
            referral.referral_reason,
            "Requires specialized antimicrobial management.",
        )

    def test_create_referral_defaults_to_pending(self):
        referral = self.create_referral()

        self.assertEqual(
            referral.status,
            Referral.Status.PENDING,
        )

    def test_create_referral_defaults_to_routine(self):
        referral = self.create_referral()

        self.assertEqual(
            referral.priority,
            Referral.Priority.ROUTINE,
        )

    def test_create_referral_with_amr_record(self):
        referral = self.create_referral(
            amr_record=self.amr_record,
        )

        self.assertEqual(
            referral.amr_record,
            self.amr_record,
        )

    def test_create_referral_with_optional_fields(self):
        referral = self.create_referral(
            amr_record=self.amr_record,
            clinical_summary="AMR screening indicates elevated risk.",
            destination_name="Specialized Referral Facility",
            priority=Referral.Priority.URGENT,
            referral_notes="Review on arrival.",
        )

        self.assertEqual(
            referral.clinical_summary,
            "AMR screening indicates elevated risk.",
        )
        self.assertEqual(
            referral.destination_name,
            "Specialized Referral Facility",
        )
        self.assertEqual(
            referral.priority,
            Referral.Priority.URGENT,
        )
        self.assertEqual(
            referral.referral_notes,
            "Review on arrival.",
        )

    def test_create_referral_normalizes_priority(self):
        referral = self.create_referral(
            priority=" urgent ",
        )

        self.assertEqual(
            referral.priority,
            Referral.Priority.URGENT,
        )

    def test_create_referral_rejects_invalid_priority(self):
        with self.assertRaises(ValidationError):
            self.create_referral(priority="INVALID")

    def test_create_referral_requires_reason(self):
        with self.assertRaises(ValidationError):
            self.create_referral(referral_reason="")

    def test_create_referral_rejects_mismatched_amr_record(self):
        other_screening = Screening.objects.create(
            patient=self.other_patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )

        other_amr_record = create_amr_record(
            patient=self.other_patient,
            screening=other_screening,
            created_by=self.staff_user,
        )

        with self.assertRaises(ValidationError):
            self.create_referral(
                amr_record=other_amr_record,
            )

    def test_validate_priority_accepts_valid_value(self):
        result = validate_priority(" urgent ")

        self.assertEqual(
            result,
            Referral.Priority.URGENT,
        )

    def test_validate_priority_rejects_invalid_value(self):
        with self.assertRaises(ValidationError):
            validate_priority("INVALID")

    def test_validate_status_accepts_valid_value(self):
        result = validate_status(" accepted ")

        self.assertEqual(
            result,
            Referral.Status.ACCEPTED,
        )

    def test_validate_status_rejects_invalid_value(self):
        with self.assertRaises(ValidationError):
            validate_status("INVALID")

    def test_validate_referral_reason_strips_value(self):
        result = validate_referral_reason("  Specialized care required.  ")

        self.assertEqual(
            result,
            "Specialized care required.",
        )

    def test_validate_referral_reason_rejects_empty_value(self):
        with self.assertRaises(ValidationError):
            validate_referral_reason("   ")

    def test_update_referral(self):
        referral = self.create_referral()

        updated = update_referral(
            referral=referral,
            referral_reason="Updated referral reason.",
            clinical_summary="Updated summary.",
            destination_name="Referral Centre",
            priority="URGENT",
            status="SENT",
            referral_notes="Updated notes.",
        )

        updated.refresh_from_db()

        self.assertEqual(
            updated.referral_reason,
            "Updated referral reason.",
        )
        self.assertEqual(
            updated.clinical_summary,
            "Updated summary.",
        )
        self.assertEqual(
            updated.destination_name,
            "Referral Centre",
        )
        self.assertEqual(
            updated.priority,
            Referral.Priority.URGENT,
        )
        self.assertEqual(
            updated.status,
            Referral.Status.SENT,
        )
        self.assertEqual(
            updated.referral_notes,
            "Updated notes.",
        )

    def test_update_referral_partial_update(self):
        referral = self.create_referral(
            destination_name="Original Facility",
        )

        update_referral(
            referral=referral,
            destination_name="New Facility",
        )

        referral.refresh_from_db()

        self.assertEqual(
            referral.destination_name,
            "New Facility",
        )
        self.assertEqual(
            referral.referral_reason,
            "Requires specialized antimicrobial management.",
        )

    def test_update_referral_rejects_invalid_priority(self):
        referral = self.create_referral()

        with self.assertRaises(ValidationError):
            update_referral(
                referral=referral,
                priority="INVALID",
            )

    def test_update_referral_rejects_invalid_status(self):
        referral = self.create_referral()

        with self.assertRaises(ValidationError):
            update_referral(
                referral=referral,
                status="INVALID",
            )

    def test_update_referral_status(self):
        referral = self.create_referral()

        update_referral_status(
            referral,
            Referral.Status.ACCEPTED,
        )

        referral.refresh_from_db()

        self.assertEqual(
            referral.status,
            Referral.Status.ACCEPTED,
        )

    def test_update_referral_status_normalizes_value(self):
        referral = self.create_referral()

        update_referral_status(
            referral,
            " in_progress ",
        )

        referral.refresh_from_db()

        self.assertEqual(
            referral.status,
            Referral.Status.IN_PROGRESS,
        )

    def test_update_referral_status_rejects_invalid_status(self):
        referral = self.create_referral()

        with self.assertRaises(ValidationError):
            update_referral_status(
                referral,
                "INVALID",
            )

    def test_get_referral(self):
        referral = self.create_referral()

        result = get_referral(referral.id)

        self.assertEqual(
            result.id,
            referral.id,
        )
        self.assertEqual(
            result.patient,
            self.patient,
        )

    def test_get_patient_referrals(self):
        self.create_referral()

        result = get_patient_referrals(self.patient)

        self.assertEqual(
            result.count(),
            1,
        )
        self.assertEqual(
            result.first().patient,
            self.patient,
        )

    def test_get_patient_referrals_isolated_between_patients(self):
        referral = self.create_referral()

        other_referral = create_referral(
            patient=self.other_patient,
            created_by=self.staff_user,
            referral_reason="Other patient requires specialist care.",
        )

        result = get_patient_referrals(self.patient)

        self.assertEqual(
            result.count(),
            1,
        )
        self.assertEqual(
            result.first().id,
            referral.id,
        )
        self.assertNotEqual(
            result.first().id,
            other_referral.id,
        )

    def test_get_all_referrals(self):
        first = self.create_referral()

        second = create_referral(
            patient=self.other_patient,
            created_by=self.staff_user,
            referral_reason="Other referral.",
        )

        result = get_all_referrals()

        self.assertEqual(
            result.count(),
            2,
        )
        self.assertIn(
            first.id,
            result.values_list("id", flat=True),
        )
        self.assertIn(
            second.id,
            result.values_list("id", flat=True),
        )


class ReferralSerializerTests(ReferralTestBase):
    def test_referral_serializer_contains_expected_fields(self):
        referral = self.create_referral(
            amr_record=self.amr_record,
            priority=Referral.Priority.URGENT,
        )

        update_referral_status(
            referral,
            Referral.Status.SENT,
        )

        data = ReferralSerializer(referral).data

        expected_fields = {
            "id",
            "patient",
            "patient_username",
            "amr_record",
            "amr_risk_level",
            "referral_reason",
            "clinical_summary",
            "destination_name",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "referral_notes",
            "created_by",
            "created_at",
            "updated_at",
        }

        self.assertEqual(
            set(data.keys()),
            expected_fields,
        )

    def test_referral_serializer_returns_patient_username(self):
        referral = self.create_referral()

        data = ReferralSerializer(referral).data

        self.assertEqual(
            data["patient_username"],
            self.patient_user.username,
        )

    def test_referral_serializer_returns_amr_risk_level(self):
        referral = self.create_referral(
            amr_record=self.amr_record,
        )

        data = ReferralSerializer(referral).data

        self.assertEqual(
            data["amr_risk_level"],
            AMRRecord.RiskLevel.HIGH,
        )

    def test_referral_serializer_returns_display_values(self):
        referral = self.create_referral(
            priority=Referral.Priority.URGENT,
        )

        update_referral_status(
            referral,
            Referral.Status.ACCEPTED,
        )

        data = ReferralSerializer(referral).data

        self.assertEqual(
            data["priority_display"],
            "Urgent",
        )
        self.assertEqual(
            data["status_display"],
            "Accepted",
        )


class ReferralViewTests(ReferralTestBase):
    def login_as(self, username, password="TestPass123!"):
        self.client.login(
            username=username,
            password=password,
        )

    def test_create_page_requires_login(self):
        response = self.client.get(reverse("ReferralsApp:create"))

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_list_page_requires_login(self):
        response = self.client.get(reverse("ReferralsApp:list"))

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_detail_page_requires_login(self):
        response = self.client.get(
            reverse(
                "ReferralsApp:detail",
                kwargs={"referral_id": 1},
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_tracking_page_requires_login(self):
        response = self.client.get(reverse("ReferralsApp:tracking"))

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_patient_cannot_access_create_page(self):
        self.login_as(
            "patient_user",
        )

        response = self.client.get(reverse("ReferralsApp:create"))

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_patient_cannot_access_list_page(self):
        self.login_as(
            "patient_user",
        )

        response = self.client.get(reverse("ReferralsApp:list"))

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_clinician_can_access_create_page(self):
        self.login_staff()

        response = self.client.get(reverse("ReferralsApp:create"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_facility_staff_can_access_create_page(self):
        self.login_as(
            "facility_staff",
        )

        response = self.client.get(reverse("ReferralsApp:create"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_admin_can_access_create_page(self):
        self.login_as(
            "referral_admin",
        )

        response = self.client.get(reverse("ReferralsApp:create"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_create_referral_endpoint_requires_login(self):
        response = self.client.post(
            reverse("ReferralsApp:api_create"),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_create_referral_endpoint_rejects_get(self):
        self.login_staff()

        response = self.client.get(
            reverse("ReferralsApp:api_create"),
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_create_referral_endpoint(self):
        self.login_staff()

        response = self.client.post(
            reverse("ReferralsApp:api_create"),
            {
                "patient_id": self.patient.id,
                "amr_record_id": self.amr_record.id,
                "referral_reason": "Requires specialized AMR care.",
                "clinical_summary": "High-risk AMR assessment.",
                "destination_name": "Specialized Facility",
                "priority": "URGENT",
                "referral_notes": "Refer immediately.",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            Referral.objects.filter(
                patient=self.patient,
                amr_record=self.amr_record,
            ).exists()
        )

    def test_create_referral_endpoint_rejects_mismatched_amr_record(self):
        self.login_staff()

        other_screening = Screening.objects.create(
            patient=self.other_patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )

        other_amr_record = create_amr_record(
            patient=self.other_patient,
            screening=other_screening,
            created_by=self.staff_user,
        )

        response = self.client.post(
            reverse("ReferralsApp:api_create"),
            {
                "patient_id": self.patient.id,
                "amr_record_id": other_amr_record.id,
                "referral_reason": "Invalid relationship.",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_create_referral_endpoint_rejects_missing_reason(self):
        self.login_staff()

        response = self.client.post(
            reverse("ReferralsApp:api_create"),
            {
                "patient_id": self.patient.id,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_all_referrals_endpoint(self):
        self.create_referral()

        self.login_staff()

        response = self.client.get(reverse("ReferralsApp:api_records"))

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertIn(
            "referrals",
            response.json(),
        )
        self.assertEqual(
            len(response.json()["referrals"]),
            1,
        )

    def test_referral_detail_endpoint(self):
        referral = self.create_referral(
            amr_record=self.amr_record,
        )

        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_detail",
                kwargs={"referral_id": referral.id},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["id"],
            referral.id,
        )

    def test_update_referral_endpoint(self):
        referral = self.create_referral()

        self.login_staff()

        response = self.client.post(
            reverse(
                "ReferralsApp:api_update",
                kwargs={"referral_id": referral.id},
            ),
            {
                "referral_reason": "Updated reason.",
                "clinical_summary": "Updated summary.",
                "destination_name": "Updated Facility",
                "priority": "URGENT",
                "status": "SENT",
                "referral_notes": "Updated notes.",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        referral.refresh_from_db()

        self.assertEqual(
            referral.status,
            Referral.Status.SENT,
        )
        self.assertEqual(
            referral.priority,
            Referral.Priority.URGENT,
        )

    def test_update_referral_endpoint_rejects_get(self):
        referral = self.create_referral()

        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_update",
                kwargs={"referral_id": referral.id},
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_update_referral_status_endpoint(self):
        referral = self.create_referral()

        self.login_staff()

        response = self.client.post(
            reverse(
                "ReferralsApp:api_status",
                kwargs={"referral_id": referral.id},
            ),
            {
                "status": "ACCEPTED",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        referral.refresh_from_db()

        self.assertEqual(
            referral.status,
            Referral.Status.ACCEPTED,
        )

    def test_update_referral_status_endpoint_rejects_get(self):
        referral = self.create_referral()

        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_status",
                kwargs={"referral_id": referral.id},
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_patient_referrals_endpoint(self):
        self.create_referral()

        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_patient_records",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["patient_id"],
            self.patient.id,
        )
        self.assertEqual(
            len(response.json()["referrals"]),
            1,
        )

    def test_patient_cannot_access_referral_api(self):
        self.login_as(
            "patient_user",
        )

        response = self.client.get(reverse("ReferralsApp:api_records"))

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_nonexistent_referral_returns_404(self):
        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_detail",
                kwargs={"referral_id": 99999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nonexistent_patient_returns_404(self):
        self.login_staff()

        response = self.client.get(
            reverse(
                "ReferralsApp:api_patient_records",
                kwargs={"patient_id": 99999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
