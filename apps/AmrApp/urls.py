from django.urls import path
from . import views

app_name = "AmrApp"

urlpatterns = [
    path("screenings/<int:screening_id>/create/", views.create_amr, name="create"),
    path("records/<int:amr_record_id>/", views.amr_detail, name="detail"),
    path(
        "records/<int:amr_record_id>/resistance-tests/",
        views.add_resistance_test_view,
        name="add_resistance_test",
    ),
    path(
        "patients/<int:patient_id>/records/",
        views.patient_amr_records,
        name="patient_records",
    ),
]
