from django.test import TestCase

from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening
from apps.AmrApp.models import AMRRecord, Antibiotic, Organism, ResistanceTest
from apps.AmrApp.rules import (
    is_resistant,
    validate_resistance_result,
    validate_risk_level,
)
from apps.AmrApp.serializers import (
    AMRRecordSerializer,
    AntibioticSerializer,
    OrganismSerializer,
)
from apps.AmrApp.services import (
    add_resistance_test,
    create_amr_record,
    update_amr_record,
)


class AMRServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="amr_test_user", password="testpass123", role=User.Role.CLINICIAN
        )
        self.patient_user = User.objects.create_user(
            username="amr_patient", password="testpass123"
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth="2000-01-01",
            sex=Patient.Sex.MALE,
            phone_number="0712345678",
            address="Voi",
            emergency_contact_name="Test Contact",
            emergency_contact_phone="0798765432",
        )
        self.screening = Screening.objects.create(
            patient=self.patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=self.user,
        )
        self.organism = Organism.objects.create(name="Escherichia coli", code="ECOLI")
        self.antibiotic = Antibiotic.objects.create(name="Amoxicillin", code="AMX")

    def test_create_amr_record(self):
        record = create_amr_record(
            patient=self.patient,
            screening=self.screening,
            created_by=self.user,
            risk_level="HIGH",
        )
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(record.screening, self.screening)
        self.assertEqual(record.risk_level, "HIGH")
        self.assertEqual(record.status, AMRRecord.Status.OPEN)

    def test_create_amr_record_rejects_wrong_patient(self):
        other_user = User.objects.create_user(
            username="other_patient", password="testpass123"
        )
        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth="1999-01-01",
            sex=Patient.Sex.FEMALE,
            phone_number="0700000000",
            address="Voi",
            emergency_contact_name="Contact",
            emergency_contact_phone="0700000001",
        )

        with self.assertRaises(Exception):
            create_amr_record(
                patient=other_patient, screening=self.screening, created_by=self.user
            )

    def test_update_amr_record(self):
        record = create_amr_record(
            patient=self.patient, screening=self.screening, created_by=self.user
        )
        updated_record = update_amr_record(
            record,
            exposure_history="Previous antibiotic exposure",
            infection_information="Suspected bacterial infection",
            risk_level="MODERATE",
            clinical_notes="Requires clinician review",
            status=AMRRecord.Status.UNDER_REVIEW,
        )
        self.assertEqual(
            updated_record.exposure_history, "Previous antibiotic exposure"
        )
        self.assertEqual(updated_record.risk_level, "MODERATE")
        self.assertEqual(updated_record.status, AMRRecord.Status.UNDER_REVIEW)

    def test_add_resistance_test(self):
        record = create_amr_record(
            patient=self.patient, screening=self.screening, created_by=self.user
        )
        resistance_test = add_resistance_test(
            amr_record=record,
            organism=self.organism,
            antibiotic=self.antibiotic,
            result="RESISTANT",
            test_notes="Laboratory result",
        )
        self.assertEqual(resistance_test.amr_record, record)
        self.assertEqual(resistance_test.organism, self.organism)
        self.assertEqual(resistance_test.antibiotic, self.antibiotic)
        self.assertEqual(resistance_test.result, ResistanceTest.Result.RESISTANT)

    def test_resistance_rules(self):
        self.assertEqual(validate_risk_level("high"), "HIGH")
        self.assertEqual(validate_resistance_result("resistant"), "RESISTANT")
        self.assertTrue(is_resistant("RESISTANT"))
        self.assertFalse(is_resistant("SUSCEPTIBLE"))


class AMRSerializerTests(TestCase):
    def test_organism_serializer(self):
        organism = Organism(name="Escherichia coli", code="ECOLI")
        data = OrganismSerializer(organism).data
        self.assertEqual(data["name"], "Escherichia coli")
        self.assertEqual(data["code"], "ECOLI")

    def test_antibiotic_serializer(self):
        antibiotic = Antibiotic(
            name="Amoxicillin", code="AMX", antibiotic_class="Penicillin"
        )
        data = AntibioticSerializer(antibiotic).data
        self.assertEqual(data["name"], "Amoxicillin")
        self.assertEqual(data["code"], "AMX")
        self.assertEqual(data["antibiotic_class"], "Penicillin")

    def test_amr_record_serializer(self):
        user = User.objects.create_user(
            username="serializer_user", password="testpass123"
        )
        patient_user = User.objects.create_user(
            username="serializer_patient", password="testpass123"
        )
        patient = Patient.objects.create(
            user=patient_user,
            date_of_birth="2000-01-01",
            sex=Patient.Sex.MALE,
            phone_number="0711111111",
            address="Voi",
            emergency_contact_name="Contact",
            emergency_contact_phone="0722222222",
        )
        screening = Screening.objects.create(
            patient=patient,
            screening_type=Screening.ScreeningType.AMR,
            status=Screening.Status.COMPLETED,
            created_by=user,
        )
        record = AMRRecord.objects.create(
            patient=patient, screening=screening, created_by=user
        )
        data = AMRRecordSerializer(record).data
        self.assertEqual(data["patient"], patient.id)
        self.assertEqual(data["screening"], screening.id)
        self.assertEqual(data["status"], AMRRecord.Status.OPEN)
