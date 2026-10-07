from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.AccountsApp.urls")),
    path("patients/", include("apps.PatientsApp.urls")),
    path("screening/", include("apps.ScreeningApp.urls")),
    path("ai/", include("apps.AIApp.urls")),
    path("amr/", include("apps.AmrApp.urls")),
    path("referrals/", include("apps.ReferralsApp.urls")),
    path("facilities/", include("apps.FacilitiesApp.urls")),
    path("followups/", include("apps.FollowupsApp.urls")),
    path("notifications/", include("apps.NotificationsApp.urls")),
    path("analytics/", include("apps.AnalyticsApp.urls")),
]
