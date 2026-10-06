from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.FollowupsApp.models import FollowUp
from apps.FollowupsApp.serializers import FollowUpSerializer
from apps.FollowupsApp.services import (
    complete_follow_up,
    create_follow_up,
    get_all_follow_ups,
    get_follow_up,
    get_missed_follow_ups,
    get_patient_follow_ups,
    get_pending_follow_ups,
    reschedule_follow_up,
    update_follow_up,
)
from apps.PatientsApp.models import Patient
from apps.ReferralsApp.models import Referral

ALLOWED_ROLES = {
    "CLINICIAN",
    "FACILITY_STAFF",
    "ADMIN",
}


def _require_staff_access(user):
    if user.is_superuser:
        return

    if getattr(user, "role", None) not in ALLOWED_ROLES:
        raise PermissionDenied("You do not have permission to access follow-ups.")


def _serialize_follow_ups(queryset):
    return FollowUpSerializer(queryset, many=True).data


@login_required
def list_page(request):
    _require_staff_access(request.user)

    follow_ups = get_all_follow_ups()

    return render(
        request,
        "FollowupsApp/list.html",
        {"follow_ups": follow_ups},
    )


@login_required
def create_page(request):
    _require_staff_access(request.user)

    patients = Patient.objects.select_related("user").order_by("user__username")
    referrals = Referral.objects.select_related("patient", "patient__user").order_by(
        "-created_at"
    )

    return render(
        request,
        "FollowupsApp/create.html",
        {
            "patients": patients,
            "referrals": referrals,
        },
    )


@login_required
def detail_page(request, follow_up_id):
    _require_staff_access(request.user)

    follow_up = get_follow_up(follow_up_id)

    return render(
        request,
        "FollowupsApp/detail.html",
        {"follow_up": follow_up},
    )


@login_required
def all_follow_ups(request):
    _require_staff_access(request.user)

    data = _serialize_follow_ups(get_all_follow_ups())

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "follow_ups": data,
        }
    )


@login_required
def patient_follow_ups(request, patient_id):
    _require_staff_access(request.user)

    patient = get_object_or_404(Patient, id=patient_id)
    data = _serialize_follow_ups(get_patient_follow_ups(patient))

    return JsonResponse(
        {
            "success": True,
            "patient_id": patient.id,
            "count": len(data),
            "follow_ups": data,
        }
    )


@login_required
def pending_follow_ups(request):
    _require_staff_access(request.user)

    data = _serialize_follow_ups(get_pending_follow_ups())

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "follow_ups": data,
        }
    )


@login_required
def missed_follow_ups(request):
    _require_staff_access(request.user)

    data = _serialize_follow_ups(get_missed_follow_ups())

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "follow_ups": data,
        }
    )


@login_required
def follow_up_detail(request, follow_up_id):
    _require_staff_access(request.user)

    follow_up = get_follow_up(follow_up_id)

    return JsonResponse(
        {
            "success": True,
            "follow_up": FollowUpSerializer(follow_up).data,
        }
    )


@login_required
@require_POST
def create_follow_up_view(request):
    _require_staff_access(request.user)

    try:
        patient_id = request.POST.get("patient_id")
        referral_id = request.POST.get("referral_id")
        follow_up_type = request.POST.get(
            "follow_up_type",
            FollowUp.FollowUpType.GENERAL_REVIEW,
        )
        reason = request.POST.get("reason", "")
        scheduled_at = request.POST.get("scheduled_at")
        status = request.POST.get(
            "status",
            FollowUp.Status.PENDING,
        )
        outcome = request.POST.get("outcome", "")
        notes = request.POST.get("notes", "")
        completed_at = request.POST.get("completed_at")

        if not patient_id:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Patient is required.",
                },
                status=400,
            )

        if not scheduled_at:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Scheduled date and time is required.",
                },
                status=400,
            )

        patient = get_object_or_404(Patient, id=patient_id)

        referral = None

        if referral_id:
            referral = get_object_or_404(
                Referral,
                id=referral_id,
            )

        follow_up = create_follow_up(
            patient=patient,
            created_by=request.user,
            reason=reason,
            scheduled_at=scheduled_at,
            follow_up_type=follow_up_type,
            referral=referral,
            status=status,
            outcome=outcome,
            notes=notes,
            completed_at=completed_at or None,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Follow-up created successfully.",
                "follow_up": FollowUpSerializer(follow_up).data,
            },
            status=201,
        )

    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )


@login_required
@require_POST
def update_follow_up_view(request, follow_up_id):
    _require_staff_access(request.user)

    follow_up = get_object_or_404(
        FollowUp,
        id=follow_up_id,
    )

    try:
        follow_up = update_follow_up(
            follow_up=follow_up,
            reason=request.POST.get("reason"),
            scheduled_at=request.POST.get("scheduled_at") or None,
            follow_up_type=request.POST.get("follow_up_type") or None,
            status=request.POST.get("status") or None,
            outcome=request.POST.get("outcome"),
            notes=request.POST.get("notes"),
            completed_at=request.POST.get("completed_at") or None,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Follow-up updated successfully.",
                "follow_up": FollowUpSerializer(follow_up).data,
            }
        )

    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )


@login_required
@require_POST
def complete_follow_up_view(request, follow_up_id):
    _require_staff_access(request.user)

    follow_up = get_object_or_404(
        FollowUp,
        id=follow_up_id,
    )

    try:
        follow_up = complete_follow_up(
            follow_up=follow_up,
            outcome=request.POST.get("outcome", ""),
            notes=request.POST.get("notes", ""),
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Follow-up completed successfully.",
                "follow_up": FollowUpSerializer(follow_up).data,
            }
        )

    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )


@login_required
@require_POST
def reschedule_follow_up_view(request, follow_up_id):
    _require_staff_access(request.user)

    follow_up = get_object_or_404(
        FollowUp,
        id=follow_up_id,
    )

    scheduled_at = request.POST.get("scheduled_at")

    if not scheduled_at:
        return JsonResponse(
            {
                "success": False,
                "error": "New scheduled date and time is required.",
            },
            status=400,
        )

    try:
        follow_up = reschedule_follow_up(
            follow_up=follow_up,
            scheduled_at=scheduled_at,
            notes=request.POST.get("notes", ""),
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Follow-up rescheduled successfully.",
                "follow_up": FollowUpSerializer(follow_up).data,
            }
        )

    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=400,
        )
