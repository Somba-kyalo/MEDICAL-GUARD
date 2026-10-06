from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import render

from .models import Facility, FacilityResource
from .serializers import FacilityResourceSerializer, FacilitySerializer
from .services import (
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

ALLOWED_ROLES = {
    "CLINICIAN",
    "FACILITY_STAFF",
    "ADMIN",
}


def user_has_facility_access(user):
    return user.is_superuser or getattr(user, "role", None) in ALLOWED_ROLES


def require_facility_access(user):
    if not user_has_facility_access(user):
        raise PermissionDenied("You do not have permission to access FacilitiesApp.")


@login_required
def list_page(request):
    require_facility_access(request.user)
    return render(request, "FacilitiesApp/list.html")


@login_required
def detail_page(request, facility_id):
    require_facility_access(request.user)
    return render(
        request,
        "FacilitiesApp/detail.html",
        {"facility_id": facility_id},
    )


@login_required
def map_page(request):
    require_facility_access(request.user)
    return render(request, "FacilitiesApp/map.html")


@login_required
def resources_page(request, facility_id=None):
    require_facility_access(request.user)
    return render(
        request,
        "FacilitiesApp/resources.html",
        {"facility_id": facility_id},
    )


@login_required
def all_facilities(request):
    require_facility_access(request.user)

    facilities = get_all_facilities()

    return JsonResponse(
        {
            "facilities": FacilitySerializer(
                facilities,
                many=True,
            ).data
        }
    )


@login_required
def active_facilities(request):
    require_facility_access(request.user)

    facilities = get_active_facilities()

    return JsonResponse(
        {
            "facilities": FacilitySerializer(
                facilities,
                many=True,
            ).data
        }
    )


@login_required
def referral_facilities(request):
    require_facility_access(request.user)

    facilities = get_referral_facilities()

    return JsonResponse(
        {
            "facilities": FacilitySerializer(
                facilities,
                many=True,
            ).data
        }
    )


@login_required
def facility_detail(request, facility_id):
    require_facility_access(request.user)

    facility = get_facility(facility_id)

    return JsonResponse(FacilitySerializer(facility).data)


@login_required
def create_facility_view(request):
    require_facility_access(request.user)

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required."},
            status=405,
        )

    try:
        facility = create_facility(
            name=request.POST.get("name", ""),
            facility_code=request.POST.get("facility_code", ""),
            facility_type=request.POST.get("facility_type", ""),
            county=request.POST.get("county", ""),
            sub_county=request.POST.get("sub_county", ""),
            address=request.POST.get("address", ""),
            phone_number=request.POST.get("phone_number", ""),
            email=request.POST.get("email", ""),
            latitude=request.POST.get("latitude") or None,
            longitude=request.POST.get("longitude") or None,
            services=request.POST.get("services", ""),
            referral_available=request.POST.get(
                "referral_available",
                "true",
            ).lower()
            == "true",
            operating_status=request.POST.get(
                "operating_status",
                Facility.OperatingStatus.ACTIVE,
            ),
        )

        return JsonResponse(
            FacilitySerializer(facility).data,
            status=201,
        )

    except ValidationError as error:
        return JsonResponse(
            {"error": error.message},
            status=400,
        )


@login_required
def update_facility_view(request, facility_id):
    require_facility_access(request.user)

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required."},
            status=405,
        )

    facility = get_facility(facility_id)

    try:
        update_data = {}

        fields = [
            "name",
            "facility_code",
            "facility_type",
            "county",
            "sub_county",
            "address",
            "phone_number",
            "email",
            "latitude",
            "longitude",
            "services",
            "operating_status",
        ]

        for field in fields:
            if field in request.POST:
                update_data[field] = request.POST.get(field)

        if "referral_available" in request.POST:
            update_data["referral_available"] = (
                request.POST.get("referral_available", "").lower() == "true"
            )

        updated_facility = update_facility(
            facility,
            **update_data,
        )

        return JsonResponse(FacilitySerializer(updated_facility).data)

    except ValidationError as error:
        return JsonResponse(
            {"error": error.message},
            status=400,
        )


@login_required
def facility_resources(request, facility_id):
    require_facility_access(request.user)

    facility = get_facility(facility_id)
    resources = get_facility_resources(facility)

    return JsonResponse(
        {
            "facility": FacilitySerializer(facility).data,
            "resources": FacilityResourceSerializer(
                resources,
                many=True,
            ).data,
        }
    )


@login_required
def create_resource_view(request, facility_id):
    require_facility_access(request.user)

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required."},
            status=405,
        )

    facility = get_facility(facility_id)

    try:
        quantity = int(request.POST.get("quantity", 0))

        resource = create_resource(
            facility=facility,
            name=request.POST.get("name", ""),
            category=request.POST.get("category", ""),
            quantity=quantity,
            available=request.POST.get(
                "available",
                "true",
            ).lower()
            == "true",
            notes=request.POST.get("notes", ""),
        )

        return JsonResponse(
            FacilityResourceSerializer(resource).data,
            status=201,
        )

    except (ValidationError, ValueError) as error:
        message = (
            error.message
            if isinstance(error, ValidationError)
            else "Resource quantity must be a valid number."
        )

        return JsonResponse(
            {"error": message},
            status=400,
        )


@login_required
def update_resource_view(request, resource_id):
    require_facility_access(request.user)

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required."},
            status=405,
        )

    resource = get_resource(resource_id)

    try:
        update_data = {}

        if "name" in request.POST:
            update_data["name"] = request.POST.get("name")

        if "category" in request.POST:
            update_data["category"] = request.POST.get("category")

        if "quantity" in request.POST:
            update_data["quantity"] = int(request.POST.get("quantity", 0))

        if "available" in request.POST:
            update_data["available"] = (
                request.POST.get("available", "").lower() == "true"
            )

        if "notes" in request.POST:
            update_data["notes"] = request.POST.get("notes")

        updated_resource = update_resource(
            resource,
            **update_data,
        )

        return JsonResponse(FacilityResourceSerializer(updated_resource).data)

    except (ValidationError, ValueError) as error:
        message = (
            error.message
            if isinstance(error, ValidationError)
            else "Resource quantity must be a valid number."
        )

        return JsonResponse(
            {"error": message},
            status=400,
        )
