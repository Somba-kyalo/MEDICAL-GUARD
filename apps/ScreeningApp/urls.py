from django.urls import path

from . import views

app_name = "ScreeningApp"


urlpatterns = [
    path(
        "",
        views.screening_list,
        name="list",
    ),
    path(
        "start/",
        views.screening_start,
        name="start",
    ),
    path(
        "<int:screening_id>/",
        views.screening_detail,
        name="detail",
    ),
    path(
        "<int:screening_id>/form/",
        views.screening_form,
        name="form",
    ),
    path(
        "<int:screening_id>/complete/",
        views.screening_complete,
        name="complete",
    ),
    path(
        "<int:screening_id>/submit-review/",
        views.screening_submit_for_review,
        name="submit_review",
    ),
    path(
        "<int:screening_id>/review/",
        views.screening_review,
        name="review",
    ),
]
