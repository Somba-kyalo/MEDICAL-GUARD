from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.AIApp.models import AIAnalysis
from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening

from apps.AmrApp.models import AMRRecord, Antibiotic, Organism, ResistanceTest
from apps.AmrApp.serializers import (
    AMRRecordSerializer,
    AntibioticSerializer,
    OrganismSerializer,
    ResistanceTestSerializer,
)
from apps.AmrApp.services import (
    add_resistance_test,
    create_amr_record,
    get_amr_record,
    get_patient_amr_records,
    update_amr_record,
)


class AMRTestBase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="clinician", password="testpass123", role=User.Role.CLINICIAN)
        self.facility_staff = User.objects.create_user(username="facilitystaff", password="testpass123", role=User.Role.FACILITY_STAFF)
        self.admin_user = User.objects.create_user(username="admin", password="testpass123", role=User.Role.ADMIN)
        self.patient_user = User.objects.create_user(username="patient", password="testpass123", role=User.Role.PATIENT)
        self.other_patient_user = User.objects.create_user(username="otherpatient", password="testpass123", role=User.Role.PATIENT)

        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth=date(2000, 1, 1),
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Voi, Taita Taveta",
            emergency_contact_name="John Doe",
            emergency_contact_phone="0722345678",
        )

        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            date_of_birth=date(1999, 1, 1),
            sex=Patient.Sex.FEMALE,
            phone_number="0712345679",
            address="Mombasa, Kenya",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="0722345679",
        )

        self.screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )

        self.organism = Organism.objects.create(
            name="Escherichia coli",
            code="ECOLI",
            description="Common bacterial organism.",
        )

        self.antibiotic = Antibiotic.objects.create(
            name="Amoxicillin",
            code="AMX",
            antibiotic_class="Penicillin",
        )

    def create_record(self, **kwargs):
        defaults = {
            "patient": self.patient,
            "screening": self.screening,
            "created_by": self.staff_user,
        }
        defaults.update(kwargs)
        return create_amr_record(**defaults)

    def login_staff(self):
        self.client.login(username="clinician", password="testpass123")


