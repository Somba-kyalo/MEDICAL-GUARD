from django.contrib import admin

from apps.AuditApp.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "model_name",
        "object_id",
        "success",
        "created_at",
    )
    list_filter = (
        "action",
        "success",
        "created_at",
    )
    search_fields = (
        "user__username",
        "model_name",
        "object_id",
        "description",
        "ip_address",
    )
    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "description",
        "ip_address",
        "user_agent",
        "success",
        "created_at",
    )
    ordering = ("-created_at",)
    list_per_page = 50
