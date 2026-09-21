from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient


class PatientsAppTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="patientone",
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            password="StrongPassword123",
            role=User.Role.PATIENT,
        )

        self.patient = Patient.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 15),
            sex=Patient.Sex.MALE,
            phone_number="+254700000000",
            address="Voi, Kenya",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+254711111111",
        )

        self.other_patient_user = User.objects.create_user(
            username="patienttwo",
            email="patienttwo@example.com",
            first_name="Mary",
            last_name="Doe",
            password="StrongPassword123",
            role=User.Role.PATIENT,
        )

        self.other_patient = Patient.objects.create(
            user=self.other_patient_user,
            date_of_birth=date(1998, 5, 20),
            sex=Patient.Sex.FEMALE,
            phone_number="+254722222222",
            address="Nairobi, Kenya",
            emergency_contact_name="John Doe",
            emergency_contact_phone="+254733333333",
        )

        self.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="StrongPassword123",
            role=User.Role.CLINICIAN,
        )

    def test_patient_model_string_representation(self):
        self.assertEqual(str(self.patient), "patientone")

    def test_patient_list_requires_login(self):
        response = self.client.get(reverse("PatientsApp:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_detail_requires_login(self):
        response = self.client.get(
            reverse(
                "PatientsApp:detail",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_create_requires_login(self):
        response = self.client.get(reverse("PatientsApp:create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_edit_requires_login(self):
        response = self.client.get(
            reverse(
                "PatientsApp:edit",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_timeline_requires_login(self):
        response = self.client.get(
            reverse(
                "PatientsApp:timeline",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_list_authenticated(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("PatientsApp:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "PatientsApp/list.html",
        )
        self.assertContains(response, "patientone")
        self.assertContains(response, "patienttwo")

    def test_patient_detail_authenticated(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse(
                "PatientsApp:detail",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "PatientsApp/detail.html",
        )
        self.assertContains(response, "patientone")
        self.assertContains(response, "John")
        self.assertContains(response, "Doe")

    def test_patient_create_successfully(self):
        self.client.force_login(self.staff_user)

        new_user = User.objects.create_user(
            username="patientthree",
            email="patientthree@example.com",
            first_name="Kevin",
            last_name="Smith",
            password="StrongPassword123",
            role=User.Role.PATIENT,
        )

        response = self.client.post(
            reverse("PatientsApp:create"),
            {
                "username": new_user.username,
                "date_of_birth": "2002-03-10",
                "sex": Patient.Sex.MALE,
                "phone_number": "+254744444444",
                "address": "Mombasa, Kenya",
                "emergency_contact_name": "Sarah Smith",
                "emergency_contact_phone": "+254755555555",
            },
        )

        self.assertEqual(response.status_code, 302)

        created_patient = Patient.objects.get(user=new_user)

        self.assertRedirects(
            response,
            reverse(
                "PatientsApp:detail",
                kwargs={"patient_id": created_patient.id},
            ),
        )

        self.assertEqual(
            created_patient.date_of_birth,
            date(2002, 3, 10),
        )

    def test_patient_create_rejects_missing_username(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("PatientsApp:create"),
            {
                "username": "",
                "date_of_birth": "2002-03-10",
                "sex": Patient.Sex.MALE,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertContains(
            response,
            "Username is required.",
        )

    def test_patient_create_rejects_invalid_sex(self):
        self.client.force_login(self.staff_user)

        new_user = User.objects.create_user(
            username="patientthree",
            password="StrongPassword123",
            role=User.Role.PATIENT,
        )

        response = self.client.post(
            reverse("PatientsApp:create"),
            {
                "username": new_user.username,
                "date_of_birth": "2002-03-10",
                "sex": "INVALID",
                "phone_number": "+254744444444",
                "address": "Mombasa, Kenya",
                "emergency_contact_name": "Sarah Smith",
                "emergency_contact_phone": "+254755555555",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertContains(
            response,
            "Select a valid sex.",
        )

    def test_patient_create_rejects_duplicate_profile(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("PatientsApp:create"),
            {
                "username": self.user.username,
                "date_of_birth": "2002-03-10",
                "sex": Patient.Sex.MALE,
                "phone_number": "+254744444444",
                "address": "Mombasa, Kenya",
                "emergency_contact_name": "Sarah Smith",
                "emergency_contact_phone": "+254755555555",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertContains(
            response,
            "That user already has a patient profile.",
        )

    def test_patient_create_rejects_non_patient_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("PatientsApp:create"),
            {
                "username": self.staff_user.username,
                "date_of_birth": "2002-03-10",
                "sex": Patient.Sex.MALE,
                "phone_number": "+254744444444",
                "address": "Mombasa, Kenya",
                "emergency_contact_name": "Sarah Smith",
                "emergency_contact_phone": "+254755555555",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertContains(
            response,
            "A valid patient user is required.",
        )

    def test_patient_edit_successfully(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "PatientsApp:edit",
                kwargs={"patient_id": self.patient.id},
            ),
            {
                "date_of_birth": "1999-12-25",
                "sex": Patient.Sex.FEMALE,
                "phone_number": "+254766666666",
                "address": "Nairobi, Kenya",
                "emergency_contact_name": "Updated Contact",
                "emergency_contact_phone": "+254777777777",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(
                "PatientsApp:detail",
                kwargs={"patient_id": self.patient.id},
            ),
        )

        self.patient.refresh_from_db()

        self.assertEqual(
            self.patient.date_of_birth,
            date(1999, 12, 25),
        )
        self.assertEqual(
            self.patient.sex,
            Patient.Sex.FEMALE,
        )
        self.assertEqual(
            self.patient.phone_number,
            "+254766666666",
        )

    def test_patient_edit_rejects_missing_date_of_birth(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "PatientsApp:edit",
                kwargs={"patient_id": self.patient.id},
            ),
            {
                "date_of_birth": "",
                "sex": Patient.Sex.MALE,
                "phone_number": "+254766666666",
                "address": "Nairobi, Kenya",
                "emergency_contact_name": "Updated Contact",
                "emergency_contact_phone": "+254777777777",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Date of birth is required.",
        )

        self.patient.refresh_from_db()

        self.assertEqual(
            self.patient.date_of_birth,
            date(2000, 1, 15),
        )

    def test_patient_edit_rejects_invalid_sex(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "PatientsApp:edit",
                kwargs={"patient_id": self.patient.id},
            ),
            {
                "date_of_birth": "1999-12-25",
                "sex": "INVALID",
                "phone_number": "+254766666666",
                "address": "Nairobi, Kenya",
                "emergency_contact_name": "Updated Contact",
                "emergency_contact_phone": "+254777777777",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Select a valid sex.",
        )

        self.patient.refresh_from_db()

        self.assertEqual(
            self.patient.sex,
            Patient.Sex.MALE,
        )

    def test_patient_timeline_authenticated(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse(
                "PatientsApp:timeline",
                kwargs={"patient_id": self.patient.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "PatientsApp/timeline.html",
        )
        self.assertContains(response, "Patient Timeline")
        self.assertContains(response, "patientone")