class AMRServiceTests(AMRTestBase):
    def test_create_amr_record(self):
        record = self.create_record(
            exposure_history="Previous antibiotic exposure",
            infection_information="Suspected bacterial infection",
            risk_level="high",
            clinical_notes="Requires clinical review",
        )
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(record.screening, self.screening)
        self.assertEqual(record.created_by, self.staff_user)
        self.assertEqual(record.risk_level, AMRRecord.RiskLevel.HIGH)
        self.assertEqual(record.status, AMRRecord.Status.OPEN)

    def test_create_amr_record_defaults_to_open_status(self):
        record = self.create_record()
        self.assertEqual(record.status, AMRRecord.Status.OPEN)

    def test_create_amr_record_without_optional_fields(self):
        record = self.create_record()
        self.assertEqual(record.exposure_history, "")
        self.assertEqual(record.infection_information, "")
        self.assertEqual(record.risk_level, "")
        self.assertEqual(record.clinical_notes, "")

    def test_create_amr_record_normalizes_risk_level(self):
        record = self.create_record(risk_level="  high  ")
        self.assertEqual(record.risk_level, AMRRecord.RiskLevel.HIGH)

    def test_create_amr_record_rejects_invalid_risk_level(self):
        with self.assertRaises(ValidationError):
            self.create_record(risk_level="INVALID")

    def test_create_amr_record_rejects_wrong_patient(self):
        with self.assertRaises(ValidationError):
            create_amr_record(patient=self.other_patient, screening=self.screening, created_by=self.staff_user)

    def test_create_amr_record_rejects_non_amr_screening(self):
        screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.GENERAL,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )
        with self.assertRaises(ValidationError):
            create_amr_record(patient=self.patient, screening=screening, created_by=self.staff_user)

    def test_create_amr_record_rejects_ai_analysis_from_different_screening(self):
        other_screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )
        ai_analysis = AIAnalysis.objects.create(screening=other_screening)
        with self.assertRaises(ValidationError):
            create_amr_record(patient=self.patient, screening=self.screening, created_by=self.staff_user, ai_analysis=ai_analysis)

    def test_create_amr_record_accepts_matching_ai_analysis(self):
        ai_analysis = AIAnalysis.objects.create(
            screening=self.screening,
            summary="AMR screening analysis",
            risk_level=AIAnalysis.RiskLevel.HIGH,
            recommended_action="Clinical review required",
            status=AIAnalysis.Status.COMPLETED,
        )
        record = self.create_record(ai_analysis=ai_analysis)
        self.assertEqual(record.ai_analysis, ai_analysis)

    def test_update_amr_record(self):
        record = self.create_record()
        updated_record = update_amr_record(
            amr_record=record,
            exposure_history="Previous antibiotic exposure",
            infection_information="Suspected bacterial infection",
            risk_level="moderate",
            clinical_notes="Monitor patient",
            status="UNDER_REVIEW",
        )
        self.assertEqual(updated_record.exposure_history, "Previous antibiotic exposure")
        self.assertEqual(updated_record.infection_information, "Suspected bacterial infection")
        self.assertEqual(updated_record.risk_level, AMRRecord.RiskLevel.MODERATE)
        self.assertEqual(updated_record.clinical_notes, "Monitor patient")
        self.assertEqual(updated_record.status, AMRRecord.Status.UNDER_REVIEW)

    def test_update_amr_record_normalizes_values(self):
        record = self.create_record()
        updated_record = update_amr_record(amr_record=record, risk_level="  high  ", status="  reviewed  ")
        self.assertEqual(updated_record.risk_level, AMRRecord.RiskLevel.HIGH)
        self.assertEqual(updated_record.status, AMRRecord.Status.REVIEWED)

    def test_update_amr_record_rejects_invalid_risk_level(self):
        record = self.create_record()
        with self.assertRaises(ValidationError):
            update_amr_record(amr_record=record, risk_level="INVALID")

    def test_update_amr_record_rejects_invalid_status(self):
        record = self.create_record()
        with self.assertRaises(ValidationError):
            update_amr_record(amr_record=record, status="INVALID")

    def test_update_amr_record_allows_partial_update(self):
        record = self.create_record(exposure_history="Original history", risk_level="low")
        updated_record = update_amr_record(amr_record=record, clinical_notes="New clinical note")
        self.assertEqual(updated_record.exposure_history, "Original history")
        self.assertEqual(updated_record.risk_level, AMRRecord.RiskLevel.LOW)
        self.assertEqual(updated_record.clinical_notes, "New clinical note")

    def test_add_resistance_test(self):
        record = self.create_record()
        resistance_test = add_resistance_test(
            amr_record=record,
            organism=self.organism,
            antibiotic=self.antibiotic,
            result="resistant",
            test_notes="Laboratory confirmed resistance",
        )
        self.assertEqual(resistance_test.amr_record, record)
        self.assertEqual(resistance_test.organism, self.organism)
        self.assertEqual(resistance_test.antibiotic, self.antibiotic)
        self.assertEqual(resistance_test.result, ResistanceTest.Result.RESISTANT)

    def test_add_resistance_test_normalizes_result(self):
        record = self.create_record()
        resistance_test = add_resistance_test(
            amr_record=record,
            organism=self.organism,
            antibiotic=self.antibiotic,
            result="  resistant  ",
        )
        self.assertEqual(resistance_test.result, ResistanceTest.Result.RESISTANT)

    def test_add_resistance_test_rejects_missing_record(self):
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=None, organism=self.organism, antibiotic=self.antibiotic, result="resistant")

    def test_add_resistance_test_rejects_missing_organism(self):
        record = self.create_record()
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=record, organism=None, antibiotic=self.antibiotic, result="resistant")

    def test_add_resistance_test_rejects_missing_antibiotic(self):
        record = self.create_record()
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=record, organism=self.organism, antibiotic=None, result="resistant")

    def test_add_resistance_test_rejects_inactive_organism(self):
        record = self.create_record()
        self.organism.is_active = False
        self.organism.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=record, organism=self.organism, antibiotic=self.antibiotic, result="resistant")

    def test_add_resistance_test_rejects_inactive_antibiotic(self):
        record = self.create_record()
        self.antibiotic.is_active = False
        self.antibiotic.save(update_fields=["is_active"])
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=record, organism=self.organism, antibiotic=self.antibiotic, result="resistant")

    def test_add_resistance_test_rejects_invalid_result(self):
        record = self.create_record()
        with self.assertRaises(ValidationError):
            add_resistance_test(amr_record=record, organism=self.organism, antibiotic=self.antibiotic, result="INVALID")

    def test_get_amr_record(self):
        record = self.create_record()
        retrieved_record = get_amr_record(record.id)
        self.assertEqual(retrieved_record.id, record.id)
        self.assertEqual(retrieved_record.patient, self.patient)
        self.assertEqual(retrieved_record.screening, self.screening)

    def test_get_amr_record_includes_related_resistance_tests(self):
        record = self.create_record()
        add_resistance_test(amr_record=record, organism=self.organism, antibiotic=self.antibiotic, result="resistant")
        retrieved_record = get_amr_record(record.id)
        self.assertEqual(retrieved_record.resistance_tests.count(), 1)

    def test_get_patient_amr_records(self):
        self.create_record()
        records = get_patient_amr_records(self.patient)
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first().patient, self.patient)

    def test_get_patient_amr_records_does_not_return_other_patient_records(self):
        self.create_record()
        other_screening = Screening.objects.create(
            patient=self.other_patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.staff_user,
        )
        create_amr_record(patient=self.other_patient, screening=other_screening, created_by=self.staff_user)
        records = get_patient_amr_records(self.patient)
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first().patient, self.patient)


