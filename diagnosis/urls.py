from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze, name='analyze'),
    path('<int:pk>/', views.diagnosis_detail, name='diagnosis-detail'),
]
