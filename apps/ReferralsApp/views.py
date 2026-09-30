from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.AccountsApp.models import User
from apps.AmrApp.models import AMRRecord
from apps.PatientsApp.models import Patient

from .models import Referral
from .serializers import ReferralSerializer
from .services import (
    create_referral,
    get_all_referrals,
    get_patient_referrals,
    get_referral,
    update_referral,
    update_referral_status,
)

REFERRAL_STAFF_ROLES = {
    User.Role.CLINICIAN,
    User.Role.FACILITY_STAFF,
    User.Role.ADMIN,
}


def _is_referral_staff(user):
    return user.is_authenticated and (
        user.is_superuser or user.role in REFERRAL_STAFF_ROLES
    )


def _require_referral_staff(request):
    if not _is_referral_staff(request.user):
        raise PermissionDenied("You do not have permission to use referral services.")


@login_required
def create_page(request):
    _require_referral_staff(request)
    return render(request, "ReferralsApp/create.html")


@login_required
def list_page(request):
    _require_referral_staff(request)
    return render(request, "ReferralsApp/list.html")


@login_required
def detail_page(request, referral_id):
    _require_referral_staff(request)
    return render(
        request,
        "ReferralsApp/detail.html",
        {"referral_id": referral_id},
    )


@login_required
def tracking_page(request):
    _require_referral_staff(request)
    return render(request, "ReferralsApp/tracking.html")


@login_required
def create_referral_view(request):
    _require_referral_staff(request)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    patient_id = request.POST.get("patient_id")
    amr_record_id = request.POST.get("amr_record_id")
    referral_reason = request.POST.get("referral_reason", "")
    clinical_summary = request.POST.get("clinical_summary", "")
    destination_name = request.POST.get("destination_name", "")
    priority = request.POST.get("priority", Referral.Priority.ROUTINE)
    referral_notes = request.POST.get("referral_notes", "")

    patient = get_object_or_404(Patient, id=patient_id)

    amr_record = None
    if amr_record_id:
        amr_record = get_object_or_404(
            AMRRecord,
            id=amr_record_id,
        )

    try:
        referral = create_referral(
            patient=patient,
            created_by=request.user,
            referral_reason=referral_reason,
            amr_record=amr_record,
            clinical_summary=clinical_summary,
            destination_name=destination_name,
            priority=priority,
            referral_notes=referral_notes,
        )
    except ValidationError as error:
        return JsonResponse(
            {"error": error.message},
            status=400,
        )

    return JsonResponse(
        ReferralSerializer(referral).data,
        status=201,
    )


@login_required
def referral_detail(request, referral_id):
    _require_referral_staff(request)

    referral = get_object_or_404(
        Referral.objects.select_related(
            "patient__user",
            "amr_record",
            "created_by",
        ),
        id=referral_id,
    )

    return JsonResponse(ReferralSerializer(referral).data)


@login_required
def update_referral_view(request, referral_id):
    _require_referral_staff(request)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    referral = get_object_or_404(
        Referral,
        id=referral_id,
    )

    try:
        referral = update_referral(
            referral=referral,
            referral_reason=request.POST.get("referral_reason"),
            clinical_summary=request.POST.get("clinical_summary"),
            destination_name=request.POST.get("destination_name"),
            priority=request.POST.get("priority"),
            status=request.POST.get("status"),
            referral_notes=request.POST.get("referral_notes"),
        )
    except ValidationError as error:
        return JsonResponse(
            {"error": error.message},
            status=400,
        )

    referral = get_referral(referral.id)

    return JsonResponse(ReferralSerializer(referral).data)


@login_required
def update_referral_status_view(request, referral_id):
    _require_referral_staff(request)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    referral = get_object_or_404(
        Referral,
        id=referral_id,
    )

    status = request.POST.get("status", "")

    try:
        referral = update_referral_status(
            referral=referral,
            status=status,
        )
    except ValidationError as error:
        return JsonResponse(
            {"error": error.message},
            status=400,
        )

    referral = get_referral(referral.id)

    return JsonResponse(ReferralSerializer(referral).data)


@login_required
def all_referrals(request):
    _require_referral_staff(request)

    referrals = get_all_referrals()

    return JsonResponse(
        {
            "referrals": ReferralSerializer(
                referrals,
                many=True,
            ).data
        }
    )


@login_required
def patient_referrals(request, patient_id):
    _require_referral_staff(request)

    patient = get_object_or_404(
        Patient,
        id=patient_id,
    )

    referrals = get_patient_referrals(patient)

    return JsonResponse(
        {
            "patient_id": patient.id,
            "referrals": ReferralSerializer(
                referrals,
                many=True,
            ).data,
        }
    )
