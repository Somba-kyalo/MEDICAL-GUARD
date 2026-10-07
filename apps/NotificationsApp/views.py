from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.NotificationsApp.models import Notification
from apps.NotificationsApp.serializers import NotificationSerializer
from apps.NotificationsApp.services import (
    delete_all_read_notifications,
    delete_notification,
    get_notification,
    get_read_notifications,
    get_unread_notifications,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
    mark_notification_as_unread,
)


def _serialize_notifications(queryset):
    return NotificationSerializer(
        queryset,
        many=True,
    ).data


@login_required
def list_page(request):
    notifications = get_user_notifications(request.user)

    return render(
        request,
        "NotificationsApp/list.html",
        {
            "notifications": notifications,
        },
    )


@login_required
def unread_page(request):
    notifications = get_unread_notifications(request.user)

    return render(
        request,
        "NotificationsApp/unread.html",
        {
            "notifications": notifications,
        },
    )


@login_required
def all_notifications(request):
    data = _serialize_notifications(get_user_notifications(request.user))

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "notifications": data,
        }
    )


@login_required
def unread_notifications(request):
    data = _serialize_notifications(get_unread_notifications(request.user))

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "notifications": data,
        }
    )


@login_required
def read_notifications(request):
    data = _serialize_notifications(get_read_notifications(request.user))

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "notifications": data,
        }
    )


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    return JsonResponse(
        {
            "success": True,
            "notification": NotificationSerializer(notification).data,
        }
    )


@login_required
@require_POST
def mark_read_view(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification = mark_notification_as_read(notification)

    return JsonResponse(
        {
            "success": True,
            "message": "Notification marked as read.",
            "notification": NotificationSerializer(notification).data,
        }
    )


@login_required
@require_POST
def mark_unread_view(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification = mark_notification_as_unread(notification)

    return JsonResponse(
        {
            "success": True,
            "message": "Notification marked as unread.",
            "notification": NotificationSerializer(notification).data,
        }
    )


@login_required
@require_POST
def mark_all_read_view(request):
    updated_count = mark_all_notifications_as_read(request.user)

    return JsonResponse(
        {
            "success": True,
            "message": "All notifications marked as read.",
            "updated_count": updated_count,
        }
    )


@login_required
@require_POST
def delete_notification_view(
    request,
    notification_id,
):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    delete_notification(notification)

    return JsonResponse(
        {
            "success": True,
            "message": "Notification deleted successfully.",
        }
    )


@login_required
@require_POST
def delete_read_notifications_view(request):
    deleted_count = delete_all_read_notifications(request.user)

    return JsonResponse(
        {
            "success": True,
            "message": "Read notifications deleted successfully.",
            "deleted_count": deleted_count,
        }
    )
