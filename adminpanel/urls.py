from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='admin-stats'),
    path('patients/', views.patient_list, name='admin-patients'),
    path('patients/<int:pk>/', views.patient_detail, name='admin-patient-detail'),
    path('patients/<int:pk>/suspend/', views.suspend_patient, name='admin-suspend-patient'),
    path('doctors/pending/', views.pending_doctors, name='admin-pending-doctors'),
    path('doctors/<int:pk>/', views.doctor_admin_detail, name='admin-doctor-detail'),
    path('doctors/<int:pk>/approve/', views.approve_doctor, name='admin-approve-doctor'),
    path('doctors/<int:pk>/reject/', views.reject_doctor, name='admin-reject-doctor'),
    path('analytics/', views.analytics, name='admin-analytics'),
]
