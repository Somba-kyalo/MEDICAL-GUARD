from datetime import date
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening, ScreeningAssessment, ScreeningResponse

from apps.ScreeningApp.services import (
    ScreeningServiceError,
    complete_screening,
    create_or_update_assessment,
    create_screening,
    review_screening,
    save_screening_response,
    submit_for_review,
)
from apps.ScreeningApp.validators import (
    validate_question,
    validate_question_code,
    validate_response,
    validate_response_type,
    validate_risk_level,
    validate_screening_type,
)


class ScreeningTestMixin:

    def create_user(self, username, role):
        return User.objects.create_user(
            username=username,
            password="TestPassword123!",
            role=role,
        )

    def create_patient(self, username="patient"):
        user = self.create_user(
            username,
            User.Role.PATIENT,
        )

        return Patient.objects.create(
            user=user,
            date_of_birth=date(2000, 1, 1),
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Voi",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0798765432",
        )


class ScreeningModelTests(ScreeningTestMixin, TestCase):

    def test_screening_is_created_with_started_status(self):
        patient = self.create_patient()
        clinician = self.create_user(
            "clinician",
            User.Role.CLINICIAN,
        )

        screening = Screening.objects.create(
            patient=patient,
            created_by=clinician,
        )

        self.assertEqual(
            screening.status,
            Screening.Status.STARTED,
        )

    def test_screening_response_is_related_to_screening(self):
        patient = self.create_patient()
        clinician = self.create_user(
            "clinician",
            User.Role.CLINICIAN,
        )

        screening = Screening.objects.create(
            patient=patient,
            created_by=clinician,
        )

        response = ScreeningResponse.objects.create(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
            response_type=ScreeningResponse.ResponseType.BOOLEAN,
        )

        self.assertEqual(
            screening.responses.count(),
            1,
        )
        self.assertEqual(
            response.screening,
            screening,
        )

    def test_screening_assessment_is_one_to_one_with_screening(self):
        patient = self.create_patient()
        clinician = self.create_user(
            "clinician",
            User.Role.CLINICIAN,
        )

        screening = Screening.objects.create(
            patient=patient,
            created_by=clinician,
        )

        assessment = ScreeningAssessment.objects.create(
            screening=screening,
            risk_level=ScreeningAssessment.RiskLevel.MODERATE,
        )

        self.assertEqual(
            screening.assessment,
            assessment,
        )


