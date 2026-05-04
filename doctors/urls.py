from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor-list'),
    path('<int:pk>/', views.doctor_detail, name='doctor-detail'),
    path('submit-verification/', views.submit_verification, name='submit-verification'),
    path('verification-status/', views.verification_status, name='verification-status'),
    path('<int:pk>/slots/', views.doctor_slots, name='doctor-slots'),
]
