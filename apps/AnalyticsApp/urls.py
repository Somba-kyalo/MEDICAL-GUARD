from django.urls import path

from apps.AnalyticsApp import views

app_name = "AnalyticsApp"


urlpatterns = [
    path("", views.dashboard_page, name="dashboard"),
    path("dashboard/", views.dashboard_page, name="dashboard_page"),
    path("screening/", views.screening_page, name="screening"),
    path("amr/", views.amr_page, name="amr"),
    path("referrals/", views.referrals_page, name="referrals"),
    path("api/dashboard/", views.dashboard_api, name="api_dashboard"),
    path("api/screening/", views.screening_api, name="api_screening"),
    path("api/amr/", views.amr_api, name="api_amr"),
    path("api/referrals/", views.referrals_api, name="api_referrals"),
    path("api/facilities/", views.facilities_api, name="api_facilities"),
    path("api/follow-ups/", views.follow_ups_api, name="api_follow_ups"),
]
