from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book-appointment'),
    path('', views.appointment_list, name='appointment-list'),
    path('<int:pk>/accept/', views.accept_appointment, name='accept-appointment'),
    path('<int:pk>/reject/', views.reject_appointment, name='reject-appointment'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel-appointment'),
]
