from django.contrib import admin

from apps.NotificationsApp.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "notification_type",
        "priority",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "priority",
        "is_read",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient__username",
        "patient__user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "read_at",
    )

    ordering = ("-created_at",)
