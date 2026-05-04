from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('recommended/', views.recommended_products, name='recommended-products'),
]
