from django.contrib import admin

from .models import AIAnalysis


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "screening",
        "risk_level",
        "status",
        "provider",
        "model_name",
        "confidence",
        "created_at",
    )

    list_filter = (
        "risk_level",
        "status",
        "provider",
    )

    search_fields = (
        "screening__patient__user__username",
        "screening__patient__user__first_name",
        "screening__patient__user__last_name",
        "summary",
        "recommended_action",
        "explanation",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)
