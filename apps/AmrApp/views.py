from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.AccountsApp.models import User
from apps.PatientsApp.models import Patient
from apps.ScreeningApp.models import Screening

from .models import AMRRecord, Antibiotic, Organism
from .serializers import (
    AMRRecordSerializer,
    AntibioticSerializer,
    OrganismSerializer,
    ResistanceTestSerializer,
)
from .services import (
    add_resistance_test,
    create_amr_record,
    get_amr_record,
    get_patient_amr_records,
    update_amr_record,
)

AMR_STAFF_ROLES = {
    User.Role.CLINICIAN,
    User.Role.FACILITY_STAFF,
    User.Role.ADMIN,
}


def _is_amr_staff(user):
    return user.is_authenticated and (user.is_superuser or user.role in AMR_STAFF_ROLES)


def _require_amr_staff(request):
    if not _is_amr_staff(request.user):
        raise PermissionDenied("You do not have permission to use AMR services.")


@login_required
def dashboard_page(request):
    _require_amr_staff(request)
    return render(request, "AmrApp/dashboard.html")


@login_required
def assessment_page(request):
    _require_amr_staff(request)
    return render(request, "AmrApp/assessment.html")


@login_required
def result_page(request):
    _require_amr_staff(request)
    return render(request, "AmrApp/result.html")


@login_required
def surveillance_page(request):
    _require_amr_staff(request)
    return render(request, "AmrApp/surveillance.html")


@login_required
def create_amr(request, screening_id):
    _require_amr_staff(request)

    screening = get_object_or_404(
        Screening.objects.select_related("patient", "patient__user"),
        id=screening_id,
    )

    if screening.status != Screening.Status.COMPLETED:
        return JsonResponse(
            {"error": "An AMR record can only be created from a completed screening."},
            status=400,
        )

    try:
        amr_record = create_amr_record(
            patient=screening.patient,
            screening=screening,
            created_by=request.user,
        )
    except ValidationError as error:
        return JsonResponse({"error": error.message}, status=400)

    return JsonResponse(AMRRecordSerializer(amr_record).data, status=201)


@login_required
def amr_detail(request, amr_record_id):
    _require_amr_staff(request)

    amr_record = get_object_or_404(
        AMRRecord.objects.select_related(
            "patient__user",
            "screening",
            "ai_analysis",
            "created_by",
        ).prefetch_related(
            "resistance_tests__organism",
            "resistance_tests__antibiotic",
        ),
        id=amr_record_id,
    )

    return JsonResponse(AMRRecordSerializer(amr_record).data)


@login_required
def update_amr(request, amr_record_id):
    _require_amr_staff(request)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    amr_record = get_object_or_404(AMRRecord, id=amr_record_id)

    try:
        amr_record = update_amr_record(
            amr_record=amr_record,
            exposure_history=request.POST.get("exposure_history"),
            infection_information=request.POST.get("infection_information"),
            risk_level=request.POST.get("risk_level"),
            clinical_notes=request.POST.get("clinical_notes"),
            status=request.POST.get("status"),
        )
    except ValidationError as error:
        return JsonResponse({"error": error.message}, status=400)

    amr_record = get_amr_record(amr_record.id)

    return JsonResponse(AMRRecordSerializer(amr_record).data)


@login_required
def add_resistance_test_view(request, amr_record_id):
    _require_amr_staff(request)

    amr_record = get_object_or_404(AMRRecord, id=amr_record_id)

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405,
        )

    try:
        organism_id = request.POST.get("organism_id")
        antibiotic_id = request.POST.get("antibiotic_id")
        result = request.POST.get("result", "")
        test_notes = request.POST.get("test_notes", "")

        organism = get_object_or_404(Organism, id=organism_id)
        antibiotic = get_object_or_404(Antibiotic, id=antibiotic_id)

        resistance_test = add_resistance_test(
            amr_record=amr_record,
            organism=organism,
            antibiotic=antibiotic,
            result=result,
            test_notes=test_notes,
        )
    except ValidationError as error:
        return JsonResponse({"error": error.message}, status=400)

    return JsonResponse(
        ResistanceTestSerializer(resistance_test).data,
        status=201,
    )


@login_required
def patient_amr_records(request, patient_id):
    _require_amr_staff(request)

    patient = get_object_or_404(Patient, id=patient_id)
    records = get_patient_amr_records(patient)

    return JsonResponse(
        {
            "patient_id": patient.id,
            "records": AMRRecordSerializer(records, many=True).data,
        }
    )


@login_required
def all_amr_records(request):
    _require_amr_staff(request)

    records = (
        AMRRecord.objects.select_related(
            "patient__user",
            "screening",
            "ai_analysis",
            "created_by",
        )
        .prefetch_related(
            "resistance_tests__organism",
            "resistance_tests__antibiotic",
        )
        .order_by("-created_at")
    )

    return JsonResponse({"records": AMRRecordSerializer(records, many=True).data})


@login_required
def organisms(request):
    _require_amr_staff(request)

    queryset = Organism.objects.filter(is_active=True).order_by("name")

    return JsonResponse({"organisms": OrganismSerializer(queryset, many=True).data})


@login_required
def antibiotics(request):
    _require_amr_staff(request)

    queryset = Antibiotic.objects.filter(is_active=True).order_by("name")

    return JsonResponse({"antibiotics": AntibioticSerializer(queryset, many=True).data})
