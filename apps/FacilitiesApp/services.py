from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Facility, FacilityResource


def validate_facility_name(name):
    name = str(name).strip()

    if not name:
        raise ValidationError("A facility name is required.")

    return name


def validate_facility_code(facility_code):
    facility_code = str(facility_code).strip().upper()

    if not facility_code:
        raise ValidationError("A facility code is required.")

    return facility_code


def validate_facility_type(facility_type):
    facility_type = str(facility_type).strip().upper()

    valid_types = {choice[0] for choice in Facility.FacilityType.choices}

    if facility_type not in valid_types:
        raise ValidationError("A valid facility type is required.")

    return facility_type


def validate_operating_status(status):
    status = str(status).strip().upper()

    valid_statuses = {choice[0] for choice in Facility.OperatingStatus.choices}

    if status not in valid_statuses:
        raise ValidationError("A valid operating status is required.")

    return status


def validate_resource_name(name):
    name = str(name).strip()

    if not name:
        raise ValidationError("A resource name is required.")

    return name


def validate_resource_category(category):
    category = str(category).strip().upper()

    valid_categories = {
        choice[0] for choice in FacilityResource.ResourceCategory.choices
    }

    if category not in valid_categories:
        raise ValidationError("A valid resource category is required.")

    return category


@transaction.atomic
def create_facility(
    name,
    facility_code,
    facility_type,
    county,
    sub_county="",
    address="",
    phone_number="",
    email="",
    latitude=None,
    longitude=None,
    services="",
    referral_available=True,
    operating_status=Facility.OperatingStatus.ACTIVE,
):
    name = validate_facility_name(name)
    facility_code = validate_facility_code(facility_code)
    facility_type = validate_facility_type(facility_type)
    operating_status = validate_operating_status(operating_status)

    if Facility.objects.filter(facility_code=facility_code).exists():
        raise ValidationError("A facility with this code already exists.")

    return Facility.objects.create(
        name=name,
        facility_code=facility_code,
        facility_type=facility_type,
        county=str(county).strip(),
        sub_county=str(sub_county).strip(),
        address=str(address).strip(),
        phone_number=str(phone_number).strip(),
        email=str(email).strip(),
        latitude=latitude,
        longitude=longitude,
        services=str(services).strip(),
        referral_available=referral_available,
        operating_status=operating_status,
    )


@transaction.atomic
def update_facility(
    facility,
    name=None,
    facility_code=None,
    facility_type=None,
    county=None,
    sub_county=None,
    address=None,
    phone_number=None,
    email=None,
    latitude=None,
    longitude=None,
    services=None,
    referral_available=None,
    operating_status=None,
):
    fields = []

    if name is not None:
        facility.name = validate_facility_name(name)
        fields.append("name")

    if facility_code is not None:
        facility_code = validate_facility_code(facility_code)

        duplicate_exists = (
            Facility.objects.filter(facility_code=facility_code)
            .exclude(id=facility.id)
            .exists()
        )

        if duplicate_exists:
            raise ValidationError("A facility with this code already exists.")

        facility.facility_code = facility_code
        fields.append("facility_code")

    if facility_type is not None:
        facility.facility_type = validate_facility_type(facility_type)
        fields.append("facility_type")

    if county is not None:
        facility.county = str(county).strip()
        fields.append("county")

    if sub_county is not None:
        facility.sub_county = str(sub_county).strip()
        fields.append("sub_county")

    if address is not None:
        facility.address = str(address).strip()
        fields.append("address")

    if phone_number is not None:
        facility.phone_number = str(phone_number).strip()
        fields.append("phone_number")

    if email is not None:
        facility.email = str(email).strip()
        fields.append("email")

    if latitude is not None:
        facility.latitude = latitude
        fields.append("latitude")

    if longitude is not None:
        facility.longitude = longitude
        fields.append("longitude")

    if services is not None:
        facility.services = str(services).strip()
        fields.append("services")

    if referral_available is not None:
        facility.referral_available = referral_available
        fields.append("referral_available")

    if operating_status is not None:
        facility.operating_status = validate_operating_status(operating_status)
        fields.append("operating_status")

    if fields:
        fields.append("updated_at")
        facility.save(update_fields=fields)

    return facility


def get_facility(facility_id):
    return Facility.objects.prefetch_related("resources").get(id=facility_id)


def get_all_facilities():
    return Facility.objects.prefetch_related("resources").order_by("name")


def get_active_facilities():
    return (
        Facility.objects.filter(operating_status=Facility.OperatingStatus.ACTIVE)
        .prefetch_related("resources")
        .order_by("name")
    )


def get_referral_facilities():
    return (
        Facility.objects.filter(
            referral_available=True,
            operating_status=Facility.OperatingStatus.ACTIVE,
        )
        .prefetch_related("resources")
        .order_by("name")
    )


@transaction.atomic
def create_resource(
    facility,
    name,
    category,
    quantity=0,
    available=True,
    notes="",
):
    name = validate_resource_name(name)
    category = validate_resource_category(category)

    if quantity < 0:
        raise ValidationError("Resource quantity cannot be negative.")

    return FacilityResource.objects.create(
        facility=facility,
        name=name,
        category=category,
        quantity=quantity,
        available=available,
        notes=str(notes).strip(),
    )


@transaction.atomic
def update_resource(
    resource,
    name=None,
    category=None,
    quantity=None,
    available=None,
    notes=None,
):
    fields = []

    if name is not None:
        resource.name = validate_resource_name(name)
        fields.append("name")

    if category is not None:
        resource.category = validate_resource_category(category)
        fields.append("category")

    if quantity is not None:
        if quantity < 0:
            raise ValidationError("Resource quantity cannot be negative.")

        resource.quantity = quantity
        fields.append("quantity")

    if available is not None:
        resource.available = available
        fields.append("available")

    if notes is not None:
        resource.notes = str(notes).strip()
        fields.append("notes")

    if fields:
        fields.append("updated_at")
        resource.save(update_fields=fields)

    return resource


def get_facility_resources(facility):
    return FacilityResource.objects.filter(facility=facility).order_by(
        "category", "name"
    )


def get_resource(resource_id):
    return FacilityResource.objects.select_related("facility").get(id=resource_id)
