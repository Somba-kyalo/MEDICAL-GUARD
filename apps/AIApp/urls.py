from django.urls import path
from apps.AIApp import views

app_name = "AIApp"

urlpatterns = [
    path(
        "screenings/<int:screening_id>/analyze/",
        views.analyze_screening,
        name="analyze",
    ),
    path("analyses/<int:analysis_id>/", views.analysis_detail, name="detail"),
]