class ScreeningServiceTests(ScreeningTestMixin, TestCase):

    def setUp(self):
        self.patient = self.create_patient()
        self.clinician = self.create_user(
            "clinician",
            User.Role.CLINICIAN,
        )

    def test_create_screening_starts_screening(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
            screening_type=Screening.ScreeningType.GENERAL,
            chief_complaint="Fever",
        )

        self.assertEqual(
            screening.status,
            Screening.Status.STARTED,
        )
        self.assertEqual(
            screening.patient,
            self.patient,
        )
        self.assertEqual(
            screening.created_by,
            self.clinician,
        )

    def test_save_response_moves_screening_to_in_progress(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        response = save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
            response_type=ScreeningResponse.ResponseType.BOOLEAN,
        )

        screening.refresh_from_db()

        self.assertEqual(
            screening.status,
            Screening.Status.IN_PROGRESS,
        )
        self.assertEqual(
            response.response,
            "Yes",
        )

    def test_save_response_updates_existing_question(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="No",
        )

        self.assertEqual(
            screening.responses.count(),
            1,
        )
        self.assertEqual(
            screening.responses.first().response,
            "No",
        )

    def test_cannot_save_response_after_completion(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)

        with self.assertRaises(ScreeningServiceError):
            save_screening_response(
                screening=screening,
                question_code="COUGH",
                question="Do you have a cough?",
                response="Yes",
            )

    def test_complete_screening(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)
        screening.refresh_from_db()

        self.assertEqual(
            screening.status,
            Screening.Status.COMPLETED,
        )
        self.assertIsNotNone(
            screening.completed_at,
        )

    def test_cannot_complete_started_screening(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        with self.assertRaises(ScreeningServiceError):
            complete_screening(screening)

    def test_submit_completed_screening_for_review(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)
        submit_for_review(screening)
        screening.refresh_from_db()

        self.assertEqual(
            screening.status,
            Screening.Status.UNDER_REVIEW,
        )

    def test_cannot_submit_incomplete_screening_for_review(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        with self.assertRaises(ScreeningServiceError):
            submit_for_review(screening)

    def test_create_or_update_assessment(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)

        assessment = create_or_update_assessment(
            screening=screening,
            summary="Patient reports fever.",
            risk_level=ScreeningAssessment.RiskLevel.MODERATE,
            recommended_action="Clinical review required.",
        )

        self.assertEqual(
            assessment.risk_level,
            ScreeningAssessment.RiskLevel.MODERATE,
        )
        self.assertEqual(
            assessment.summary,
            "Patient reports fever.",
        )

    def test_review_screening_changes_status_to_reviewed(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)
        submit_for_review(screening)

        reviewed_screening, assessment = review_screening(
            screening=screening,
            reviewed_by=self.clinician,
            summary="Reviewed clinical information.",
            risk_level=ScreeningAssessment.RiskLevel.LOW,
            recommended_action="Routine follow-up.",
            clinician_notes="No urgent concerns.",
        )

        self.assertEqual(
            reviewed_screening.status,
            Screening.Status.REVIEWED,
        )
        self.assertEqual(
            reviewed_screening.reviewed_by,
            self.clinician,
        )
        self.assertIsNotNone(
            reviewed_screening.reviewed_at,
        )
        self.assertEqual(
            assessment.risk_level,
            ScreeningAssessment.RiskLevel.LOW,
        )

    def test_cannot_review_screening_not_under_review(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        with self.assertRaises(ScreeningServiceError):
            review_screening(
                screening=screening,
                reviewed_by=self.clinician,
            )


class ScreeningValidatorTests(TestCase):

    def test_valid_screening_type(self):
        value = validate_screening_type(
            Screening.ScreeningType.GENERAL,
        )

        self.assertEqual(
            value,
            Screening.ScreeningType.GENERAL,
        )

    def test_invalid_screening_type(self):
        with self.assertRaises(ValidationError):
            validate_screening_type("INVALID")

    def test_valid_response_type(self):
        value = validate_response_type(
            ScreeningResponse.ResponseType.TEXT,
        )

        self.assertEqual(
            value,
            ScreeningResponse.ResponseType.TEXT,
        )

    def test_invalid_response_type(self):
        with self.assertRaises(ValidationError):
            validate_response_type("INVALID")

    def test_valid_risk_level(self):
        value = validate_risk_level(
            ScreeningAssessment.RiskLevel.HIGH,
        )

        self.assertEqual(
            value,
            ScreeningAssessment.RiskLevel.HIGH,
        )

    def test_invalid_risk_level(self):
        with self.assertRaises(ValidationError):
            validate_risk_level("INVALID")

    def test_question_code_is_required(self):
        with self.assertRaises(ValidationError):
            validate_question_code("")

    def test_question_code_is_trimmed(self):
        value = validate_question_code("  FEVER  ")

        self.assertEqual(
            value,
            "FEVER",
        )

    def test_question_is_required(self):
        with self.assertRaises(ValidationError):
            validate_question("")

    def test_question_is_trimmed(self):
        value = validate_question("  Do you have a fever?  ")

        self.assertEqual(
            value,
            "Do you have a fever?",
        )

    def test_boolean_response_accepts_yes(self):
        value = validate_response(
            "Yes",
            ScreeningResponse.ResponseType.BOOLEAN,
        )

        self.assertEqual(
            value,
            "Yes",
        )

    def test_boolean_response_rejects_invalid_value(self):
        with self.assertRaises(ValidationError):
            validate_response(
                "Maybe",
                ScreeningResponse.ResponseType.BOOLEAN,
            )

    def test_number_response_accepts_number(self):
        value = validate_response(
            "37.5",
            ScreeningResponse.ResponseType.NUMBER,
        )

        self.assertEqual(
            value,
            "37.5",
        )

    def test_number_response_rejects_invalid_value(self):
        with self.assertRaises(ValidationError):
            validate_response(
                "abc",
                ScreeningResponse.ResponseType.NUMBER,
            )


class ScreeningViewTests(ScreeningTestMixin, TestCase):

    def setUp(self):
        self.patient = self.create_patient()
        self.patient_user = self.patient.user

        self.clinician = self.create_user(
            "clinician",
            User.Role.CLINICIAN,
        )

        self.facility_staff = self.create_user(
            "facility_staff",
            User.Role.FACILITY_STAFF,
        )

    def test_patient_cannot_start_screening(self):
        self.client.force_login(self.patient_user)

        response = self.client.get(
            reverse("ScreeningApp:start"),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_clinician_can_open_start_screening(self):
        self.client.force_login(self.clinician)

        response = self.client.get(
            reverse("ScreeningApp:start"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_patient_can_view_own_screening(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        self.client.force_login(self.patient_user)

        response = self.client.get(
            reverse(
                "ScreeningApp:detail",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_patient_cannot_view_another_patient_screening(self):
        other_patient = self.create_patient("other_patient")

        screening = create_screening(
            patient=other_patient,
            created_by=self.clinician,
        )

        self.client.force_login(self.patient_user)

        response = self.client.get(
            reverse(
                "ScreeningApp:detail",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_clinician_can_view_screening_detail(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        self.client.force_login(self.clinician)

        response = self.client.get(
            reverse(
                "ScreeningApp:detail",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_patient_cannot_open_screening_form(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        self.client.force_login(self.patient_user)

        response = self.client.get(
            reverse(
                "ScreeningApp:form",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_clinician_can_open_screening_form(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        self.client.force_login(self.clinician)

        response = self.client.get(
            reverse(
                "ScreeningApp:form",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_facility_staff_can_review_screening(self):
        screening = create_screening(
            patient=self.patient,
            created_by=self.clinician,
        )

        save_screening_response(
            screening=screening,
            question_code="FEVER",
            question="Do you have a fever?",
            response="Yes",
        )

        complete_screening(screening)
        submit_for_review(screening)

        self.client.force_login(self.facility_staff)

        response = self.client.get(
            reverse(
                "ScreeningApp:review",
                args=[screening.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.context["screening"],
            screening,
        )