class AMRSerializerTests(AMRTestBase):
    def setUp(self):
        super().setUp()
        self.record = self.create_record(risk_level="high")
        self.resistance_test = add_resistance_test(
            amr_record=self.record,
            organism=self.organism,
            antibiotic=self.antibiotic,
            result="resistant",
            test_notes="Laboratory confirmed resistance",
        )

    def test_amr_record_serializer(self):
        serializer = AMRRecordSerializer(self.record)
        self.assertEqual(serializer.data["id"], self.record.id)
        self.assertEqual(serializer.data["patient"], self.patient.id)
        self.assertEqual(serializer.data["patient_username"], self.patient_user.username)
        self.assertEqual(serializer.data["screening"], self.screening.id)
        self.assertEqual(serializer.data["screening_type"], "Antimicrobial Resistance")
        self.assertEqual(serializer.data["risk_level"], AMRRecord.RiskLevel.HIGH)
        self.assertEqual(serializer.data["risk_level_display"], "High")
        self.assertEqual(serializer.data["status"], AMRRecord.Status.OPEN)
        self.assertEqual(serializer.data["status_display"], "Open")

    def test_amr_record_serializer_includes_resistance_tests(self):
        serializer = AMRRecordSerializer(self.record)
        self.assertEqual(len(serializer.data["resistance_tests"]), 1)
        self.assertEqual(serializer.data["resistance_tests"][0]["result"], ResistanceTest.Result.RESISTANT)

    def test_organism_serializer(self):
        serializer = OrganismSerializer(self.organism)
        self.assertEqual(serializer.data["name"], "Escherichia coli")
        self.assertEqual(serializer.data["code"], "ECOLI")
        self.assertEqual(serializer.data["description"], "Common bacterial organism.")
        self.assertTrue(serializer.data["is_active"])

    def test_antibiotic_serializer(self):
        serializer = AntibioticSerializer(self.antibiotic)
        self.assertEqual(serializer.data["name"], "Amoxicillin")
        self.assertEqual(serializer.data["code"], "AMX")
        self.assertEqual(serializer.data["antibiotic_class"], "Penicillin")
        self.assertTrue(serializer.data["is_active"])

    def test_resistance_test_serializer(self):
        serializer = ResistanceTestSerializer(self.resistance_test)
        self.assertEqual(serializer.data["result"], ResistanceTest.Result.RESISTANT)
        self.assertEqual(serializer.data["result_display"], "Resistant")
        self.assertEqual(serializer.data["organism_name"], "Escherichia coli")
        self.assertEqual(serializer.data["antibiotic_name"], "Amoxicillin")
        self.assertEqual(serializer.data["amr_record"], self.record.id)


