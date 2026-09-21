from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'date_of_birth',
        'sex',
        'phone_number',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'sex',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'phone_number',
        'emergency_contact_name',
        'emergency_contact_phone',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )