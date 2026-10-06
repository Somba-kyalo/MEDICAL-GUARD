from django.urls import path
from . import views

app_name = "FacilitiesApp"

urlpatterns = [
    path("list/", views.list_page, name="list"),
    path("detail/<int:facility_id>/", views.detail_page, name="detail"),
    path("map/", views.map_page, name="map"),
    path("resources/", views.resources_page, name="resources"),
    path(
        "resources/<int:facility_id>/",
        views.resources_page,
        name="facility_resources_page",
    ),
    path("api/records/", views.all_facilities, name="api_records"),
    path("api/records/active/", views.active_facilities, name="api_active"),
    path("api/records/referral/", views.referral_facilities, name="api_referral"),
    path("api/records/<int:facility_id>/", views.facility_detail, name="api_detail"),
    path("api/create/", views.create_facility_view, name="api_create"),
    path(
        "api/records/<int:facility_id>/update/",
        views.update_facility_view,
        name="api_update",
    ),
    path(
        "api/records/<int:facility_id>/resources/",
        views.facility_resources,
        name="api_resources",
    ),
    path(
        "api/records/<int:facility_id>/resources/create/",
        views.create_resource_view,
        name="api_resource_create",
    ),
    path(
        "api/resources/<int:resource_id>/update/",
        views.update_resource_view,
        name="api_resource_update",
    ),
]