class AMRViewTests(AMRTestBase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("AmrApp:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_assessment_requires_login(self):
        response = self.client.get(reverse("AmrApp:assessment"))
        self.assertEqual(response.status_code, 302)

    def test_result_requires_login(self):
        response = self.client.get(reverse("AmrApp:result"))
        self.assertEqual(response.status_code, 302)

    def test_surveillance_requires_login(self):
        response = self.client.get(reverse("AmrApp:surveillance"))
        self.assertEqual(response.status_code, 302)

    def test_patient_cannot_access_amr_services(self):
        self.client.login(username="patient", password="testpass123")
        response = self.client.get(reverse("AmrApp:records"))
        self.assertEqual(response.status_code, 403)

    def test_clinician_can_access_dashboard(self):
        self.login_staff()
        response = self.client.get(reverse("AmrApp:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_clinician_can_access_assessment(self):
        self.login_staff()
        response = self.client.get(reverse("AmrApp:assessment"))
        self.assertEqual(response.status_code, 200)

    def test_clinician_can_access_result(self):
        self.login_staff()
        response = self.client.get(reverse("AmrApp:result"))
        self.assertEqual(response.status_code, 200)

    def test_clinician_can_access_surveillance(self):
        self.login_staff()
        response = self.client.get(reverse("AmrApp:surveillance"))
        self.assertEqual(response.status_code, 200)

    def test_create_amr_requires_login(self):
        response = self.client.get(reverse("AmrApp:create", args=[self.screening.id]))
        self.assertEqual(response.status_code, 302)

    def test_create_amr_requires_completed_screening(self):
        self.login_staff()
        self.screening.status = Screening.Status.IN_PROGRESS
        self.screening.save(update_fields=["status"])
        response = self.client.get(reverse("AmrApp:create", args=[self.screening.id]))
        self.assertEqual(response.status_code, 400)
        self.assertIn("completed screening", response.json()["error"])

    def test_create_amr_creates_record(self):
        self.login_staff()
        response = self.client.get(reverse("AmrApp:create", args=[self.screening.id]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["patient"], self.patient.id)
        self.assertEqual(AMRRecord.objects.count(), 1)

    def test_create_amr_rejects_non_amr_screening(self):
        self.login_staff()
        self.screening.screening_type = Screening.ScreeningType.GENERAL
        self.screening.save(update_fields=["screening_type"])
        response = self.client.get(reverse("AmrApp:create", args=[self.screening.id]))
        self.assertEqual(response.status_code, 400)

    def test_amr_detail_returns_record(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:detail", args=[record.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], record.id)

    def test_amr_detail_requires_login(self):
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:detail", args=[record.id]))
        self.assertEqual(response.status_code, 302)

    def test_all_amr_records_returns_records(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:records"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["records"]), 1)
        self.assertEqual(response.json()["records"][0]["id"], record.id)

    def test_patient_amr_records_returns_patient_records(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:patient_records", args=[self.patient.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["patient_id"], self.patient.id)
        self.assertEqual(len(response.json()["records"]), 1)
        self.assertEqual(response.json()["records"][0]["id"], record.id)

    def test_update_amr_updates_record(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.post(
            reverse("AmrApp:update", args=[record.id]),
            {
                "exposure_history": "Updated exposure history",
                "infection_information": "Updated infection information",
                "risk_level": "HIGH",
                "clinical_notes": "Updated clinical notes",
                "status": "UNDER_REVIEW",
            },
        )
        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertEqual(record.exposure_history, "Updated exposure history")
        self.assertEqual(record.infection_information, "Updated infection information")
        self.assertEqual(record.risk_level, AMRRecord.RiskLevel.HIGH)
        self.assertEqual(record.clinical_notes, "Updated clinical notes")
        self.assertEqual(record.status, AMRRecord.Status.UNDER_REVIEW)

    def test_update_amr_rejects_get_request(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:update", args=[record.id]))
        self.assertEqual(response.status_code, 405)

    def test_update_amr_rejects_invalid_risk_level(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.post(
            reverse("AmrApp:update", args=[record.id]),
            {"risk_level": "INVALID"},
        )
        self.assertEqual(response.status_code, 400)

    def test_add_resistance_test_view_creates_test(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.post(
            reverse("AmrApp:add_resistance_test", args=[record.id]),
            {
                "organism_id": self.organism.id,
                "antibiotic_id": self.antibiotic.id,
                "result": "RESISTANT",
                "test_notes": "Laboratory confirmed resistance",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["result"], ResistanceTest.Result.RESISTANT)
        self.assertEqual(ResistanceTest.objects.count(), 1)

    def test_add_resistance_test_view_rejects_get_request(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.get(reverse("AmrApp:add_resistance_test", args=[record.id]))
        self.assertEqual(response.status_code, 405)

    def test_add_resistance_test_view_rejects_invalid_result(self):
        self.login_staff()
        record = self.create_record()
        response = self.client.post(
            reverse("AmrApp:add_resistance_test", args=[record.id]),
            {
                "organism_id": self.organism.id,
                "antibiotic_id": self.antibiotic.id,
                "result": "INVALID",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_organisms_returns_active_organisms(self):
        self.login_staff()
        inactive_organism = Organism.objects.create(name="Inactive organism", code="INACTIVE", is_active=False)
        response = self.client.get(reverse("AmrApp:organisms"))
        self.assertEqual(response.status_code, 200)
        organism_ids = [organism["id"] for organism in response.json()["organisms"]]
        self.assertIn(self.organism.id, organism_ids)
        self.assertNotIn(inactive_organism.id, organism_ids)

    def test_antibiotics_returns_active_antibiotics(self):
        self.login_staff()
        inactive_antibiotic = Antibiotic.objects.create(name="Inactive antibiotic", code="INACTIVE", is_active=False)
        response = self.client.get(reverse("AmrApp:antibiotics"))
        self.assertEqual(response.status_code, 200)
        antibiotic_ids = [antibiotic["id"] for antibiotic in response.json()["antibiotics"]]
        self.assertIn(self.antibiotic.id, antibiotic_ids)
        self.assertNotIn(inactive_antibiotic.id, antibiotic_ids)

    def test_facility_staff_can_access_amr_records(self):
        self.client.login(username="facilitystaff", password="testpass123")
        response = self.client.get(reverse("AmrApp:records"))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_amr_records(self):
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("AmrApp:records"))
        self.assertEqual(response.status_code, 200)