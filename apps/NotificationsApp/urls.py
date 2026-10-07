from django.urls import path
from apps.NotificationsApp import views

app_name = "NotificationsApp"

urlpatterns = [
    path("list/", views.list_page, name="list"),
    path("unread/", views.unread_page, name="unread"),
    path("api/records/", views.all_notifications, name="api_records"),
    path("api/records/unread/", views.unread_notifications, name="api_unread"),
    path("api/records/read/", views.read_notifications, name="api_read"),
    path(
        "api/records/<int:notification_id>/",
        views.notification_detail,
        name="api_detail",
    ),
    path(
        "api/records/<int:notification_id>/read/",
        views.mark_read_view,
        name="api_mark_read",
    ),
    path(
        "api/records/<int:notification_id>/unread/",
        views.mark_unread_view,
        name="api_mark_unread",
    ),
    path(
        "api/records/mark-all-read/", views.mark_all_read_view, name="api_mark_all_read"
    ),
    path(
        "api/records/<int:notification_id>/delete/",
        views.delete_notification_view,
        name="api_delete",
    ),
    path(
        "api/records/delete-read/",
        views.delete_read_notifications_view,
        name="api_delete_read",
    ),
]
