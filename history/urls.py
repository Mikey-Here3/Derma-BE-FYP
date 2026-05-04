from django.urls import path
from . import views

urlpatterns = [
    path('', views.history_list, name='history-list'),
    path('stats/', views.history_stats, name='history-stats'),
    path('progress/', views.progress_data, name='progress-data'),
]
