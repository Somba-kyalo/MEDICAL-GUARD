from django.urls import path

from apps.FollowupsApp import views

app_name = "FollowupsApp"


urlpatterns = [
    # Pages
    path("list/", views.list_page, name="list"),
    path("create/", views.create_page, name="create"),
    path("detail/<int:follow_up_id>/", views.detail_page, name="detail"),
    # APIs
    path("api/records/", views.all_follow_ups, name="api_records"),
    path(
        "api/records/patient/<int:patient_id>/",
        views.patient_follow_ups,
        name="api_patient",
    ),
    path(
        "api/records/pending/",
        views.pending_follow_ups,
        name="api_pending",
    ),
    path(
        "api/records/missed/",
        views.missed_follow_ups,
        name="api_missed",
    ),
    path(
        "api/records/<int:follow_up_id>/",
        views.follow_up_detail,
        name="api_detail",
    ),
    path(
        "api/create/",
        views.create_follow_up_view,
        name="api_create",
    ),
    path(
        "api/records/<int:follow_up_id>/update/",
        views.update_follow_up_view,
        name="api_update",
    ),
    path(
        "api/records/<int:follow_up_id>/complete/",
        views.complete_follow_up_view,
        name="api_complete",
    ),
    path(
        "api/records/<int:follow_up_id>/reschedule/",
        views.reschedule_follow_up_view,
        name="api_reschedule",
    ),
]
