from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.AccountsApp.models import User
from apps.ScreeningApp.models import Screening

from .serializers import serialize_ai_analysis
from .services import create_ai_analysis

AI_STAFF_ROLES = {
    User.Role.CLINICIAN,
    User.Role.FACILITY_STAFF,
    User.Role.ADMIN,
}


def _is_ai_staff(user):
    return user.is_authenticated and (user.is_superuser or user.role in AI_STAFF_ROLES)


def _require_ai_staff(request):
    if not _is_ai_staff(request.user):
        raise PermissionDenied("You do not have permission to use AI analysis.")


@login_required
def analyze_screening(request, screening_id):
    _require_ai_staff(request)

    screening = get_object_or_404(
        Screening.objects.select_related(
            "patient__user",
        ).prefetch_related(
            "responses",
        ),
        id=screening_id,
    )

    if screening.status != Screening.Status.COMPLETED:
        return JsonResponse(
            {
                "error": (
                    "AI analysis can only be performed " "on a completed screening."
                )
            },
            status=400,
        )

    try:
        analysis = create_ai_analysis(screening)

    except ValidationError as error:
        return JsonResponse(
            {
                "error": error.message,
            },
            status=400,
        )

    except Exception as error:
        return JsonResponse(
            {
                "error": str(error),
            },
            status=500,
        )

    return JsonResponse(
        serialize_ai_analysis(analysis),
        status=201,
    )


@login_required
def analysis_detail(request, analysis_id):
    _require_ai_staff(request)

    from .models import AIAnalysis

    analysis = get_object_or_404(
        AIAnalysis.objects.select_related(
            "screening",
            "screening__patient__user",
        ),
        id=analysis_id,
    )

    return JsonResponse(serialize_ai_analysis(analysis))
