from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.FacilitiesApp.models import Facility, FacilityResource
from apps.FacilitiesApp.serializers import (
    FacilityResourceSerializer,
    FacilitySerializer,
)
from apps.FacilitiesApp.services import (
    create_facility,
    create_resource,
    get_active_facilities,
    get_all_facilities,
    get_facility,
    get_facility_resources,
    get_referral_facilities,
    get_resource,
    update_facility,
    update_resource,
)
from apps.FacilitiesApp.views import (
    active_facilities,
    all_facilities,
    create_facility_view,
    create_resource_view,
    facility_detail,
    facility_resources,
    referral_facilities,
    update_facility_view,
    update_resource_view,
)

User = get_user_model()

class FacilitiesAppModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="facility_user",
            password="testpass123",
            role="FACILITY_STAFF",
        )

        self.facility = Facility.objects.create(
            name="Voi County Hospital",
            facility_code="VOI-001",
            facility_type=Facility.FacilityType.HOSPITAL,
            county="Taita Taveta",
            sub_county="Voi",
            address="Voi Town",
            phone_number="0712345678",
            email="voi@example.com",
            latitude=-3.3969,
            longitude=38.5567,
            services="Emergency, Laboratory, Outpatient",
            referral_available=True,
            operating_status=Facility.OperatingStatus.ACTIVE,
        )

        self.resource = FacilityResource.objects.create(
            facility=self.facility,
            name="Hospital Beds",
            category=FacilityResource.ResourceCategory.BED,
            quantity=20,
            available=True,
            notes="General ward beds",
        )

    def test_facility_string_representation(self):
        self.assertEqual(
            str(self.facility),
            "Voi County Hospital (VOI-001)",
        )

    def test_resource_string_representation(self):
        self.assertEqual(
            str(self.resource),
            "Voi County Hospital - Hospital Beds",
        )

    def test_facility_types(self):
        self.assertIn(
            Facility.FacilityType.HOSPITAL,
            dict(Facility.FacilityType.choices),
        )

    def test_operating_statuses(self):
        self.assertIn(
            Facility.OperatingStatus.ACTIVE,
            dict(Facility.OperatingStatus.choices),
        )

    def test_resource_categories(self):
        self.assertIn(
            FacilityResource.ResourceCategory.BED,
            dict(FacilityResource.ResourceCategory.choices),
        )

    def test_facility_code_is_unique(self):
        with self.assertRaises(Exception):
            Facility.objects.create(
                name="Another Hospital",
                facility_code="VOI-001",
                facility_type=Facility.FacilityType.HOSPITAL,
                county="Taita Taveta",
            )

    def test_resource_belongs_to_facility(self):
        self.assertEqual(
            self.resource.facility,
            self.facility,
        )


