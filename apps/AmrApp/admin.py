from django.contrib import admin
from .models import AMRRecord, Antibiotic, Organism, ResistanceTest


@admin.register(AMRRecord)
class AMRRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "screening",
        "risk_level",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("risk_level", "status", "created_at")
    search_fields = (
        "patient__user__username",
        "clinical_notes",
        "exposure_history",
        "infection_information",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(Antibiotic)
class AntibioticAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "antibiotic_class", "is_active")
    list_filter = ("antibiotic_class", "is_active")
    search_fields = ("name", "code", "antibiotic_class")


@admin.register(ResistanceTest)
class ResistanceTestAdmin(admin.ModelAdmin):
    list_display = ("id", "amr_record", "organism", "antibiotic", "result", "tested_at")
    list_filter = ("result", "tested_at")
    search_fields = ("organism__name", "antibiotic__name")
    readonly_fields = ("created_at", "updated_at")
