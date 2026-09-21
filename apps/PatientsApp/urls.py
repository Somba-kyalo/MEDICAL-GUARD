from django.urls import path

from . import views


app_name = 'PatientsApp'


urlpatterns = [
    path('', views.patient_list, name='list'),
    path('create/', views.patient_create, name='create'),
    path('<int:patient_id>/', views.patient_detail, name='detail'),
    path('<int:patient_id>/edit/', views.patient_edit, name='edit'),
    path('<int:patient_id>/timeline/', views.patient_timeline, name='timeline'),
]