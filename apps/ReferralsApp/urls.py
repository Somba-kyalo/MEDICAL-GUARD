from django.urls import path
from . import views

app_name = "ReferralsApp"

urlpatterns = [
    path("create/", views.create_page, name="create"),
    path("list/", views.list_page, name="list"),
    path("detail/<int:referral_id>/", views.detail_page, name="detail"),
    path("tracking/", views.tracking_page, name="tracking"),
    path("api/create/", views.create_referral_view, name="api_create"),
    path("api/records/", views.all_referrals, name="api_records"),
    path("api/records/<int:referral_id>/", views.referral_detail, name="api_detail"),
    path(
        "api/records/<int:referral_id>/update/",
        views.update_referral_view,
        name="api_update",
    ),
    path(
        "api/records/<int:referral_id>/status/",
        views.update_referral_status_view,
        name="api_status",
    ),
    path(
        "api/patients/<int:patient_id>/records/",
        views.patient_referrals,
        name="api_patient_records",
    ),
]