class FacilitiesAppServiceTests(TestCase):

    def setUp(self):
        self.facility = create_facility(
            name="Voi County Hospital",
            facility_code="voi-001",
            facility_type="hospital",
            county="Taita Taveta",
            sub_county="Voi",
            address="Voi Town",
            referral_available=True,
            operating_status="active",
        )

        self.other_facility = create_facility(
            name="Voi Clinic",
            facility_code="voi-002",
            facility_type="clinic",
            county="Taita Taveta",
            referral_available=False,
            operating_status="inactive",
        )

    def test_create_facility(self):
        self.assertEqual(
            self.facility.name,
            "Voi County Hospital",
        )
        self.assertEqual(
            self.facility.facility_code,
            "VOI-001",
        )

    def test_create_facility_normalizes_values(self):
        self.assertEqual(
            self.facility.facility_code,
            "VOI-001",
        )
        self.assertEqual(
            self.facility.facility_type,
            "HOSPITAL",
        )
        self.assertEqual(
            self.facility.operating_status,
            "ACTIVE",
        )

    def test_create_duplicate_facility_code_fails(self):
        with self.assertRaises(ValidationError):
            create_facility(
                name="Duplicate Hospital",
                facility_code="VOI-001",
                facility_type="HOSPITAL",
                county="Taita Taveta",
            )

    def test_create_facility_without_name_fails(self):
        with self.assertRaises(ValidationError):
            create_facility(
                name="",
                facility_code="VOI-003",
                facility_type="HOSPITAL",
                county="Taita Taveta",
            )

    def test_create_facility_without_code_fails(self):
        with self.assertRaises(ValidationError):
            create_facility(
                name="New Hospital",
                facility_code="",
                facility_type="HOSPITAL",
                county="Taita Taveta",
            )

    def test_invalid_facility_type_fails(self):
        with self.assertRaises(ValidationError):
            create_facility(
                name="New Hospital",
                facility_code="VOI-003",
                facility_type="INVALID",
                county="Taita Taveta",
            )

    def test_invalid_operating_status_fails(self):
        with self.assertRaises(ValidationError):
            create_facility(
                name="New Hospital",
                facility_code="VOI-003",
                facility_type="HOSPITAL",
                county="Taita Taveta",
                operating_status="INVALID",
            )

    def test_get_facility(self):
        facility = get_facility(self.facility.id)

        self.assertEqual(
            facility.id,
            self.facility.id,
        )

    def test_get_all_facilities(self):
        facilities = get_all_facilities()

        self.assertEqual(
            facilities.count(),
            2,
        )

    def test_get_active_facilities(self):
        facilities = get_active_facilities()

        self.assertEqual(
            facilities.count(),
            1,
        )
        self.assertEqual(
            facilities.first(),
            self.facility,
        )

    def test_get_referral_facilities(self):
        facilities = get_referral_facilities()

        self.assertEqual(
            facilities.count(),
            1,
        )
        self.assertEqual(
            facilities.first(),
            self.facility,
        )

    def test_update_facility(self):
        update_facility(
            self.facility,
            name="Updated Voi Hospital",
            county="Mombasa",
            referral_available=False,
        )

        self.facility.refresh_from_db()

        self.assertEqual(
            self.facility.name,
            "Updated Voi Hospital",
        )
        self.assertEqual(
            self.facility.county,
            "Mombasa",
        )
        self.assertFalse(
            self.facility.referral_available,
        )

    def test_update_facility_code_duplicate_fails(self):
        with self.assertRaises(ValidationError):
            update_facility(
                self.facility,
                facility_code="VOI-002",
            )

    def test_create_resource(self):
        resource = create_resource(
            facility=self.facility,
            name="Laboratory Staff",
            category="staff",
            quantity=5,
            available=True,
        )

        self.assertEqual(
            resource.name,
            "Laboratory Staff",
        )
        self.assertEqual(
            resource.category,
            "STAFF",
        )
        self.assertEqual(
            resource.quantity,
            5,
        )

    def test_create_resource_without_name_fails(self):
        with self.assertRaises(ValidationError):
            create_resource(
                facility=self.facility,
                name="",
                category="BED",
            )

    def test_create_resource_with_invalid_category_fails(self):
        with self.assertRaises(ValidationError):
            create_resource(
                facility=self.facility,
                name="Unknown Resource",
                category="INVALID",
            )

    def test_create_resource_with_negative_quantity_fails(self):
        with self.assertRaises(ValidationError):
            create_resource(
                facility=self.facility,
                name="Beds",
                category="BED",
                quantity=-1,
            )

    def test_update_resource(self):
        resource = create_resource(
            facility=self.facility,
            name="Beds",
            category="BED",
            quantity=10,
        )

        update_resource(
            resource,
            quantity=15,
            available=False,
            notes="Updated stock",
        )

        resource.refresh_from_db()

        self.assertEqual(
            resource.quantity,
            15,
        )
        self.assertFalse(
            resource.available,
        )
        self.assertEqual(
            resource.notes,
            "Updated stock",
        )

    def test_get_facility_resources(self):
        resource = create_resource(
            facility=self.facility,
            name="Beds",
            category="BED",
            quantity=10,
        )

        resources = get_facility_resources(
            self.facility,
        )

        self.assertIn(
            resource,
            resources,
        )

    def test_get_resource(self):
        resource = create_resource(
            facility=self.facility,
            name="Beds",
            category="BED",
            quantity=10,
        )

        fetched = get_resource(resource.id)

        self.assertEqual(
            fetched.id,
            resource.id,
        )


class FacilitiesAppSerializerTests(TestCase):

    def setUp(self):
        self.facility = Facility.objects.create(
            name="Voi County Hospital",
            facility_code="VOI-001",
            facility_type=Facility.FacilityType.HOSPITAL,
            county="Taita Taveta",
            sub_county="Voi",
            referral_available=True,
            operating_status=Facility.OperatingStatus.ACTIVE,
        )

        self.resource = FacilityResource.objects.create(
            facility=self.facility,
            name="Beds",
            category=FacilityResource.ResourceCategory.BED,
            quantity=10,
            available=True,
        )

    def test_facility_serializer(self):
        serializer = FacilitySerializer(self.facility)

        self.assertEqual(
            serializer.data["name"],
            "Voi County Hospital",
        )
        self.assertEqual(
            serializer.data["facility_code"],
            "VOI-001",
        )
        self.assertEqual(
            serializer.data["facility_type_display"],
            "Hospital",
        )
        self.assertEqual(
            len(serializer.data["resources"]),
            1,
        )

    def test_resource_serializer(self):
        serializer = FacilityResourceSerializer(self.resource)

        self.assertEqual(
            serializer.data["name"],
            "Beds",
        )
        self.assertEqual(
            serializer.data["category_display"],
            "Beds",
        )
        self.assertEqual(
            serializer.data["quantity"],
            10,
        )


class FacilitiesAppViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="facility_staff",
            password="testpass123",
            role="FACILITY_STAFF",
        )

        self.clinician = User.objects.create_user(
            username="clinician",
            password="testpass123",
            role="CLINICIAN",
        )

        self.patient = User.objects.create_user(
            username="patient",
            password="testpass123",
            role="PATIENT",
        )

        self.facility = Facility.objects.create(
            name="Voi County Hospital",
            facility_code="VOI-001",
            facility_type=Facility.FacilityType.HOSPITAL,
            county="Taita Taveta",
            sub_county="Voi",
            referral_available=True,
            operating_status=Facility.OperatingStatus.ACTIVE,
        )

        self.resource = FacilityResource.objects.create(
            facility=self.facility,
            name="Beds",
            category=FacilityResource.ResourceCategory.BED,
            quantity=10,
            available=True,
        )

        self.client.login(
            username="facility_staff",
            password="testpass123",
        )

    def test_all_facilities_api(self):
        response = self.client.get(reverse("FacilitiesApp:api_records"))

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            len(response.json()["facilities"]),
            1,
        )

    def test_active_facilities_api(self):
        response = self.client.get(reverse("FacilitiesApp:api_active"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_referral_facilities_api(self):
        response = self.client.get(reverse("FacilitiesApp:api_referral"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_facility_detail_api(self):
        response = self.client.get(
            reverse(
                "FacilitiesApp:api_detail",
                args=[self.facility.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["facility_code"],
            "VOI-001",
        )

    def test_facility_resources_api(self):
        response = self.client.get(
            reverse(
                "FacilitiesApp:api_resources",
                args=[self.facility.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            len(response.json()["resources"]),
            1,
        )

    def test_create_facility_api(self):
        response = self.client.post(
            reverse("FacilitiesApp:api_create"),
            {
                "name": "New Health Centre",
                "facility_code": "VOI-002",
                "facility_type": "HEALTH_CENTER",
                "county": "Taita Taveta",
                "sub_county": "Voi",
                "referral_available": "true",
                "operating_status": "ACTIVE",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )
        self.assertEqual(
            response.json()["facility_code"],
            "VOI-002",
        )

    def test_create_resource_api(self):
        response = self.client.post(
            reverse(
                "FacilitiesApp:api_resource_create",
                args=[self.facility.id],
            ),
            {
                "name": "New Beds",
                "category": "BED",
                "quantity": "15",
                "available": "true",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )
        self.assertEqual(
            response.json()["quantity"],
            15,
        )

    def test_update_facility_api(self):
        response = self.client.post(
            reverse(
                "FacilitiesApp:api_update",
                args=[self.facility.id],
            ),
            {
                "name": "Updated Hospital",
                "county": "Mombasa",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["name"],
            "Updated Hospital",
        )

    def test_update_resource_api(self):
        response = self.client.post(
            reverse(
                "FacilitiesApp:api_resource_update",
                args=[self.resource.id],
            ),
            {
                "quantity": "25",
                "available": "false",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertEqual(
            response.json()["quantity"],
            25,
        )

    def test_get_requests_require_login(self):
        self.client.logout()

        response = self.client.get(reverse("FacilitiesApp:api_records"))

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_patient_cannot_access_facilities(self):
        self.client.logout()

        self.client.login(
            username="patient",
            password="testpass123",
        )

        response = self.client.get(reverse("FacilitiesApp:api_records"))

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_clinician_can_access_facilities(self):
        self.client.logout()

        self.client.login(
            username="clinician",
            password="testpass123",
        )

        response = self.client.get(reverse("FacilitiesApp:api_records"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_create_facility_requires_post(self):
        response = self.client.get(reverse("FacilitiesApp:api_create"))

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_create_resource_requires_post(self):
        response = self.client.get(
            reverse(
                "FacilitiesApp:api_resource_create",
                args=[self.facility.id],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
