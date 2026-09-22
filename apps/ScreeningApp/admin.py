from django.contrib import admin

from .models import Screening, ScreeningAssessment, ScreeningResponse


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "screening_type",
        "status",
        "created_by",
        "reviewed_by",
        "started_at",
        "completed_at",
        "reviewed_at",
    )
    list_filter = (
        "screening_type",
        "status",
        "started_at",
    )
    search_fields = (
        "patient__user__username",
        "patient__user__email",
        "chief_complaint",
        "screening_notes",
    )
    readonly_fields = (
        "started_at",
        "created_at",
        "updated_at",
    )


@admin.register(ScreeningResponse)
class ScreeningResponseAdmin(admin.ModelAdmin):
    list_display = (
        "screening",
        "question_code",
        "response_type",
        "response",
        "created_at",
    )
    list_filter = (
        "response_type",
        "created_at",
    )
    search_fields = (
        "screening__patient__user__username",
        "question_code",
        "question",
        "response",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ScreeningAssessment)
class ScreeningAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "screening",
        "risk_level",
        "ai_assisted",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "risk_level",
        "ai_assisted",
        "created_at",
    )
    search_fields = (
        "screening__patient__user__username",
        "summary",
        "recommended_action",
        "clinician_notes",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
