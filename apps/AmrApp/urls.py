from django.urls import path

from . import views

app_name = "AmrApp"

urlpatterns = [
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("assessment/", views.assessment_page, name="assessment"),
    path("result/", views.result_page, name="result"),
    path("surveillance/", views.surveillance_page, name="surveillance"),
    path("screenings/<int:screening_id>/create/", views.create_amr, name="create"),
    path("records/", views.all_amr_records, name="records"),
    path("records/<int:amr_record_id>/", views.amr_detail, name="detail"),
    path("records/<int:amr_record_id>/update/", views.update_amr, name="update"),
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
    path("organisms/", views.organisms, name="organisms"),
    path("antibiotics/", views.antibiotics, name="antibiotics"),
]
