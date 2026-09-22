from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient

from .models import Screening, ScreeningAssessment, ScreeningResponse
from .services import (
    ScreeningServiceError,
    complete_screening,
    create_screening,
    review_screening,
    save_screening_response,
    submit_for_review,
)
from .validators import (
    validate_question,
    validate_question_code,
    validate_response,
    validate_response_type,
    validate_risk_level,
    validate_screening_type,
)

SCREENING_STAFF_ROLES = {
    User.Role.CLINICIAN,
    User.Role.FACILITY_STAFF,
    User.Role.ADMIN,
}


def _is_screening_staff(user):
    return user.is_authenticated and (
        user.is_superuser or user.role in SCREENING_STAFF_ROLES
    )


def _require_screening_staff(request):
    if not _is_screening_staff(request.user):
        raise PermissionDenied("You do not have permission to manage screenings.")


def _can_access_screening(user, screening):
    if _is_screening_staff(user):
        return True

    return user.role == User.Role.PATIENT and screening.patient.user_id == user.id


@login_required
def screening_list(request):
    if _is_screening_staff(request.user):
        screenings = Screening.objects.select_related(
            "patient__user",
            "created_by",
            "reviewed_by",
        ).order_by("-created_at")
    else:
        screenings = (
            Screening.objects.select_related(
                "patient__user",
                "created_by",
                "reviewed_by",
            )
            .filter(
                patient__user=request.user,
            )
            .order_by("-created_at")
        )

    return render(
        request,
        "ScreeningApp/history.html",
        {"screenings": screenings},
    )


@login_required
def screening_start(request):
    _require_screening_staff(request)

    patients = Patient.objects.select_related(
        "user",
    ).order_by(
        "user__last_name",
        "user__first_name",
        "user__username",
    )

    if request.method == "POST":
        patient_id = request.POST.get(
            "patient_id",
            "",
        ).strip()

        screening_type = request.POST.get(
            "screening_type",
            Screening.ScreeningType.GENERAL,
        )

        chief_complaint = request.POST.get(
            "chief_complaint",
            "",
        ).strip()

        try:
            validate_screening_type(screening_type)

            patient = get_object_or_404(
                Patient,
                id=patient_id,
            )

            screening = create_screening(
                patient=patient,
                created_by=request.user,
                screening_type=screening_type,
                chief_complaint=chief_complaint,
            )

            messages.success(
                request,
                "Screening started successfully.",
            )

            return redirect(
                "ScreeningApp:form",
                screening_id=screening.id,
            )

        except ValidationError as error:
            messages.error(
                request,
                error.message,
            )

    return render(
        request,
        "ScreeningApp/start.html",
        {
            "patients": patients,
            "screening_types": Screening.ScreeningType.choices,
        },
    )


@login_required
def screening_form(request, screening_id):
    _require_screening_staff(request)

    screening = get_object_or_404(
        Screening.objects.select_related(
            "patient__user",
            "created_by",
        ),
        id=screening_id,
    )

    if screening.status not in {
        Screening.Status.STARTED,
        Screening.Status.IN_PROGRESS,
    }:
        messages.error(
            request,
            "This screening is no longer accepting responses.",
        )

        return redirect(
            "ScreeningApp:detail",
            screening_id=screening.id,
        )

    if request.method == "POST":
        question_code = request.POST.get(
            "question_code",
            "",
        )

        question = request.POST.get(
            "question",
            "",
        )

        response = request.POST.get(
            "response",
            "",
        )

        response_type = request.POST.get(
            "response_type",
            ScreeningResponse.ResponseType.TEXT,
        )

        try:
            question_code = validate_question_code(
                question_code,
            )

            question = validate_question(
                question,
            )

            response_type = validate_response_type(
                response_type,
            )

            response = validate_response(
                response,
                response_type,
            )

            save_screening_response(
                screening=screening,
                question_code=question_code,
                question=question,
                response=response,
                response_type=response_type,
            )

            messages.success(
                request,
                "Screening response saved.",
            )

            return redirect(
                "ScreeningApp:form",
                screening_id=screening.id,
            )

        except ValidationError as error:
            messages.error(
                request,
                error.message,
            )

        except ScreeningServiceError as error:
            messages.error(
                request,
                str(error),
            )

    return render(
        request,
        "ScreeningApp/form.html",
        {
            "screening": screening,
            "responses": screening.responses.all(),
            "response_types": ScreeningResponse.ResponseType.choices,
        },
    )


@login_required
def screening_detail(request, screening_id):
    screening = get_object_or_404(
        Screening.objects.select_related(
            "patient__user",
            "created_by",
            "reviewed_by",
        ).prefetch_related(
            "responses",
        ),
        id=screening_id,
    )

    if not _can_access_screening(
        request.user,
        screening,
    ):
        raise PermissionDenied("You do not have permission to view this screening.")

    assessment = getattr(
        screening,
        "assessment",
        None,
    )

    return render(
        request,
        "ScreeningApp/result.html",
        {
            "screening": screening,
            "responses": screening.responses.all(),
            "assessment": assessment,
        },
    )


@login_required
@require_POST
def screening_complete(request, screening_id):
    _require_screening_staff(request)

    screening = get_object_or_404(
        Screening,
        id=screening_id,
    )

    try:
        complete_screening(screening)

        messages.success(
            request,
            "Screening completed successfully.",
        )

    except ScreeningServiceError as error:
        messages.error(
            request,
            str(error),
        )

    return redirect(
        "ScreeningApp:detail",
        screening_id=screening.id,
    )


@login_required
@require_POST
def screening_submit_for_review(request, screening_id):
    _require_screening_staff(request)

    screening = get_object_or_404(
        Screening,
        id=screening_id,
    )

    try:
        submit_for_review(screening)

        messages.success(
            request,
            "Screening submitted for review.",
        )

    except ScreeningServiceError as error:
        messages.error(
            request,
            str(error),
        )

    return redirect(
        "ScreeningApp:detail",
        screening_id=screening.id,
    )


@login_required
def screening_review(request, screening_id):
    _require_screening_staff(request)

    screening = get_object_or_404(
        Screening.objects.select_related(
            "patient__user",
            "created_by",
        ).prefetch_related(
            "responses",
        ),
        id=screening_id,
    )

    if screening.status != Screening.Status.UNDER_REVIEW:
        messages.error(
            request,
            "Only screenings under review can be reviewed.",
        )

        return redirect(
            "ScreeningApp:detail",
            screening_id=screening.id,
        )

    if request.method == "POST":
        summary = request.POST.get(
            "summary",
            "",
        ).strip()

        risk_level = request.POST.get(
            "risk_level",
            "",
        )

        recommended_action = request.POST.get(
            "recommended_action",
            "",
        ).strip()

        clinician_notes = request.POST.get(
            "clinician_notes",
            "",
        ).strip()

        try:
            risk_level = validate_risk_level(
                risk_level,
            )

            review_screening(
                screening=screening,
                reviewed_by=request.user,
                summary=summary,
                risk_level=risk_level,
                recommended_action=recommended_action,
                clinician_notes=clinician_notes,
            )

            messages.success(
                request,
                "Screening reviewed successfully.",
            )

            return redirect(
                "ScreeningApp:detail",
                screening_id=screening.id,
            )

        except ValidationError as error:
            messages.error(
                request,
                error.message,
            )

        except ScreeningServiceError as error:
            messages.error(
                request,
                str(error),
            )

    return render(
        request,
        "ScreeningApp/review.html",
        {
            "screening": screening,
            "risk_levels": ScreeningAssessment.RiskLevel.choices,
        },
    )
