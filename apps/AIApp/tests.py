from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening
from apps.ScreeningApp.services import (
    create_screening,
    save_screening_response,
    complete_screening,
)
from apps.AIApp.engines.explanation_engine import generate_explanation
from apps.AIApp.engines.screening_engine import analyze_screening_payload
from apps.AIApp.models import AIAnalysis
from apps.AIApp.serializers import serialize_ai_analysis
from apps.AIApp.services import build_screening_payload, create_ai_analysis
from apps.AIApp.validators import (
    validate_analysis_status,
    validate_analysis_text,
    validate_confidence,
    validate_risk_level,
)

User = get_user_model()


class AIAppTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ai_test_user",
            password="testpassword123",
            role=User.Role.ADMIN,
        )

        self.patient_user = User.objects.create_user(
            username="ai_test_patient",
            password="testpassword123",
            role=User.Role.PATIENT,
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(2000, 1, 1),
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Test Address",
            emergency_contact_name="Test Contact",
            emergency_contact_phone="0798765432",
        )

        self.screening = create_screening(
            patient=self.patient,
            created_by=self.user,
            screening_type=Screening.ScreeningType.INFECTIOUS,
            chief_complaint="Fever",
        )

        save_screening_response(
            screening=self.screening,
            question_code="FEVER_PRESENT",
            question="Is fever present?",
            response="YES",
            response_type="BOOLEAN",
        )

        complete_screening(self.screening)


class ScreeningPayloadTests(AIAppTestBase):
    def test_build_screening_payload(self):
        payload = build_screening_payload(self.screening)

        self.assertEqual(
            payload["screening"]["id"],
            self.screening.id,
        )
        self.assertEqual(
            payload["screening"]["type"],
            "INFECTIOUS",
        )
        self.assertEqual(
            payload["patient"]["sex"],
            "MALE",
        )
        self.assertEqual(
            len(payload["responses"]),
            1,
        )


class ScreeningEngineTests(TestCase):
    def test_analyze_screening_payload(self):
        payload = {
            "screening": {
                "type": "GENERAL",
                "chief_complaint": "Headache",
                "screening_notes": "",
            },
            "patient": {
                "id": 1,
                "sex": "MALE",
                "date_of_birth": "2000-01-01",
            },
            "responses": [
                {
                    "question_code": "HEADACHE",
                    "question": "Is headache present?",
                    "response": "YES",
                    "response_type": "BOOLEAN",
                }
            ],
        }

        result = analyze_screening_payload(payload)

        self.assertEqual(
            result["risk_level"],
            "LOW",
        )
        self.assertEqual(
            result["response_count"],
            1,
        )
        self.assertIn(
            "Headache",
            result["summary"],
        )


class ExplanationEngineTests(TestCase):
    def test_generate_explanation(self):
        result = {
            "summary": "One screening response recorded.",
            "risk_level": "LOW",
            "recommended_action": "review the screening information",
        }

        explanation = generate_explanation(result)

        self.assertIn(
            "low risk level",
            explanation,
        )
        self.assertIn(
            "clinician",
            explanation.lower(),
        )


class AIAnalysisServiceTests(AIAppTestBase):
    def test_create_ai_analysis(self):
        analysis = create_ai_analysis(self.screening)

        self.assertEqual(
            analysis.screening,
            self.screening,
        )
        self.assertEqual(
            analysis.status,
            AIAnalysis.Status.COMPLETED,
        )
        self.assertEqual(
            analysis.risk_level,
            "LOW",
        )
        self.assertEqual(
            analysis.provider,
            "internal",
        )
        self.assertEqual(
            analysis.model_name,
            "screening_engine",
        )


class SerializerTests(AIAppTestBase):
    def test_serialize_ai_analysis(self):
        analysis = create_ai_analysis(self.screening)

        data = serialize_ai_analysis(analysis)

        self.assertEqual(
            data["id"],
            analysis.id,
        )
        self.assertEqual(
            data["screening_id"],
            self.screening.id,
        )
        self.assertEqual(
            data["status"],
            "COMPLETED",
        )


class ValidatorTests(TestCase):
    def test_validate_risk_level(self):
        self.assertEqual(
            validate_risk_level("low"),
            "LOW",
        )

    def test_validate_analysis_status(self):
        self.assertEqual(
            validate_analysis_status("completed"),
            "COMPLETED",
        )

    def test_validate_analysis_text(self):
        self.assertEqual(
            validate_analysis_text(
                "Test summary",
                "Summary",
            ),
            "Test summary",
        )

    def test_validate_confidence(self):
        self.assertEqual(
            validate_confidence(85),
            85.0,
        )


class AIAnalysisViewTests(AIAppTestBase):
    def test_analyze_screening_view(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "AIApp:analyze",
                kwargs={
                    "screening_id": self.screening.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            AIAnalysis.objects.filter(
                screening=self.screening,
            ).count(),
            1,
        )
